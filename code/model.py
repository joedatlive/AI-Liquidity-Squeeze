import json
import os

class EconomySim:
    def __init__(self, config):
        # Load configuration into class variables
        self.c = config
        self.pop = config['macro_params']['initial_population']
        self.price_index = 1.0

        # Initial Agent Distribution
        self.displaced = 0
        self.utility_workers = self.pop * 0.05  # Assume 5% start in utilities
        self.active_workers = self.pop * 0.55   # Assume 55% start in other sectors
        self.capital_owners = self.pop * 0.01   # Top 1%

        self.history = [] # To track data for analysis
        self.is_collapsed = False

    def run_step(self, month):
        # 1. AI Impact: Prices drop at a lag (Cost-Push Deflation)
        prod_gain = self.c['ai_impact']['ai_cost_reduction_multiplier']
        stickiness = 0.75 # Hardcoded market friction
        self.price_index *= (1 - (prod_gain * 0.01 * stickiness))

        # 2. Displacement Logic (White Collar Job Loss)
        monthly_rate = self.c['ai_impact']['annual_labor_displacement_rate'] / 12
        new_displacement = self.active_workers * monthly_rate
        self.active_workers -= new_displacement

        # 3. Stabilizer Absorption (Hiring into Utilities)
        absorption_rate = self.c['stabilizers']['utility_labor_absorption_ratio']
        new_utility_jobs = new_displacement * absorption_rate

        self.utility_workers += new_utility_jobs
        self.displaced += (new_displacement - new_utility_jobs)

        # 4. Consumption Calculation (Purchasing Power)
        # Wages stay steady in nominal terms but are 'worth more' as prices drop
        base_wage = 5000

        cons_util = (self.utility_workers * base_wage) * self.c['consumption_logic']['mpc_utility_worker']
        cons_active = (self.active_workers * base_wage) * 0.75 # Standard MPC
        cons_displaced = (self.displaced * self.c['macro_params']['poverty_line_annual'] / 12) * self.c['consumption_logic']['mpc_displaced']

        total_cons = (cons_util + cons_active + cons_displaced) / self.price_index

        # 5. The Break Check (Insolvency)
        subsistence_floor = self.pop * (self.c['macro_params']['poverty_line_annual'] / 12)

        status = "STABLE"
        if total_cons < subsistence_floor:
            self.is_collapsed = True
            status = "COLLAPSED"

        # Record this month's data
        self.history.append({
            "month": month,
            "price_index": round(self.price_index, 4),
            "unemployment_rate": round(self.displaced / self.pop, 4),
            "total_consumption": round(total_cons, 2),
            "status": status
        })
        return status

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # Check if config exists
    if not os.path.exists('config.json'):
        print("Error: config.json not found in the current directory.")
    else:
        # Load the JSON file
        with open('config.json', 'r') as f:
            data = json.load(f)

        # DISPLAY CONFIG ---
        print("\n" + "="*40)
        print("RUN INITIALIZED WITH CONFIGURATION:")
        print(json.dumps(data, indent=4))
        print("="*40 + "\n")
        # -----------------------------------------

        # Initialize and Run
        sim = EconomySim(data)
        months_to_run = data['simulation_params']['steps_months'] if 'simulation_params' in data else 120

        print(f"{'Month':<10} | {'Price Index':<12} | {'Unemployment':<12} | {'Status'}")
        print("-" * 55)

        for m in range(1, months_to_run + 1):
            result = sim.run_step(m)
            stats = sim.history[-1]

            # Print update every 6 months for readability
            if m % 6 == 0 or result == "COLLAPSED":
                print(f"{m:<10} | {stats['price_index']:<12} | {stats['unemployment_rate']:<12} | {result}")

            if result == "COLLAPSED":
                print("\n!!! SYSTEMIC INSOLVENCY REACHED !!!")
                print(f"The economy failed at Month {m} because aggregate demand fell below subsistence levels.")
                break
