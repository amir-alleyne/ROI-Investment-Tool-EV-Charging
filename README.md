# ROI Sales Tool - Rev A.8

## Overview
The **ROI Sales Tool** is a simulation model designed to analyze the return on investment (ROI) of an energy storage system (ESS) and electric vehicle (EV) charging infrastructure. The tool evaluates various factors such as energy costs, demand charges, vehicle increase rates, and grid vs. ESS charging performance to provide insights into cost savings and profitability over time.

## Features
- **Energy Storage System Simulation**: Models the behavior of an ESS for charging EVs.
- **Charging Strategy Analysis**: Evaluates charging from ESS vs. direct grid connections.
- **Cost and ROI Estimation**: Computes ROI, energy costs, and potential savings.
- **Demand Charge Calculation**: Analyzes cost variations based on peak demand rates.
- **Graphical Data Representation**: Generates plots for energy usage, costs, and revenue trends over time.
- **Customizable Parameters**: Allows users to define input variables such as charging prices, vehicle growth rates, and demand charge rates.

### Configurable Parameters
| Parameter | Description | Default Value |
|-----------|-------------|--------------|
| `years` | Number of years to simulate | 10 |
| `vehicle_increase_percentage` | Annual vehicle count increase | 2% |
| `vehicle_draw_increase` | Annual increase in vehicle energy draw | 1% |
| `energy_cost_increase` | Annual energy cost increase | 1.5% |
| `ev_charging_price_increase` | Annual EV charging price increase | 2% |
| `demand_charge_increase` | Annual increase in demand charge rate | 1.5% |
| `demand_charge_start` | Initial demand charge rate ($/kW) | 25 |
| `price_for_EV_charging` | Charging price per kWh | $0.45 |

## Output & Analysis
- **Energy Cost Breakdown**: Computes off-peak, mid-peak, and on-peak costs.
- **Charging Performance**: Tracks vehicles charged via ESS vs. grid.
- **ROI Calculation**: Estimates return on investment over time.
- **Visualization**:
  - Charging patterns by time of day.
  - Annual cost and revenue trends.
  - ROI progression over simulation years.

