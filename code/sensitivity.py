# SENSITIVITY TEST: Impact of Displacement with Enervation Tracking
import json
import os
import copy

try:
    from model import EconomySim
    print("Imported EconomySim from local repo.")
except ImportError:
    print("EconomySim already defined in environment (Colab mode).")

config_path = 'config.json'

if not os.path.exists(config_path):
    print(f"Error: {config_path} not found.")
else:
    with open(config_path, 'r') as f:
        data = json.load(f)
displacement_scenarios = [0.05, 0.08, 0.12, 0.15, 0.20]

for rate in displacement_scenarios:
    # 1. Setup Scenario Data
    test_data=copy.deepcopy(data)
    test_data['ai_impact']['annual_labor_displacement_rate'] = rate
    
    print("\n" + "="*70)
    print(f"SCENARIO: {rate:.0%} ANNUAL DISPLACEMENT RATE")
    print("="*70)
    
    # --- HEADER ---
    print(f"{'Month':<6} | {'Price':<8} | {'Unempl':<8} | {'Enervated':<10} | {'P-PCE ($B)':<11} | {'Ratio':<8} | {'Status'}")
    print("-" * 75)

   # 2. Run Simulation Instance
    test_sim = EconomySim(test_data)
    months_to_run = test_data['simulation_metadata'].get('steps_months', 120)


    for m in range(1, months_to_run + 1):
        result = test_sim.run_step(m)

        if not test_sim.history:
            continue

        stats = test_sim.history[-1]

        # 3. Print updates every 6 months or on collapse
        if m % 6 == 0 or result == "COLLAPSED":
            enervated_val = int(stats.get('enervated_total', 0))
            pce_billions = stats.get('pce_amount', 0) / 1e9
            gdp_ratio = stats.get('gdp_ratio', 0)
            
            # --- UPDATED ROW FORMAT ---
            print(f"{m:<6} | {stats['price_index']:<8} | {stats['unemployment_rate']:<8.2%} | {enervated_val:<10,} | ${pce_billions:>9.1f}B | {gdp_ratio:>7.1%} | {result}")
        
        if result == "COLLAPSED":
            print(f"\n>>> SYSTEM COLLAPSED IN MONTH {m} <<<")
            break