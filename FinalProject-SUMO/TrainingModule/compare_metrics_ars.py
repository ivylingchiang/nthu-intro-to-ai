from sumo_rl.environment.env import SumoEnvironment
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from sb3_contrib import QRDQN
from stable_baselines3 import A2C
from sb3_contrib import ARS
from stable_baselines3 import PPO
import numpy as np
from gymnasium import spaces, Env
import traci
import pandas as pd

class SumoMetricsWrapper(Env):
    def __init__(self, env):
        super().__init__()
        self.env = env
        example_obs = self.env.reset()
        flat_obs = self._flatten_obs(example_obs)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=flat_obs.shape, dtype=np.float32)
        self.action_space = env.action_space
        self.previous_vehicles = set()
        self.metrics = {
            'waiting_times': [],
            'co2_emissions': [],
            'queue_lengths': [],
            'completed_trips': [],
            'total_vehicles': []
        }

    def _flatten_obs(self, obs):
        return np.concatenate([np.array(v).flatten() for v in obs.values()]).astype(np.float32)

    def _get_metrics(self):
        current_vehicles = set(traci.vehicle.getIDList())
        completed_trips = len(self.previous_vehicles - current_vehicles)
        
        waiting_time = 0
        queue_length = 0
        co2 = 0
        
        for vehicle_id in current_vehicles:
            waiting_time += traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            if traci.vehicle.getSpeed(vehicle_id) < 0.1:
                queue_length += 1
            co2 += traci.vehicle.getCO2Emission(vehicle_id)
        
        self.metrics['waiting_times'].append(waiting_time)
        self.metrics['co2_emissions'].append(co2)
        self.metrics['queue_lengths'].append(queue_length)
        self.metrics['completed_trips'].append(completed_trips)
        self.metrics['total_vehicles'].append(len(current_vehicles))
        
        self.previous_vehicles = current_vehicles
        return waiting_time, co2, queue_length, completed_trips

    def reset(self, **kwargs):
        obs = self.env.reset()
        self.previous_vehicles = set(traci.vehicle.getIDList())
        # Reset metrics
        for key in self.metrics:
            self.metrics[key] = []
        return self._flatten_obs(obs), {}

    def step(self, action):
        ts_id = self.env.ts_ids[0]
        dict_action = {ts_id: int(action)}
        
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
            'Average Vehicles in System': np.mean(self.metrics['total_vehicles'])
        }
        return metrics_dict

def evaluate_model(model_path=None, use_fixed_timing=False, num_episodes=1):
    results = []
    
    for episode in range(num_episodes):
        env = SumoEnvironment(
            net_file="single-intersection.net.xml",
            route_file="single-intersection-vhvh.rou.xml",
            use_gui=True,
            num_seconds=1000,
            yellow_time=3,
            min_green=5
        )
        
        wrapped_env = SumoMetricsWrapper(env)
        
        if use_fixed_timing:
            # Fixed timing strategy
            current_phase = 0
            phase_duration = 0
            obs, _ = wrapped_env.reset()
            done = False
            
            while not done:
                if phase_duration >= (30 if current_phase % 2 == 0 else 3):  # 30s green, 3s yellow
                    current_phase = (current_phase + 1) % 8
                    phase_duration = 0
                action = current_phase // 2
                obs, _, done, _, _ = wrapped_env.step(action)
                phase_duration += 1
        else:
            # RL model strategy
            model = ARS.load(model_path)
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
    # rl_metrics = evaluate_model(model_path="rainbowDQN_sumo_model_emmision"
    rl_metrics = evaluate_model(model_path="ars_sumo_model_B1.zip", num_episodes=1)
    
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
        'Average Vehicles in System': True
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