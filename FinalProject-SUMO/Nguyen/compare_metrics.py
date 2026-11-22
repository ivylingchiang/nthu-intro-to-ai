from sumo_rl.environment.env import SumoEnvironment
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from sb3_contrib import QRDQN
import numpy as np
from gymnasium import spaces, Env
import traci
import pandas as pd

class SumoMetricsWrapper(Env):
    def __init__(self, env):
        super().__init__()
        self.env = env
        example_obs = self.env.reset()
        
        # Get number of traffic lights
        self.num_traffic_lights = len(self.env.ts_ids)
        
        # Store the number of actions for each traffic light
        self.actions_per_traffic_light = {}
        total_combinations = 1
        for ts_id in self.env.ts_ids:
            num_actions = len(self.env.traffic_signals[ts_id].green_phases)
            self.actions_per_traffic_light[ts_id] = num_actions
            total_combinations *= num_actions
        
        # Calculate observation space size
        flat_obs = self._flatten_obs(example_obs)
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=flat_obs.shape, 
            dtype=np.float32
        )
        
        # Use Discrete action space with the total number of possible combinations
        self.action_space = spaces.Discrete(total_combinations)
        
        self.previous_vehicles = set()
        self.metrics = {
            'waiting_times': [],
            'co2_emissions': [],
            'queue_lengths': [],
            'completed_trips': [],
            'total_vehicles': [],
            'average_speed': []  # Added average speed metric
        }

    def _flatten_obs(self, obs):
        # Concatenate observations from all traffic lights
        all_obs = []
        for ts_id in self.env.ts_ids:
            all_obs.append(obs[ts_id])
        return np.concatenate(all_obs).astype(np.float32)

    def _decode_action(self, action):
        # Convert single action number to individual traffic light actions
        actions = {}
        remaining_action = action
        
        for ts_id in self.env.ts_ids:
            num_actions = self.actions_per_traffic_light[ts_id]
            # Extract action for this traffic light
            individual_action = remaining_action % num_actions
            actions[ts_id] = individual_action
            # Update remaining action for next traffic light
            remaining_action = remaining_action // num_actions
            
        return actions

    def _get_metrics(self):
        current_vehicles = set(traci.vehicle.getIDList())
        completed_trips = len(self.previous_vehicles - current_vehicles)
        
        waiting_time = 0
        queue_length = 0
        co2 = 0
        total_speed = 0
        
        for vehicle_id in current_vehicles:
            waiting_time += traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)
            total_speed += speed
            if speed < 0.1:
                queue_length += 1
            co2 += traci.vehicle.getCO2Emission(vehicle_id)
        
        # Calculate average speed (if there are vehicles)
        avg_speed = total_speed / len(current_vehicles) if current_vehicles else 0
        
        self.metrics['waiting_times'].append(waiting_time)
        self.metrics['co2_emissions'].append(co2)
        self.metrics['queue_lengths'].append(queue_length)
        self.metrics['completed_trips'].append(completed_trips)
        self.metrics['total_vehicles'].append(len(current_vehicles))
        self.metrics['average_speed'].append(avg_speed)
        
        self.previous_vehicles = current_vehicles
        return waiting_time, co2, queue_length, completed_trips, avg_speed

    def reset(self, **kwargs):
        obs = self.env.reset()
        self.previous_vehicles = set(traci.vehicle.getIDList())
        # Reset metrics
        for key in self.metrics:
            self.metrics[key] = []
        return self._flatten_obs(obs), {}

    def step(self, action):
        # Decode the single action number into individual traffic light actions
        dict_action = self._decode_action(action)
        
        obs, reward, done, info = self.env.step(dict_action)
        flat_obs = self._flatten_obs(obs)
        
        # Collect metrics
        self._get_metrics()
        
        if isinstance(done, dict):
            done_flag = any(done.values())
        else:
            done_flag = done
            
        return flat_obs, reward, done_flag, False, info

    def get_final_metrics(self):
        metrics_dict = {
            'Average Waiting Time': np.mean(self.metrics['waiting_times']),
            'Total CO2 Emissions (g)': sum(self.metrics['co2_emissions']) / 1000,  # Convert to grams
            'Average Queue Length': np.mean(self.metrics['queue_lengths']),
            'Total Completed Trips': sum(self.metrics['completed_trips']),
            'Average Vehicles in System': np.mean(self.metrics['total_vehicles']),
            'Average Speed (m/s)': np.mean(self.metrics['average_speed'])
        }
        return metrics_dict

