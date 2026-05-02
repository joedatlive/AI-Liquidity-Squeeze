import json
import os
import random

class EconomySim:
    def __init__(self, config):
        self.c = config
        self.price_index = 1.0
        self.history = []
        self.is_collapsed = False

        # --- 1. POPULATION SEGMENTATION ---
        # Capital Owners: Small population, wealth capture, low MPC
        self.capital_owners = self.c['simulation_metadata']['total_workforce'] * 0.01
        
        # Cognitive Labor Pool (The Displaceable Group)
        self.cog_labor_total = sum(arch['count'] for arch in self.c['archetypes'].values())
        self.active_displaceable = self.cog_labor_total
        
        # Utility/Essential: Total Workforce - (Cognitive + Owners)
        self.utility_workers = self.c['simulation_metadata']['total_workforce'] - self.cog_labor_total - self.capital_owners

        # --- 2. DISPLACED SUB-COHORTS ---
        self.displaced_low_resilience = 0
        self.displaced_mid_resilience = 0
        self.displaced_high_resilience = 0
        self.enervated_total = 0

        # --- 3. BASELINE GDP CALCULATION ---
        # We calculate the starting consumption to serve as our 100% benchmark
        baseline_cons_owners = self.capital_owners * 12000 * 0.30
        baseline_cons_utility = self.utility_workers * 4000 * 0.85
        baseline_cons_active = self.active_displaceable * 5000 * 0.80
        
        # At start, nobody is displaced or enervated
        self.baseline_gdp = baseline_cons_owners + baseline_cons_utility + baseline_cons_active

        # a filter to account for monopoply effects of AI providers on price effeciencies
        self.price_pass_through = self.c['ai_impact'].get('price_pass_through_rate', 0.5)

        # a parameter to set a segment of price effeciency that AI doesn't improve, like land
        self.sticky_ratio = self.c['ai_impact'].get('sticky_price_ratio', 0.0)

    def run_step(self, month):
        # --- PHASE A: WORKFORCE IMPACT ---
        
        # 1. Displacement
        annual_rate = self.c['ai_impact']['annual_labor_displacement_rate']
        monthly_new_displaced = (self.active_displaceable * (annual_rate / 12))
        
        # Distribution: 52% Low, 29% Mid, 19% High
        self.active_displaceable -= monthly_new_displaced
        self.displaced_low_resilience += monthly_new_displaced * 0.52
        self.displaced_mid_resilience += monthly_new_displaced * 0.29
        self.displaced_high_resilience += monthly_new_displaced * 0.19

        # 2. Stabilization (Utility Re-hiring)
        absorption_ratio = self.c['stabilizers'].get('utility_labor_absorption_ratio', 0.12)
        monthly_rehire_rate = absorption_ratio / 12
        
        rehire_pool = (self.displaced_low_resilience + self.displaced_mid_resilience + self.displaced_high_resilience)
        if rehire_pool > 0:
            rehire_amt = rehire_pool * monthly_rehire_rate
            # Proportional recovery
            self.displaced_low_resilience -= rehire_amt * 0.52
            self.displaced_mid_resilience -= rehire_amt * 0.29
            self.displaced_high_resilience -= rehire_amt * 0.19
            if self.utility_workers < (self.c['simulation_metadata']['total_workforce'] * 0.50):
                self.utility_workers += rehire_amt
                

        # 3. Enervation (The Gaussian Drain)
        # Rates derived from empirically grounded SCF runway averages
        avg_low = sum(self.c['archetypes']['low_resilience']['runway_range']) / 2
        avg_mid = sum(self.c['archetypes']['mid_resilience']['runway_range']) / 2
        avg_high = sum(self.c['archetypes']['high_resilience']['runway_range']) / 2

        fail_low = self.displaced_low_resilience * (1 / avg_low)
        fail_mid = self.displaced_mid_resilience * (1 / avg_mid)
        fail_high = self.displaced_high_resilience * (1 / avg_high)

        self.displaced_low_resilience -= fail_low
        self.displaced_mid_resilience -= fail_mid
        self.displaced_high_resilience -= fail_high
        self.enervated_total += (fail_low + fail_mid + fail_high)

        # --- PHASE B: CONSUMPTION & MACRO ---
        
        # 4. Deflation (Parameterized)
        prod_gain = self.c['ai_impact']['ai_cost_reduction_multiplier']
        
        # We calculate how much "potential" price drop there is
        potential_deflation = prod_gain * 0.01 
        
        # We apply the 'Pass-Through' rate. 
        # Lower rate = Higher Monopoly capture.
        actual_deflation = potential_deflation * self.price_pass_through
        
        self.price_index *= (1 - actual_deflation)

        # 5. Consumption Math (The "Squeeze" Calculation)
        # MPCs applied to standardized monthly spends
        cons_owners = self.capital_owners * 12000 * 0.30
        cons_utility = self.utility_workers * 4000 * 0.85
        cons_active = self.active_displaceable * 5000 * 0.80
        
        total_displaced = (self.displaced_low_resilience + self.displaced_mid_resilience + self.displaced_high_resilience)
        cons_displaced = total_displaced * 2500 * 1.0 # Spending down savings

        # 6. Real Value Adjustment (Blended for Sticky Prices)
        nominal_cons = (cons_owners + cons_utility + cons_active + cons_displaced)
        
        # Calculate the blended index: 60% stays at 1.0 (sticky), 40% drops with AI
        blended_index = (self.price_index * (1 - self.sticky_ratio)) + (1.0 * self.sticky_ratio)
        
        # This is your final Participatory PCE adjusted for reality
        total_real_cons = nominal_cons / blended_index

        # 7. Break Check (The Systemic Snap)
        # We check two conditions: Social Fracture (Admin Crisis) and Economic Snap (Collapse)
        
        enervation_rate = self.enervated_total / self.c['simulation_metadata']['total_workforce']
        
        # Calculate the 'GDP Gap'
        # What percentage of our healthy baseline is the current real consumption?
        gdp_retention_ratio = total_real_cons / self.baseline_gdp
        
        status = "STABLE"
        
        # HYPOTHESIS TRIGGER: 
        # If real consumption falls below 80% of baseline, the system cannot 
        # sustain the infrastructure/debt of the original economy.
        if gdp_retention_ratio < 0.80:
            self.is_collapsed = True
            status = "COLLAPSED"
        # SOCIAL TRIGGER:
        # If 10% of people have $0, it is a political/administrative crisis.
        elif enervation_rate > 0.1:
            status = "ADMIN_CRISIS"

        # --- PHASE C: LOGGING ---
        self.history.append({
            "month": month,
            "price_index": round(self.price_index, 4),
            "unemployment_rate": round((self.cog_labor_total - self.active_displaceable) / self.c['simulation_metadata']['total_workforce'], 4),
            "enervated_total": int(self.enervated_total),
            "pce_amount": total_real_cons,      # The raw dollar value of personal consumption expendiitures for thos participating in the economy (not the enervated)
            "gdp_ratio": round(gdp_retention_ratio, 4), # Added for your own tracking
            "status": status
        })
        return status

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            data = json.load(f)
        sim = EconomySim(data)
        print(f"{'Month':<10} | {'Price Index':<12} | {'Unemployment':<12} | {'Enervated':<12} | {'P-PCE ($B)':<10} | {'PCE %':<8}| {'Status'}")
        for m in range(1, data['simulation_metadata']['steps_months'] + 1):
            res = sim.run_step(m)
            stats = sim.history[-1]
            pce_billions = stats['pce_amount'] / 1e9  # Convert to Billions
            if m % 6 == 0 or res == "COLLAPSED":
                print(f"{m:<10} | {stats['price_index']:<12} | {stats['unemployment_rate']:<12} | {stats['enervated_total']:<12} | ${pce_billions:>8.1f}B | {stats['gdp_ratio']:<8.2%}| {res}")
            if res == "COLLAPSED": break
