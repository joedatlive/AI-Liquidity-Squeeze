# SENSITIVITY TEST: Impact of Displacement with Enervation Tracking
import json
import os
from model import EconomySim

config_path = 'config.json'

if not os.path.exists(config_path):
    print(f"Error: {config_path} not found.")
else:
    with open(config_path, 'r') as f:
        data = json.load(f)
displacement_scenarios = [0.05, 0.08, 0.12, 0.15, 0.20]

for rate in displacement_scenarios:
    # 1. Setup Scenario Data
    test_data = data.copy()
    test_data['ai_impact']['annual_labor_displacement_rate'] = rate
    
    print("\n" + "="*70)
    print(f"SCENARIO: {rate:.0%} ANNUAL DISPLACEMENT RATE")
    print("="*70)
    # Added Enervated column to the header
    print(f"{'Month':<10} | {'Price Index':<12} | {'Unemployment':<14} | {'Enervated':<12} | {'Status'}")
    print("-" * 70)

    # 2. Run Simulation Instance
    test_sim = EconomySim(test_data)
    months_to_run = test_data['simulation_params'].get('steps_months', 120)
    
    for m in range(1, months_to_run + 1):
        result = test_sim.run_step(m)
        stats = test_sim.history[-1]

        # 3. Print updates every 6 months or on collapse
        if m % 6 == 0 or result == "COLLAPSED":
            # Formatting enervated agents as an integer for readability
            enervated_display = f"{int(stats['enervated_agents']):,}" 
            print(f"{m:<10} | {stats['price_index']:<12} | {stats['unemployment_rate']:<14.4f} | {enervated_display:<12} | {result}")

        if result == "COLLAPSED":
            print(f"\n!!! SYSTEMIC INSOLVENCY REACHED AT {rate:.0%} DISPLACEMENT !!!")
            print(f"Final Count of Enervated Agents: {int(stats['enervated_agents']):,}")
            break