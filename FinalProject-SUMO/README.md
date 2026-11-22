# Carbon Emission Reduction with Dynamic Traffic Light Control

Team 11 final project for Introduction to Artificial Intelligence (NTHU, spring 2025), theme **AI for Sustainability**. Reinforcement learning (RL) agents control traffic lights in the [SUMO](https://eclipse.dev/sumo/) traffic simulator, and the team compares them with a fixed-timing signal.

The project has three steps:

1. **Single intersection:** train and compare five RL algorithms on one traffic light.
2. **Larger network:** control many traffic lights at once with one agent per light.
3. **Pedestrians:** add crosswalks and penalize making pedestrians wait.

The final presentation is in [`docs/AI_Presentation.pdf`](docs/AI_Presentation.pdf).

## Motivation

Most traffic lights run on fixed timers. Cars often wait at a red light while the cross street is empty, and idling cars emit CO2. If the light can see the traffic, it can give the green to the side that has cars. Less waiting should then mean less emission.

## Method

- **Simulator:** SUMO, controlled through the TraCI API and the [`sumo-rl`](https://github.com/LucasAlegre/sumo-rl) Gymnasium environment. SUMO also reports the metrics: waiting time, completed trips, queue length and CO2 emissions.
- **Observation:** the current phase (one-hot), a min-green flag, and the density and queue length of each incoming lane.
- **Action:** choose the next green phase. A phase change adds a 3-second yellow light. Every green lasts at least 5 seconds.
- **Algorithms:** Rainbow DQN (implemented as QR-DQN), PPO, A2C, ARS and TRPO, from Stable-Baselines3 and sb3-contrib.
- **Baseline:** a fixed-timing signal with 30 s green and 3 s yellow, on the same scenario.

### Choosing the reward

The team tried four rewards. Three of them taught the agent the wrong thing:

| Reward | Problem |
|---|---|
| Completed trips | Feedback comes long after the car passes the light, and the trip does not depend on this light alone. |
| Queue length | Under heavy traffic, one huge stalled queue scores better than two moving queues. |
| CO2 emissions | Idle cars emit little, so the agent learns to keep one side red and the other side always green. |
| **Average waiting time (negative)** | **Chosen.** The agent learns to clear the intersection, and less waiting means less emission once all trips finish. |

## Results

### 1. Single intersection

One traffic light, one vehicle type, 1,000 simulated seconds.

Slide 11 compares all five algorithms with fixed timing. All five beat fixed timing on every metric. PPO and A2C do best on every metric. Among the other three, TRPO has the longest waiting time and queue length, and Rainbow DQN has the highest CO2 emissions.

The tuning logs in [`TrainingData/`](TrainingData) give these runs, as percentage change compared with fixed timing:

| Model (run) | Avg. waiting time | Total CO2 | Avg. queue length | Completed trips |
|---|---|---|---|---|
| PPO (lr 7e-4, 300k steps) | −97.6% | −49.4% | −84.8% | +49.2% |
| A2C (lr 3e-4, 300k steps) | −97.3% | −47.1% | −83.0% | +48.2% |
| Rainbow DQN (QR-DQN) | −91.5% | −22.0% | −66.2% | +34.3% |

Raw numbers for the Rainbow DQN model in [`single_intersection/rainbowDQN_sumo_model.zip`](single_intersection):

| Metric | RL model (Rainbow DQN) | Fixed timing | Improvement |
|---|---|---|---|
| Average waiting time | 1,063.73 | 12,546.10 | +91.5% |
| Total CO2 emissions (g) | 20,675.76 | 26,521.42 | +22.0% |
| Average queue length | 22.16 | 65.56 | +66.2% |
| Total completed trips | 608.80 | 453.40 | +34.3% |
| Average vehicles in system | 52.99 | 78.96 | +32.9% |

Improvement is the change in the better direction: lower is better for waiting time, CO2, queue length and vehicles in system, and higher is better for completed trips.

Not every setting worked. Some ARS runs and one early PPO run had longer waiting times than fixed timing. The logs keep these runs too.

### 2. Larger network

To control many traffic lights at once, the team compared two designs:

- **Single model:** one model controls every light. It sees more information, but it is hard to train to convergence.
- **Multi-agent:** each light has its own model. Each model has a smaller search space and is easier to train. **The team used this design.**

The network is the Nguyen test network in [`Nguyen/`](Nguyen). The team ran Rainbow DQN against fixed timing on three test cases. The numbers below are read from the bar charts on slide 15, so they are approximate:

| Test case | Waiting time (s), fixed → RL | Completed trips, fixed → RL | Queue length, fixed → RL |
|---|---|---|---|
| 1 | ≈ 3,300 → 560 | ≈ 143 → 202 | ≈ 410 → 190 |
| 2 | ≈ 4,450 → 1,080 | ≈ 138 → 203 | ≈ 580 → 350 |
| 3 | ≈ 3,480 → 680 | ≈ 156 → 197 | ≈ 435 → 197 |

In every test case, waiting time drops by about 75–85% and completed trips rise. CO2 emissions stay almost the same as fixed timing, at about 120,000–128,000 in each case.

### 3. Adding pedestrians

The team added crosswalks to the intersection. Making pedestrians wait costs more in the reward, and changing the light takes longer. Rainbow DQN compared with fixed timing (slide 17, approximate values):

| Metric | Fixed timing | Rainbow DQN |
|---|---|---|
| Average vehicle waiting time | ≈ 10,600 | ≈ 5,500 |
| Average pedestrian waiting time | ≈ 4.9 | ≈ 0.2 |
| Average vehicle queue length | ≈ 60 | ≈ 27 |
| Total completed vehicle trips | ≈ 430 | ≈ 485 |
| Total completed pedestrian trips | ≈ 39 | ≈ 46 |
| Total CO2 emissions (g) | ≈ 30,500 | ≈ 23,000 |

The pedestrian scenario is only in the slides. Its code is not in this folder.

## Real-world idea: Guangfu Road

Students at NTHU wait a long time to cross Guangfu Road (光復路), especially at mealtimes and in strong sun. The team proposed:

1. Use dynamic signal control to give pedestrians a shorter wait during peak walking hours. This makes the green light for cars on Guangfu Road shorter.
2. To keep traffic moving, add digital signs that send cars to Gongdao 5th Road (公道五路) during those hours.

This part is a proposal. It was not simulated.

## Future work

- More complex traffic scenarios
- Priority for special vehicles, such as ambulances
- Predicting traffic flow under different road conditions
- Real-world use together with digital signs

## Folder structure

```
FinalProject-SUMO/
├── single_intersection/      # Single-intersection scenario
│   ├── single-intersection.net.xml        # SUMO network
│   ├── single-intersection-vhvh.rou.xml   # Traffic routes
│   ├── sumo_rl.ipynb                      # Training notebook (waiting-time reward)
│   ├── sumo_rl_carbon.ipynb               # Training notebook (CO2 reward)
│   ├── compare_metrics.py                 # RL model vs. fixed timing
│   ├── regluar_strategy.py                # Fixed-timing baseline only
│   ├── rainbowDQN_sumo_model.zip          # Trained Rainbow DQN (QR-DQN) model
│   ├── rainbowDQN_sumo_model_emmision_crap.zip  # Model trained on the CO2 reward (worse result)
│   └── ppo_sumo_model_emission.zip        # Trained PPO model
├── Nguyen/                   # Larger network (Nguyen), multi-agent
│   ├── nguyen.sumocfg, *.net.xml, *.rou.xml, ...  # Network, demand and route files
│   ├── sumo_rl_ngu.ipynb                  # Training notebook (QR-DQN)
│   ├── ngu.py                             # Training script (QR-DQN)
│   └── compare_metrics.py                 # RL model vs. fixed timing
├── TrainingModule/           # Training notebooks (PPO, A2C, ARS) and comparison scripts
├── TrainingData/             # Hyperparameter tuning logs (PDF) and A2C training curves (PNG)
├── docs/
│   ├── AI_Presentation.pdf                # Final presentation
│   ├── AI_Team11.pdf                      # Proposal paper (IEEE format)
│   └── prog24_proposal.pdf                # Proposal assignment spec
└── requirements.txt          # Python dependencies
```

## Setup

1. Install Python 3.9 or later.
2. Install SUMO:
   - macOS: `brew install sumo`
   - Linux: `sudo apt-get install sumo sumo-tools sumo-doc`
   - Windows: download it from the [SUMO website](https://sumo.dlr.de/docs/Downloads.php)
3. Set `SUMO_HOME`, for example `export SUMO_HOME=/usr/share/sumo` on Linux. Check the install with `sumo --version`.
4. Install the Python packages in a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

Compare the trained Rainbow DQN model with fixed timing on the single intersection:

```bash
cd single_intersection
python compare_metrics.py
```

The script runs one simulation with the RL model and one with fixed timing, opens the SUMO GUI, and prints each metric with the percentage change.

Notes:

- The scripts open network and model files by relative path, so run each script from its own folder.
- The scripts in `TrainingModule/` expect the network files and a trained model in the same folder. Copy `single-intersection.net.xml` and `single-intersection-vhvh.rou.xml` from `single_intersection/`, and train the model with the matching notebook first. The model files they name (for example `ppo_sumo_model_emission_v1_D.zip`) are not stored in this repository.
- `Nguyen/compare_metrics.py` loads `rainbowDQN_sumo_model_ngu.zip`, which is not stored in this repository. Train it with `Nguyen/sumo_rl_ngu.ipynb` first.
