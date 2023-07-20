# ROI Sales Tool - Rev A.8
# Authors: Omri Tayyara and Perry Yi
# Date: 6 - 30 - 2023

import matplotlib.pyplot as plt
import numpy as np

class Charger:
    def __init__(self, power, id, cost):
        self.power = power
        self.id = id
        self.cost = cost
        self.busy_until = 0

    def charge_vehicle(self, energy_required=45):
        return energy_required / self.power

class EnergyStorageSystem:
    def __init__(self, kwh_size, chargers, cost):
        self.kwh_size = kwh_size * 0.8
        self.chargers = chargers
        self.soc = self.kwh_size
        self.cost = cost
        self.grid_connection_power = None
        self.energy_drawn = {"off_peak": 0, "mid_peak": 0, "on_peak": 0}
        self.ess_charged_vehicles = 0
        self.grid_charged_vehicles = 0
        self.grid_energy_cost = 0

    def get_available_charger(self, current_time):
        return next((c for c in self.chargers if c.busy_until <= current_time), None)

    def recharge(self, current_time, target_soc):
        energy_needed = target_soc - self.soc
        while energy_needed > 0:
            potential_recharge = min(self.grid_connection_power, energy_needed)
            energy_needed -= potential_recharge
            current_time += 1
            self.soc += potential_recharge
            if 7 <= current_time < 11 or 17 <= current_time < 19:
                self.energy_drawn["mid_peak"] += potential_recharge
            elif 11 <= current_time < 17:
                self.energy_drawn["on_peak"] += potential_recharge
            else:
                self.energy_drawn["off_peak"] += potential_recharge
        return current_time

    def get_grid_price(self, current_time, off_peak_cost, mid_peak_cost, on_peak_cost):
        if 7 <= current_time < 11 or 17 <= current_time < 19:
            return mid_peak_cost
        elif 11 <= current_time < 17:
            return on_peak_cost
        else:
            return off_peak_cost

    def charge_vehicle(self, current_time, charger, off_peak_cost, mid_peak_cost, on_peak_cost):
        charging_time = charger.charge_vehicle()  # Calculate charging time
        charger.busy_until = current_time + charging_time  # Update the time until which the charger will be busy
        if self.soc >= 45:
            self.soc -= 45  # Reduce the SOC of the ESS
            self.ess_charged_vehicles += 1
        else:
            self.grid_energy_cost += 45 * self.get_grid_price(current_time, off_peak_cost, mid_peak_cost,
                                                               on_peak_cost)  # Add the cost of charging from the grid
            self.grid_charged_vehicles += 1
        return charger.busy_until, charging_time

def recharge_ess():
    #TODO: f
    pass

