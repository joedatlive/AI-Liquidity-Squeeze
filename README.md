# AI-Induced Liquidity Trap & Enervation Model (AILiquidity)

## Overview
This codebase provides a discrete-time simulation of a national economy undergoing rapid labor displacement due to Artificial Intelligence. Unlike standard models that assume labor is "reabsorbed" into new sectors, this model tracks **Economic Enervation**—the process where displaced workers exhaust private liquidity and permanently cease participation in the circular flow of the economy.

## Core Methodology & Phases
The simulation operates on a monthly step-count, processing the economy through three distinct lenses in each cycle:

1.  **Micro-Displacement:** AI agents replace cognitive labor based on a set annual displacement rate.
2.  **Macro-Flows:** Calculation of aggregate Personal Consumption Expenditures (PCE) based on the remaining active workforce and the current price index.
3.  **Status Evaluation:** A systemic health check based on the ratio of current consumption vs. the pre-AI baseline.

## Technical Assumptions & Parameters

### 1. Population Segmentation
The model assumes a total workforce of **160 Million**, segmented into:
* **Capital Owners (1%):** High-wealth individuals with a low Marginal Propensity to Consume (MPC). Spending is modeled as a fixed luxury baseline ($12,000/mo).
* **Utility/Essential Workers:** Non-displaceable manual labor or service roles.
* **Cognitive Labor (90M):** The "at-risk" population, divided into three archetypes:
    * **Low Resilience:** Minimal savings; 3-month survival window.
    * **Mid Resilience:** Moderate savings; 12-month survival window.
    * **High Resilience:** Significant savings; 36-month survival window.

### 2. The Absorption Factor (Stabilizers)
A critical variable in this model is the **Stabilizer Absorption Rate**. This represents the percentage of displaced workers who transition from "Low Resilience" to "Mid/High" tiers due to severance, private insurance, or government safety nets. 
* *Default configuration used in analysis:* 25%.

### 3. Economic Enervation (The "Drain")
The model treats unemployment not as a static state, but as a **decaying orbit**.
* Displaced workers continue to contribute to GDP/PCE until their specific resilience tier "drains."
* Once a tier reaches 0, individuals become **Enervated**. They are removed from the consumption pool entirely, representing a total loss of liquidity and economic participation.

### 4. Supply-Side Monopoly Friction
As AI reduces production costs, the model tracks a **Price Index**.
* **Friction = 0.0:** Companies pass 100% of AI savings to consumers (prices drop).
* **Friction > 0.0:** Companies retain savings as profit. High friction prevents the price floor from dropping, accelerating the liquidity trap as purchasing power fails to keep pace with displacement.

## Systemic Status Definitions

| Status | Threshold | Definition |
| :--- | :--- | :--- |
| **STABLE** | > 90% PCE | The economy is absorbing displacement via savings or price drops. |
| **ADMIN_CRISIS** | > 15M Enervated | Social infrastructure and safety nets are overwhelmed by the un-liquified population. |
| **LIQUIDITY_TRAP** | < 85% PCE | Aggregate demand falls faster than the price index can compensate. |
| **COLLAPSED** | < 80% PCE | Systemic failure; the circular flow of the economy is no longer sustainable. |

## Usage

To run the sensitivity analysis across various displacement rates (5% to 20%):

```bash
python sensitivity.py

# Interactive model
https://colab.research.google.com/drive/1d7Nw3-fBQgLxm-IkDWP1x9nof0XsYrJ5?usp=drive_link

# Related Research:
Research Specification describing this model: https://papers.ssrn.com/abstract=6650278

# Contact
Research Specification: The AI-Driven Liquidity Squeeze
Research Lead: Joseph J Donahue, joe@idam05.com
Technical Portfolio: idam05.com
Academic Profile: 
Google Scholar: https://scholar.google.com/citations?user=ZFA1PhgAAAAJ&hl=en
SSRN author page: https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=11025548
