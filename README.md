# Introduction to Artificial Intelligence — NTHU

Coursework from the Introduction to Artificial Intelligence course at National Tsing Hua University (spring 2025): search algorithms, local search and genetic algorithms, a machine learning competition on Kaggle, and a team final project that trains reinforcement learning (RL) agents to control traffic lights in the SUMO traffic simulator.

## Final project: Carbon Emission Reduction with Dynamic Traffic Light Control

**Folder:** [`FinalProject-SUMO/`](FinalProject-SUMO) · **Team:** Team 11 (6 students) · **Theme:** AI for Sustainability

### Problem

Most traffic lights run on fixed timers. Cars wait at red lights even when the cross street is empty, and idling cars waste fuel and emit CO2. The team asked whether an RL agent that watches the traffic can switch lights better than a fixed timer, and so cut waiting time and emissions.

### Approach

- **Simulator:** [SUMO](https://eclipse.dev/sumo/) (Simulation of Urban MObility), controlled through the TraCI API and the [`sumo-rl`](https://github.com/LucasAlegre/sumo-rl) Gymnasium environment.
- **Observation:** current phase (one-hot), a min-green flag, and the density and queue length of each incoming lane.
- **Action:** choose the next green phase. Each phase change adds a 3-second yellow light, and every green lasts at least 5 seconds.
- **Reward design:** the team tested several rewards and explained why most of them failed. Completed trips gave delayed, unfair credit. Queue length favored one huge stalled queue. A pure CO2 reward taught the agent to block one side, because idle cars emit little. The final choice was **negative average waiting time**, because it clears the intersection and less waiting means less emission.
- **Algorithms:** A2C, PPO, ARS and QR-DQN from Stable-Baselines3 and sb3-contrib, each with hyperparameter tuning.
- **Baseline:** a fixed-timing signal (30 s green, 3 s yellow), run on the same 1,000-second single-intersection scenario.
- **Extensions (in the slides):** a larger multi-intersection network with one agent per light (multi-agent), crosswalks with a higher penalty for making pedestrians wait, and a proposal for Guangfu Road next to the NTHU campus.

### Results (single intersection, RL agent vs. fixed timing)

Percentage change compared with fixed timing. The PPO and A2C rows come from the tuning logs in [`TrainingData/`](FinalProject-SUMO/TrainingData), one evaluation episode each.

| Model (run) | Avg. waiting time | Total CO2 | Avg. queue length | Completed trips |
|---|---|---|---|---|
| PPO (lr 7e-4, 300k steps) | −97.6% | −49.4% | −84.8% | +49.2% |
| A2C (lr 3e-4, 300k steps) | −97.3% | −47.1% | −83.0% | +48.2% |
| QR-DQN | −91.5% | −22.0% | −66.2% | +34.3% |

Raw numbers for the QR-DQN model (`single_intersection/rainbowDQN_sumo_model.zip`) compared with fixed timing:

| Metric | RL model (QR-DQN) | Fixed timing | Improvement |
|---|---|---|---|
| Average waiting time | 1,063.73 | 12,546.10 | +91.5% |
| Total CO2 emissions (g) | 20,675.76 | 26,521.42 | +22.0% |
| Average queue length | 22.16 | 65.56 | +66.2% |
| Total completed trips | 608.80 | 453.40 | +34.3% |
| Average vehicles in system | 52.99 | 78.96 | +32.9% |

Not every setting worked. Some ARS runs and one early PPO run had *longer* waiting times than the fixed timer. The logs keep these runs too, so the effect of tuning is visible.

### Documents

- [Final presentation (slides)](FinalProject-SUMO/docs/AI_Presentation.pdf)
- [Team proposal (IEEE format)](FinalProject-SUMO/docs/AI_Team11.pdf)
- [Proposal assignment spec](FinalProject-SUMO/docs/prog24_proposal.pdf)
- [Project README with setup and usage](FinalProject-SUMO/README.md)

## Assignments

| Assignment | Problem | Algorithms | Link |
|---|---|---|---|
| Search in Pac-Man | Guide Pac-Man to a food dot, then through all four corners of a maze (UC Berkeley CS188 framework) | DFS, BFS, uniform-cost search, A* with a Manhattan-distance heuristic, and a custom corners heuristic (greedy nearest-corner tour) | [`Search in Pac-Man/`](Search%20in%20Pac-Man) |
| The n-Queen Problem | Place n queens with no attacks, for n = 8 and n = 50; compare run time and success rate over 30 runs | Iterative deepening search, hill climbing with random restarts, genetic algorithm (tournament selection, 1-point crossover, mutation). For n = 50, the GA solved 30/30 runs (about 4.3 s average), and hill climbing solved 0/30 | [`The n-Queen Problem/`](The%20n-Queen%20Problem) |
| Machine Learning | Imbalanced binary classification: 156,076 rows, 96 features, Kaggle class competition | LightGBM, XGBoost, HistGradientBoosting and Random Forest, with class weighting and RandomizedSearchCV tuning. LightGBM scored best on Kaggle (0.380, then 0.389 after tuning) | [`Machine Learning/`](Machine%20Learning) |
| Intelligent Agents | Written exercise: PEAS descriptions and environment types for a Mars rover and a smart traffic control system; rational agent design for a vacuum-cleaner world | Simple reflex agents, reflex agents with state, goal-based agents, learning agents | [`Intelligent Agents/`](Intelligent%20Agents) |

Each folder contains the assignment spec (`prog24_*.pdf` / `assign24_*.pdf`), the source code and the submitted report. The reports are written in Chinese.

## Tech stack

- **Language:** Python (scripts and Jupyter notebooks)
- **Reinforcement learning:** Stable-Baselines3 (PPO, A2C), sb3-contrib (ARS, QR-DQN), Gymnasium, sumo-rl
- **Simulation:** SUMO and TraCI
- **Machine learning:** scikit-learn, LightGBM, XGBoost, pandas, NumPy
- **Tools:** TensorBoard and matplotlib for training curves; Google Colab

## Repository structure

```
.
├── FinalProject-SUMO/         # Team final project: RL traffic-signal control in SUMO
│   ├── single_intersection/   # Single intersection: network, training notebooks, trained models, comparison script
│   ├── Nguyen/                # Multi-intersection Nguyen network and training
│   ├── TrainingModule/        # Training notebooks (PPO, A2C, ARS) and comparison scripts vs. fixed timing
│   ├── TrainingData/          # Hyperparameter tuning logs (PDF) and A2C training curves (PNG)
│   ├── docs/                  # Final presentation, proposal paper, assignment spec
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Setup, usage and results
├── Search in Pac-Man/         # search.py, searchAgents.py, report, starter code (search.zip)
├── The n-Queen Problem/       # IDS, hill climbing, GA — notebook and report
├── Machine Learning/          # Kaggle classification — notebook and report
└── Intelligent Agents/        # Written assignment (Chapter 2)
```