def simulate_ess(years, vehicle_increase_percentage, vehicle_draw_increase,
                 energy_cost_increase, ev_charging_price_increase, demand_charge_increase, demand_charge_start,
                 price_for_EV_charging):
    valid_sizes = [220, 440, 660]
    size_chargers_map = {220: 2, 440: 4, 660: 6}
    ess_costs = {220: 221400, 440: 395000, 660: 525000}
    charger_costs = {75: 24900, 150: 49800}

    # Calculate CAPEX (Capital Expenditure)
    installation_cost = 50000
    shipping_cost = 15000
    commissioning_cost = 7000
    inverter_cost_dict = {125: 24000, 250: 54500}
    # inverter_size = float(input("Enter Inverter Size: Options 125 kVA or 250 kVA "))
    inverter_size = 250
    inverter_cost = inverter_cost_dict[inverter_size]

    kwh_size = 220
    # kwh_size = None
    # while kwh_size not in valid_sizes:
        # kwh_size = int(input("Enter the ESS size (kWh) - options are 220, 440, 660: "))

    num_chargers = 2
    # num_chargers = 0
    # while num_chargers not in range(1, size_chargers_map[kwh_size] + 1):
    #     num_chargers = int(input(f"Enter the number of chargers (up to {size_chargers_map[kwh_size]} for {kwh_size} kWh): "))

    chargers = []
    total_cost = ess_costs[kwh_size]
    for i in range(num_chargers):
        power = None
        while power not in charger_costs:
            power = int(input("Enter charger power - options are 75, 150: "))
        chargers.append(Charger(power, i, charger_costs[power]))
        total_cost += charger_costs[power]

    def get_demand_charge_cost():
        return float(input("Enter the demand charge cost in $/kW: "))

    def get_price_of_EV_charging():
        return float(input("Enter the Price for EV Charging in $/kWh:"))

    # off_peak_cost = float(input("Enter the cost of energy during off-peak times in $/kWh: "))
    # mid_peak_cost = float(input("Enter the cost of energy during mid-peak times in $/kWh: "))
    # on_peak_cost = float(input("Enter the cost of energy during on-peak times in $/kWh: "))
    off_peak_cost = 0.07
    mid_peak_cost = .1
    on_peak_cost = .12

    # vehicle_count = int(input("Enter the number of vehicles: "))
    # grid_connection_power = int(input("Enter the grid connection power (kW): "))
    # gap_time = int(input("Enter the gap time (minutes): ")) / 60  # converted to hours
    vehicle_count = 30
    grid_connection_power = 50
    gap_time = 10

    ess = EnergyStorageSystem(kwh_size, chargers, total_cost)
    ess.grid_connection_power = grid_connection_power

    demand_charge_cost = demand_charge_start

    CAPEX = total_cost + shipping_cost + commissioning_cost + inverter_cost + installation_cost

    current_year = 1
    energy_cost_total = []
    d2g_demand_charge_total = []
    ess_demand_charge_total = []
    ev_charging_revenue_total = []
    total_charging_times = 0
    cash_flow_values = []
    annual_EV_charging_revenue_map = {}

    while current_year < years + 1:
        # MODIFIED, reset chargers busy times for each year
        for charger in ess.chargers:
            charger.busy_until = 0

        # MODIFIED, reset ess soc for each year
        ess.soc = kwh_size * 0.8
        soc = np.zeros(25)

        charging_times = np.zeros(24)
        current_time = 0
        vehicle_index = 0
        total_charging_time = 0
        total_ev_charging_energy = 0

        arrival_adjustment = vehicle_count % 2
        morning_times = np.random.normal(loc=8, scale=1, size=vehicle_count // 2)
        evening_times = np.random.normal(loc=18, scale=1, size=vehicle_count // 2 + arrival_adjustment)
        arrival_times = np.concatenate([morning_times, evening_times])
        arrival_times = (arrival_times + 24) % 24  # wrap around to 0-24 hours
        arrival_times.sort()

        while current_time <= 24 and total_charging_time < 24:
            # MODIFIED, in case arrived vehicles are all iterated but the current time is less than 24
            while vehicle_index < vehicle_count:
                # MODIFIED, for every arriving car, retrieve the list of available chargers using exact busy times
                available_chargers = [charger for charger in ess.chargers if
                                      charger.busy_until <= arrival_times[vehicle_index]]
                if arrival_times[vehicle_index] <= current_time:
                    # MODIFIED, no matter having available charger or not, increment vehicle index by 1
                    if available_chargers:
                        charger = available_chargers.pop()  # Get an available charger
                        charging_time = charger.charge_vehicle()  # Calculate charging time

                        # MODIFIED, time of finishing charging should not be over 24
                        if arrival_times[vehicle_index] + charging_time > 24:
                            # If charging this vehicle would make the total charging time exceed 24 hours, skip it.
                            break
                        if total_charging_time + charging_time > 24:
                            # If charging this vehicle would make the total charging time exceed 24 hours, skip it.
                            break

                        total_charging_time += charging_time
                        charger.busy_until = arrival_times[vehicle_index] + charging_time + gap_time  # Update the time until which the charger will be busy

                        if ess.soc >= 45:
                            ess.soc -= 45  # Decrease the SOC of the ESS
                            # MODIFIED, get energy drawn from grid to ess, assuming charging cars by ess always cost off-peak rate
                            ess.energy_drawn["off_peak"] += 45
                            ess.ess_charged_vehicles += 1
                        else:
                            # MODIFIED, get energy drawn directly from grid to vehicle
                            if 7 <= current_time < 11 or 17 <= current_time < 19:
                                ess.energy_drawn["mid_peak"] += 45
                            elif 11 <= current_time < 17:
                                ess.energy_drawn["on_peak"] += 45
                            else:
                                ess.energy_drawn["off_peak"] += 45
                            charging_time_from_grid = 45 / grid_connection_power
                            # MODIFIED, already done checking before
                            # if current_time + charging_time_from_grid + gap_time > 24:
                            #     break  # If charging this vehicle from the grid exceeds the available time, skip it.
                            ess.grid_energy_cost += 45 * ess.get_grid_price(current_time, off_peak_cost, mid_peak_cost,
                                                                            on_peak_cost)  # Add the cost of charging from the grid
                            charger.busy_until = current_time + charging_time_from_grid + gap_time  # Update the time until which the charger will be busy
                            ess.grid_charged_vehicles += 1

                        charging_times[int(np.round(current_time))] += 1  # increment the charging_times at the current hour
                    vehicle_index += 1  # Move to the next vehicle
                    current_time += 1
                else:
                    if num_chargers == len(available_chargers) and ess.soc < kwh_size * 0.8:
                        ess, time_to_charge, next_vehicle = recharge_ess(ess, chargers, current_time)
                        current_time += time_to_charge
                        vehicle_index += next_vehicle
            # POSSIBLY ADD GRADUAL CHARGING OF ESS AS TIME PASSES
            soc[int(current_time)] = ess.soc
        total_charging_times += np.sum(charging_times)

        off_peak_cost_total = ess.energy_drawn["off_peak"] * off_peak_cost
        mid_peak_cost_total = ess.energy_drawn["mid_peak"] * mid_peak_cost
        on_peak_cost_total = ess.energy_drawn["on_peak"] * on_peak_cost

        energy_cost = off_peak_cost_total + mid_peak_cost_total + on_peak_cost_total
        energy_cost_total.append(energy_cost)

        # MODIFIED, already computed the compounded rate for
        # d2g_demand_charge_cost, ess_demand_charge_cost, ev_charging_energy and ev_charging_revenue below
        d2g_demand_charge_cost = sum(charger.power for charger in ess.chargers) * demand_charge_cost * (1 + demand_charge_increase / 100) * current_year
        d2g_demand_charge_total.append(d2g_demand_charge_cost)
        ess_demand_charge_cost = ess.grid_connection_power * demand_charge_cost * (1 + demand_charge_increase / 100) * current_year
        ess_demand_charge_total.append(ess_demand_charge_cost)
        ev_charging_energy = np.sum(charging_times) * 45 * (1 + vehicle_draw_increase / 100) * (1 + vehicle_increase_percentage / 100)
        total_ev_charging_energy += ev_charging_energy
        ev_charging_revenue = total_ev_charging_energy * price_for_EV_charging * (1 + ev_charging_price_increase / 100)
        # ev_charging_revenue is computed using total_ev_charging_energy, which is cumulative
        ev_charging_revenue_total.append(ev_charging_revenue)

        # Update simulation parameters for the next year
        vehicle_count = int(vehicle_count * (1 + vehicle_increase_percentage / 100))
        off_peak_cost *= (1 + energy_cost_increase / 100)
        mid_peak_cost *= (1 + energy_cost_increase / 100)
        on_peak_cost *= (1 + energy_cost_increase / 100)
        ev_charging_price_increase *= (1 + ev_charging_price_increase / 100)
        demand_charge_increase *= (1 + demand_charge_increase / 100)
        demand_charge_cost *= (1 + (demand_charge_increase / 100))
        current_year += 1

        # MODIFIED, estimates the total number of cars charged for X years
        # daily car charged * 7 * 4 * 12 to be yearly number of cars charged, already increment for X years
        ess.ess_charged_vehicles = ess.ess_charged_vehicles * 7 * 4 * 12
        ess.grid_charged_vehicles = ess.grid_charged_vehicles * 7 * 4 * 12
        total_charging_times = total_charging_times * 7 * 4 * 12
        energy_cost_total = np.array(energy_cost_total)
        d2g_demand_charge_total = np.array(d2g_demand_charge_total)
        ess_demand_charge_total = np.array(ess_demand_charge_total)
        ev_charging_revenue_total = np.array(ev_charging_revenue_total)

        # MODIFIED: changed annual data calculation
        monthly_energy_cost = energy_cost_total * 7 * 4
        annual_energy_cost = monthly_energy_cost * 12
        monthly_d2g_cost = d2g_demand_charge_total
        monthly_ess_cost = ess_demand_charge_total
        annual_d2g_cost = monthly_d2g_cost * 12
        annual_ess_cost = monthly_ess_cost * 12
        monthly_EV_charging_revenue = np.cumsum(ev_charging_revenue_total) * 7 * 4
        annual_EV_charging_revenue = monthly_EV_charging_revenue * 12
        annual_EV_charging_revenue_map[year] = annual_EV_charging_revenue
    yearList = np.arange(0, years)

    # Compute ROI and Cash flow as a Function of time
    roi_values = []
    for year in range(years):
        annual_net_profit = annual_EV_charging_revenue[year] - (annual_energy_cost[year] + annual_ess_cost[year])
        ROI = (annual_net_profit / CAPEX) * 100
        roi_values.append(ROI)
        cash_flow = annual_net_profit - CAPEX
        cash_flow_values.append(cash_flow)

        # Add -CAPEX as the first element in cash_flow_values
        cash_flow_values = [-CAPEX] + cash_flow_values[:-1]

        # Calculate payback period
        cumulative_cash_flow = np.cumsum(cash_flow_values)
        payback_period = np.argmax(cumulative_cash_flow >= 0) + 1

 # Plot cumulative values
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.plot(yearList, annual_energy_cost, label="Energy Cost")
    plt.plot(yearList, annual_d2g_cost, label="Direct to Grid Demand Charge")
    plt.plot(yearList, annual_ess_cost, label="ESS Demand Charge")
    plt.xlabel("Years")
    plt.ylabel("Cumulative Cost ($)")
    plt.legend()

    plt.subplot(122)
    plt.plot(yearList, annual_EV_charging_revenue, label="EV Charging Revenue")
    plt.xlabel("Years")
    plt.ylabel("Cumulative Revenue ($)")
    plt.legend()

    # -------- Testing Graphs -----------
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.bar(range(24), charging_times)
    plt.xlabel("Hour of day")
    plt.ylabel("Number of cars charging")

    hours = np.arange(0, 25, 1)
    plt.subplot(122)
    plt.plot(hours, soc)
    plt.xlabel("Hour of day")
    plt.ylabel("State of Charge (kWh)")

    plt.figure(figsize=(12, 5))
    plt.plot(yearList, roi_values, label="ROI")
    plt.xlabel('Year')
    plt.ylabel('ROI (%)')
    plt.title('Return on Investment Over Time')
    plt.grid(False)
    plt.legend()

    # Plot cumulative cash flow with payback period
    plt.figure(figsize=(12, 5))
    plt.plot(yearList, np.cumsum(cash_flow_values), label="Cumulative Cash Flow")
    plt.axvline(payback_period, color='red', linestyle='--', label="Payback Period")
    plt.xlabel('Year')
    plt.ylabel('Cash Flow ($)')
    plt.title('Cumulative Cash Flow Over Time')
    plt.grid(False)
    plt.legend()
    # -------- Testing Graphs -----------

    print("Total number of vehicles charged for {0} years is: {1}, average daily cars charged is: {2:.1f}".format(years,int(total_charging_times), total_charging_times/years/12/4/7))
    print("Number of vehicles charged from the ESS for {0} years is: {1}, average daily cars charged is: {2:.1f}".format(years,ess.ess_charged_vehicles, ess.ess_charged_vehicles/years/12/4/7))
    print("Number of vehicles charged from the grid for {0} years is: {1}, average daily cars charged is: {2:.1f}".format(years,ess.grid_charged_vehicles, ess.grid_charged_vehicles/years/12/4/7))
    print("Cost of ESS and chargers: $", ess.cost)
    print("Energy cost (off peak) " + "for " + str(years) + " years: $ " + str(off_peak_cost_total * 7 * 4 * 12))
    print("Energy cost (mid peak) " + "for " + str(years) + " years: $ " + str(mid_peak_cost_total * 7 * 4 * 12))
    print("Energy cost (on peak) " + "for " + str(years) + " years: $ " + str(on_peak_cost_total * 7 * 4 * 12))
    print("The AVERAGE annual cost of energy drawn from the grid for {0} years is: $ {1:.2f}".format(years, annual_energy_cost[-1]/years))
    print("Total cost for 10 years: $ {0:.2f}".format(ess.cost + annual_energy_cost[-1]))
    print(f"The ROI after {years} years is {roi_values[-1]}%")

    plt.show()

simulate_ess(
    years=int(input("Enter the number of years to simulate: ")),
    vehicle_increase_percentage=float(input("Enter the vehicle increase percentage per year: ")),
    vehicle_draw_increase=float(input("Enter the vehicle draw increase per year: ")),
    energy_cost_increase=float(input("Enter the energy cost increase percentage per year: ")),
    ev_charging_price_increase=float(input("Enter the EV charging price increase percentage per year: ")),
    demand_charge_increase=float(input("Enter the demand charge increase percentage per year: ")),
    demand_charge_start=float(input("Enter the initial demand charge cost in $/kW: ")),
    price_for_EV_charging=float(input("Enter the price for EV charging in $/kWh: "))
)