def evaluate_model(model_path=None, use_fixed_timing=False, num_episodes=1):
    results = []
    
    for episode in range(num_episodes):
        env = SumoEnvironment(
            net_file="nguyentl.net.xml",  # Updated to use your network file
            route_file="nguyentesteod.rou.xml",  # Updated to use your route file
            use_gui=True,
            num_seconds=1000,
            yellow_time=3,
            min_green=5
        )
        
        wrapped_env = SumoMetricsWrapper(env)
        
        if use_fixed_timing:
            # Fixed timing strategy - adapted for multiple traffic lights
            phase_durations = {}
            current_phases = {}
            
            # Initialize phases for each traffic light
            for ts_id in env.ts_ids:
                current_phases[ts_id] = 0
                phase_durations[ts_id] = 0
            
            obs, _ = wrapped_env.reset()
            done = False
            
            while not done:
                actions = {}
                for ts_id in env.ts_ids:
                    num_phases = len(env.traffic_signals[ts_id].green_phases)
                    if phase_durations[ts_id] >= (30 if current_phases[ts_id] % 2 == 0 else 3):
                        current_phases[ts_id] = (current_phases[ts_id] + 1) % (num_phases * 2)
                        phase_durations[ts_id] = 0
                    actions[ts_id] = current_phases[ts_id] // 2
                    phase_durations[ts_id] += 1
                
                # Convert actions dict to single action number
                total_action = 0
                multiplier = 1
                for ts_id in env.ts_ids:
                    total_action += actions[ts_id] * multiplier
                    multiplier *= len(env.traffic_signals[ts_id].green_phases)
                
                obs, _, done, _, _ = wrapped_env.step(total_action)
        else:
            # RL model strategy
            model = QRDQN.load(model_path)
            obs, _ = wrapped_env.reset()
            done = False
            
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, _, done, _, _ = wrapped_env.step(action)
        
        results.append(wrapped_env.get_final_metrics())
    
    # Calculate average metrics across episodes
    avg_results = {}
    for key in results[0].keys():
        avg_results[key] = np.mean([r[key] for r in results])
    
    return avg_results

if __name__ == "__main__":
    # Evaluate RL model
    print("\nEvaluating RL Model...")
    rl_metrics = evaluate_model(model_path="rainbowDQN_sumo_model_ngu.zip", num_episodes=1)
    
    # Evaluate fixed timing
    print("\nEvaluating Fixed Timing Strategy...")
    fixed_metrics = evaluate_model(use_fixed_timing=True, num_episodes=1)
    
    # Create comparison table
    metrics_df = pd.DataFrame({
        'RL Model': rl_metrics,
        'Fixed Timing': fixed_metrics
    })
    
    print("\nComparison of Metrics:")
    print(metrics_df)
    
    # Define which metrics are better when lower
    lower_is_better = {
        'Average Waiting Time': True,
        'Total CO2 Emissions (g)': True,
        'Average Queue Length': True,
        'Total Completed Trips': False,
        'Average Vehicles in System': True,
        'Average Speed (m/s)': False
    }
    
    # Calculate percentage improvements
    improvements = pd.DataFrame({
        'Metric': metrics_df.index,
        'Improvement (%)': [
            ((fixed_metrics[m] - rl_metrics[m]) / fixed_metrics[m] * 100 if lower_is_better[m] else
             (rl_metrics[m] - fixed_metrics[m]) / fixed_metrics[m] * 100)
            for m in metrics_df.index
        ]
    })
    
    print("\nRL Model Improvements over Fixed Timing:")
    print(improvements) 