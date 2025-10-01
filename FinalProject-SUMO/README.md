# Traffic Light Control using Reinforcement Learning

This project implements an intelligent traffic light control system using Quantile Regression DQN (QR-DQN) reinforcement learning algorithm. The system is tested and simulated using SUMO (Simulation of Urban MObility).

## Project Overview

The project aims to optimize traffic flow at a single intersection by using reinforcement learning to control traffic light timing. Our implementation shows significant improvements over traditional fixed-timing strategies across multiple metrics:

- 91.5% reduction in average waiting time
- 22.0% reduction in CO2 emissions
- 66.2% reduction in average queue length
- 34.3% increase in completed trips
- 32.9% reduction in average vehicles in system

## Prerequisites

1. Python 3.9 or higher
2. SUMO (Simulation of Urban MObility)
   - Windows: Download and install from [SUMO website](https://sumo.dlr.de/docs/Downloads.php)
   - Linux: `sudo apt-get install sumo sumo-tools sumo-doc`
   - macOS: `brew install sumo`
3. Git (for cloning the repository)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Crazy-Ting-Yao/Introduction_to_Artificial_Intelligence_Team11.git
   cd Introduction_to_Artificial_Intelligence_Team11
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install sumo-rl package from source (for latest version):
   ```bash
   git clone https://github.com/LucasAlegre/sumo-rl
   cd sumo-rl
   pip install -e .
   cd ..
   ```

5. Configure SUMO environment:
   ```bash
   # Windows
   set SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo
   # Linux/macOS
   export SUMO_HOME=/usr/share/sumo
   ```

## Project Structure

- `compare_metrics.py`: Main script for comparing RL model performance with fixed timing
- `rainbowDQN_sumo_model.zip`: Trained RL model
- `simulate-intersection/`: SUMO configuration files
  - `single-intersection.net.xml`: Network definition
  - `single-intersection-vhvh.rou.xml`: Traffic route definition
- `requirements.txt`: List of Python dependencies

## Usage

1. To compare the RL model with fixed timing strategy:
   ```bash
   python compare_metrics.py
   ```
   This will run two simulations:
   - One using the trained RL model
   - One using a fixed timing strategy (30s green, 3s yellow)

2. The script will display:
   - Comparison metrics between RL and fixed timing
   - Percentage improvements for each metric
   - Visual simulation in SUMO GUI

## Model Details

The reinforcement learning model:
- Architecture: Quantile Regression DQN (QR-DQN)
- State space: Traffic density and waiting time information
- Action space: Traffic light phases
- Reward function: Combination of:
  - Waiting time reduction
  - CO2 emission reduction
  - Queue length minimization
  - Trip completion rewards

## Results

The RL model significantly outperforms the fixed timing strategy:

| Metric | RL Model | Fixed Timing | Improvement |
|--------|----------|--------------|-------------|
| Average Waiting Time | 1,063.73 | 12,546.10 | +91.5% |
| Total CO2 Emissions (g) | 20,675.76 | 26,521.42 | +22.0% |
| Average Queue Length | 22.16 | 65.56 | +66.2% |
| Total Completed Trips | 608.80 | 453.40 | +34.3% |
| Average Vehicles in System | 52.99 | 78.96 | +32.9% |

## Troubleshooting

1. If you encounter SUMO-related errors:
   - Ensure SUMO_HOME environment variable is correctly set
   - Verify SUMO is properly installed and accessible from command line: `sumo --version`
   - Check if sumo-gui works: `sumo-gui`

2. If you get Python package conflicts:
   - Use a fresh virtual environment
   - Install packages in the order specified in requirements.txt
   - Ensure you have compatible Python version (3.9+)

## Contributing

This project is part of the Introduction to Artificial Intelligence course. Contributions from team members are welcome through pull requests.

## License


This project is for educational purposes. Please check individual dependencies for their respective licenses.
