from sumo_rl.environment.env import SumoEnvironment

sumo_env = SumoEnvironment(
        net_file="nguyentl.net.xml",
        route_file="nguyentesteod.rou.xml",
        use_gui=False,
        num_seconds=1000,
        yellow_time=3,
        min_green=5
    )

# traffic signal id
print(sumo_env.ts_ids)

### obs = [phase_one_hot, min_green, lane_1_density,...,lane_n_density, lane_1_queue,...,lane_n_queue]
### phase_one_hot is a one-hot encoded vector indicating the current active green phase
### min_green is a binary variable indicating whether min_green seconds have already passed in the current phase
### lane_i_density is the number of vehicles in incoming lane i dividided by the total capacity of the lane
### lane_i_queueis the number of queued (speed below 0.1 m/s) vehicles in incoming lane i divided by the total capacity of the lane

obs = sumo_env.reset()
print(obs) 

### The action space is discrete. Every 'delta_time' seconds, each traffic signal agent can choose the next green phase configuration.
### Important: every time a phase change occurs, the next phase is preeceded by a yellow phase lasting yellow_time seconds.

print(sumo_env.action_space)

import numpy as np
from gymnasium import spaces, Env
import traci

class SumoEmissionWrapper(Env):
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
        
        # Calculate total observation space size for all traffic lights
        single_ts_obs_size = len(next(iter(example_obs.values())))
        total_obs_size = single_ts_obs_size * self.num_traffic_lights
        
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(total_obs_size,), 
            dtype=np.float32
        )
        
        # Use Discrete action space with the total number of possible combinations
        self.action_space = spaces.Discrete(total_combinations)
        
        self.previous_waiting_time = 0
        self.previous_vehicles = set()

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

    def _get_emissions(self):
        vehicle_list = traci.vehicle.getIDList()
        total_co2 = 0.0
        for vehicle_id in vehicle_list:
            co2 = traci.vehicle.getCO2Emission(vehicle_id)
            total_co2 += co2
        return total_co2

    def _get_traffic_metrics(self):
        current_vehicles = set(traci.vehicle.getIDList())
        
        total_waiting_time = 0
       
        for vehicle_id in current_vehicles:
            waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            total_waiting_time += waiting_time
            
        self.previous_vehicles = current_vehicles
        return total_waiting_time

    def reset(self, **kwargs):
        obs = self.env.reset()
        self.previous_waiting_time = 0
        self.previous_vehicles = set(traci.vehicle.getIDList())
        return self._flatten_obs(obs), {}

    def step(self, action):
        # Decode the single action number into individual traffic light actions
        dict_action = self._decode_action(action)
        
        obs, reward, done, info = self.env.step(dict_action)
        flat_obs = self._flatten_obs(obs)

        # Calculate emissions and traffic metrics
        waiting_time = self._get_traffic_metrics()
        
        
        # Combined reward
        reward = -waiting_time

        if isinstance(done, dict):
            done_flag = any(done.values())
        else:
            done_flag = done

        return flat_obs, reward, done_flag, False, info

    def render(self):
        return self.env.render()

    def close(self):
        return self.env.close()


from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor

def make_env():
    wrapped_env = SumoEmissionWrapper(sumo_env)
    monitored_env = Monitor(wrapped_env)
    return monitored_env

env = DummyVecEnv([make_env])

from sb3_contrib import QRDQN

model = QRDQN(
    policy="MlpPolicy",
    env=env,
    learning_rate=1e-4,
    buffer_size=100000,
    learning_starts=2000,
    batch_size=64,
    tau=1.0,
    gamma=0.99,
    train_freq=1,
    gradient_steps=1,
    target_update_interval=100,
    exploration_fraction=0.2,
    exploration_final_eps=0.05,
    policy_kwargs=dict(
        net_arch=[256, 256, 128],
        n_quantiles=50
    ),
    verbose=1
)

model.learn(total_timesteps=200000)

model.save("rainbowDQN_sumo_model_ngu")

# model testing
test_env = DummyVecEnv([lambda: Monitor(make_env())])
obs = test_env.reset()
done = False
total_reward = 0

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, info = test_env.step(action)
    total_reward += reward[0]

print(f"Total reward (test): {total_reward}")

new_env = SumoEnvironment(
        net_file="nguyentl.net.xml",
        route_file="nguyentesteod.rou.xml",
    use_gui=True,  
    num_seconds=1000,
    yellow_time=3,
    min_green=5
)

wrapped_env = SumoEmissionWrapper(new_env)

obs, _ = wrapped_env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, _, info = wrapped_env.step(action)
    wrapped_env.render()  