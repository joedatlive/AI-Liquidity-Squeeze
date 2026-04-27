# SENSITIVITY TEST: Impact of Displacement Rate with Consistent Reporting
displacement_scenarios = [0.05, 0.08, 0.12, 0.15, 0.20]

for rate in displacement_scenarios:
    # 1. Setup specific scenario
    test_data = data.copy()
    test_data['ai_impact']['annual_labor_displacement_rate'] = rate
    
    print("\n" + "="*55)
    print(f"SCENARIO: {rate:.0%} ANNUAL DISPLACEMENT RATE")
    print("="*55)
    print(f"{'Month':<10} | {'Price Index':<12} | {'Unemployment':<12} | {'Status'}")
    print("-" * 55)

    # 2. Initialize and Run instance
    test_sim = EconomySim(test_data)
    months_to_run = test_data['simulation_params'].get('steps_months', 120)
    
    for m in range(1, months_to_run + 1):
        result = test_sim.run_step(m)
        stats = test_sim.history[-1]

        # Mirror the baseline reporting logic: every 6 months or on collapse
        if m % 6 == 0 or result == "COLLAPSED":
            print(f"{m:<10} | {stats['price_index']:<12} | {stats['unemployment_rate']:<12} | {result}")

        if result == "COLLAPSED":
            print(f"\n!!! SYSTEMIC INSOLVENCY REACHED AT {rate:.0%} DISPLACEMENT !!!")
            break