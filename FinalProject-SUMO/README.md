# Carbon Emission Reduction with Dynamic Traffic Light Control

Team 11 final project for Introduction to Artificial Intelligence (NTHU, spring 2025). Reinforcement learning (RL) agents control traffic lights in the [SUMO](https://eclipse.dev/sumo/) traffic simulator. The goal is to cut waiting time and CO2 emissions compared with a fixed-timing signal.

## Folder structure

```
FinalProject-SUMO/
├── single_intersection/      # Single-intersection scenario
│   ├── single-intersection.net.xml        # SUMO network
│   ├── single-intersection-vhvh.rou.xml   # Traffic routes
│   ├── sumo_rl.ipynb                      # Training notebook
│   ├── sumo_rl_carbon.ipynb               # Training notebook with a CO2-based reward
│   ├── compare_metrics.py                 # RL model vs. fixed timing
│   ├── regluar_strategy.py                # Fixed-timing baseline only
│   ├── rainbowDQN_sumo_model.zip          # Trained QR-DQN model (used by compare_metrics.py)
│   ├── rainbowDQN_sumo_model_emmision_crap.zip  # QR-DQN trained on the CO2 reward (worse result)
│   └── ppo_sumo_model_emission.zip        # Trained PPO model
├── Nguyen/                   # Multi-intersection Nguyen network
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

## Method

- **Environment:** SUMO, controlled through TraCI and the [`sumo-rl`](https://github.com/LucasAlegre/sumo-rl) Gymnasium environment.
- **Observation:** current phase (one-hot), a min-green flag, and the density and queue length of each incoming lane.
- **Action:** choose the next green phase. A phase change adds a 3-second yellow light. Every green lasts at least 5 seconds.
- **Reward:** negative average waiting time. The team also tried rewards based on completed trips, queue length and CO2. The CO2 reward taught the agent to block one direction, because idle cars emit little.
- **Algorithms:** QR-DQN, PPO, A2C and ARS from Stable-Baselines3 and sb3-contrib.
- **Baseline:** fixed-timing signal with 30 s green and 3 s yellow, on the same 1,000-second scenario.

## Results

Single intersection, RL agent compared with fixed timing:

| Model (run) | Avg. waiting time | Total CO2 | Avg. queue length | Completed trips |
|---|---|---|---|---|
| PPO (lr 7e-4, 300k steps) | −97.6% | −49.4% | −84.8% | +49.2% |
| A2C (lr 3e-4, 300k steps) | −97.3% | −47.1% | −83.0% | +48.2% |
| QR-DQN (`single_intersection/rainbowDQN_sumo_model.zip`) | −91.5% | −22.0% | −66.2% | +34.3% |

The PPO and A2C rows come from the tuning logs in [`TrainingData/`](TrainingData). Raw QR-DQN numbers:

| Metric | RL model (QR-DQN) | Fixed timing | Improvement |
|---|---|---|---|
| Average waiting time | 1,063.73 | 12,546.10 | +91.5% |
| Total CO2 emissions (g) | 20,675.76 | 26,521.42 | +22.0% |
| Average queue length | 22.16 | 65.56 | +66.2% |
| Total completed trips | 608.80 | 453.40 | +34.3% |
| Average vehicles in system | 52.99 | 78.96 | +32.9% |

Improvement is the percentage change in the better direction: lower is better for waiting time, CO2, queue length and vehicles in system, and higher is better for completed trips.

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

Compare the trained QR-DQN model with fixed timing on the single intersection:

```bash
cd single_intersection
python compare_metrics.py
```

The script runs one simulation with the RL model and one with fixed timing, opens the SUMO GUI, and prints each metric with the percentage change.

Notes:

- The scripts open network and model files by relative path, so run each script from its own folder.
- The scripts in `TrainingModule/` expect the network files and a trained model in the same folder. Copy `single-intersection.net.xml` and `single-intersection-vhvh.rou.xml` from `single_intersection/`, and train the model with the matching notebook first. The model files they name (for example `ppo_sumo_model_emission_v1_D.zip`) are not stored in this repository.
- `Nguyen/compare_metrics.py` loads `rainbowDQN_sumo_model_ngu.zip`, which is not stored in this repository. Train it with `Nguyen/sumo_rl_ngu.ipynb` first.
