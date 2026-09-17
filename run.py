import argparse
import json
import os
import pandas as pd
from datetime import datetime
from model import CyberComplianceModel, SCENARIOS
import logging

logger = logging.getLogger("CyberComplianceModel")

def run_simulation(scenario="equifax_2017", steps=30, incident_step=10, seed=42, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    
    if scenario not in SCENARIOS:
        print(f"Error: Unknown scenario '{scenario}'. Available presets: {list(SCENARIOS.keys())}")
        return

    scenario_info = SCENARIOS[scenario]
    print(f"\n" + "="*70)
    print(f"--- RUNNING SCENARIO: {scenario.upper()} ---")
    print(f"Description: {scenario_info['description']}")
    print("="*70)

    config = {
        "scenario": scenario,
        "description": scenario_info["description"],
        "steps": steps,
        "incident_step": incident_step,
        "seed": seed,
        "timestamp": datetime.now().isoformat()
    }
    
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    logger.info("Saved simulation configuration to %s", config_path)

    # Initialize model
    model = CyberComplianceModel(
        scenario_name=scenario,
        incident_step=incident_step
    )

    # Display initial values for each stakeholder before running the simulation
    print("\n" + "="*50)
    print(f"--- INITIAL STAKEHOLDER VALUES (T = 0) [{scenario}] ---")
    print("="*50)
    initial_agent_data = []
    for agent in model.schedule.agents:
        initial_agent_data.append({
            "AgentID": agent.unique_id,
            "Type": agent.stakeholder_type,
            "SubType": agent.sub_type,
            "OperationalCapacity": agent.operational_capacity,
            "RegulatoryPressure": agent.regulatory_pressure,
            "ThreatLevel": agent.threat_level
        })
    df_initial = pd.DataFrame(initial_agent_data)
    print(df_initial.to_string(index=False))

    for i in range(steps):
        model.step()

    # Collect data
    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    model_csv_path = os.path.join(output_dir, "model_output.csv")
    agent_csv_path = os.path.join(output_dir, "agent_output.csv")

    model_data.to_csv(model_csv_path)
    agent_data.to_csv(agent_csv_path)

    logger.info("Simulation complete. Model output saved to %s", model_csv_path)
    logger.info("Agent output saved to %s", agent_csv_path)
    print(f"\nSimulation finished successfully!")
    print(f"Results stored in absolute path: {os.path.abspath(output_dir)}")
    
    # Print summary statistics split by Phase
    print("\n" + "="*50)
    print("--- MODEL SUMMARY STATISTICS BY PHASE ---")
    print("="*50)
    
    for phase_val in [1, 2]:
        phase_subset = model_data[model_data["Phase"] == phase_val]
        print(f"\n--- Phase {phase_val} (Steps: {len(phase_subset)}) ---")
        if not phase_subset.empty:
            print(phase_subset[["AvgThreat", "AvgOperationalCapacity", "AvgRegulatoryPressure", "ThreatGini"]].describe())
        else:
            print("No steps recorded in this phase.")
            
    print("\n" + "="*50)
    print("--- OVERALL MODEL SUMMARY STATISTICS ---")
    print("="*50)
    print(model_data[["AvgThreat", "AvgOperationalCapacity", "AvgRegulatoryPressure", "ThreatGini"]].describe())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cybersecurity Regulatory Compliance ABM simulation with preset incident scenarios.")
    parser.add_argument("--scenario", type=str, default="equifax_2017", choices=list(SCENARIOS.keys()), help="Preset incident scenario to simulate.")
    parser.add_argument("--steps", type=int, default=30, help="Total simulation steps.")
    parser.add_argument("--incident_step", type=int, default=10, help="Step at which the cybersecurity incident occurs.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--output", type=str, default="outputs", help="Directory to store simulation outputs.")

    args = parser.parse_args()
    
    run_simulation(
        scenario=args.scenario,
        steps=args.steps,
        incident_step=args.incident_step,
        seed=args.seed,
        output_dir=args.output
    )
