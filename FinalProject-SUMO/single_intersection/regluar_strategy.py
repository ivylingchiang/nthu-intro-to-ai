from sumo_rl.environment.env import SumoEnvironment
import traci
import numpy as np

def run_fixed_time_control(
    net_file="single-intersection.net.xml",
    route_file="single-intersection-vhvh.rou.xml",
    use_gui=True,
    num_seconds=1000,
    green_time=30,  # Fixed green time for each phase
    yellow_time=3
):
    # Initialize the SUMO environment
    env = SumoEnvironment(
        net_file=net_file,
        route_file=route_file,
        use_gui=use_gui,
        num_seconds=num_seconds,
        yellow_time=yellow_time,
        min_green=5
    )
    
    # Reset the environment
    env.reset()
    
    # Initialize traffic light program
    traci.trafficlight.setProgram('t', '0')  # Set to default program
    num_phases = len(traci.trafficlight.getAllProgramLogics('t')[0].phases)
    print(f"Number of phases in traffic light program: {num_phases}")
    
    phase_duration = 0  # Counter for the current phase duration
    current_phase = 0   # Current phase index
    
    # Metrics to track
    total_waiting_time = 0
    total_co2_emissions = 0
    total_vehicles_completed = 0
    initial_vehicles = set()
    
    # Main simulation loop
    for step in range(num_seconds):
        # Get current vehicles
        current_vehicles = set(traci.vehicle.getIDList())
        
        # Calculate completed trips
        if step == 0:
            initial_vehicles = current_vehicles
        else:
            completed = len(initial_vehicles - current_vehicles)
            total_vehicles_completed += completed
            initial_vehicles = current_vehicles
        
        # Calculate metrics for this step
        for vehicle_id in current_vehicles:
            total_waiting_time += traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            total_co2_emissions += traci.vehicle.getCO2Emission(vehicle_id)
        
        # Phase management
        phase_duration += 1
        
        # Get current phase type (assuming even indices are green phases and odd are yellow)
        is_yellow_phase = current_phase % 2 == 1
        phase_time = yellow_time if is_yellow_phase else green_time
        
        # Check if it's time to change phase
        if phase_duration >= phase_time:
            phase_duration = 0
            current_phase = (current_phase + 1) % num_phases
            traci.trafficlight.setPhase('t', current_phase)
        
        # Simulate one step
        env.step({})
    
    # Print final metrics
    print(f"\nSimulation completed. Metrics:")
    print(f"Total waiting time: {total_waiting_time:.2f} seconds")
    print(f"Total CO2 emissions: {total_co2_emissions/1000:.2f} grams")  # Convert from mg to g
    print(f"Total vehicles completed: {total_vehicles_completed}")
    
    env.close()
    return total_waiting_time, total_co2_emissions, total_vehicles_completed

if __name__ == "__main__":
    # Run the simulation
    run_fixed_time_control(
        use_gui=True,  # Set to True to see the visualization
        num_seconds=1000,
        green_time=30,  # 30 seconds of green time for each phase
        yellow_time=3
    )
