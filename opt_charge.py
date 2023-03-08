#!/usr/bin/env python3

# host = "192.168.0.90"                                   # Enter SolarEdge Modbus IP Address
# port = "1502"                                           # Enter SolarEdge Modbus TCP Port
solcast_api_key = "yTRovc0Ul0WKLIPXci5LcFATIC1LRg8y"	# Enter SolCast API key here 
solcast_resource_id_1 = "619d-b849-4418-5737"	        # Enter SolCast Resource 1 ID here
solcast_resource_id_2 = "125d-fa43-6fcf-666b"	        # Enter SolCast Resource 2 ID here
Max_Daily_Usage = 19.2342                               # Enter maximum daily electricity comsumption (kWh)
Reduction_to_Min = 0.2                                  # Enter reduction between Max Consumption & Min Consumption (% as a decimal)
Buffer = 2000                                           # Enter Battery Buffer (Watts)

solcast_url_1 = "https://api.solcast.com.au/rooftop_sites/" + solcast_resource_id_1 + "/forecasts?format=csv&api_key=" + solcast_api_key
solcast_url_2 = "https://api.solcast.com.au/rooftop_sites/" + solcast_resource_id_2 + "/forecasts?format=csv&api_key=" + solcast_api_key

print("Programme Initiated")

import argparse
import datetime
import json
import math
import pandas as pd
import requests
import solaredge_modbus
import time

today = pd.Period(datetime.datetime.now(), freq='D')
Day_of_Year = today.day_of_year
print("Today is Day", Day_of_Year, "of the year")
Day_Usage = Max_Daily_Usage*1000*(1-Reduction_to_Min*((1-math.cos(Day_of_Year/182*math.pi))/2))
print("Average Daily Usage =", "{:.0f}".format(Day_Usage), "Wh")

print("Iteration   Batt_Energy   Batt_Charge   Charge_Rate")
Has_Charged = 0

for iteration in range (16):
    # Get current Battery Energy level
    def get_values(inverter):
        values = {}
#       values = inverter.read_all()
        batteries = inverter.batteries()
        values["batteries"] = {}

        for battery, params in batteries.items():
            battery_values = params.read_all()
            values["batteries"][battery] = battery_values

        return values

    if __name__ == "__main__":
        argparser = argparse.ArgumentParser()
        argparser.add_argument("host", type=str, help="Modbus TCP address")
        argparser.add_argument("port", type=int, help="Modbus TCP port")
        argparser.add_argument("--timeout", type=int, default=1, help="Connection timeout")
        argparser.add_argument("--unit", type=int, default=1, help="Modbus device address")
        argparser.add_argument("--json", action="store_true", default=False, help="Output as JSON")
        args = argparser.parse_args()

        inverter = solaredge_modbus.Inverter(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            unit=args.unit
        )

        values = get_values(inverter)
        Battery_Energy = (values['batteries']['Battery1']['available_energy'])*(values['batteries']['Battery1']['soe'])/100
        # print(json.dumps(values, indent=4))
       
    # raise SystemExit(0)

    # Get current Solcast PV Forecast
    PV_data_1 = pd.read_csv(solcast_url_1)
    PV_data_2 = pd.read_csv(solcast_url_2)
    # print(data_1, data_2)
    # print("Row Timefrac   PV_1     PV-2     PV_Cum  Use_Cum    Delta     Bat_Charge")

    Battery_Charge = Battery_Energy
    PV_Cum = 0
    
    # Calculate number of Solcast rows to include until 00:30 tomorrow morning
    rows = int(48-math.trunc(iteration/2))
    # For the remaining period until 00:30 tomorrow morning, calculate maximum Battery Charge required over the course of the day
    for n in range(rows):
        Timefrac = (n+1)*30/24/60
        PV_Cum = PV_Cum+(PV_data_1.iat[n,0]+PV_data_2.iat[n,0])*1000/2
        Usage_Cum = Day_Usage*(-3.0405*Timefrac**5+7.26*Timefrac**4-6.9325*Timefrac**3+3.6981*Timefrac**2+0.0065*Timefrac+0.01)
        Delta = Usage_Cum+Buffer-Battery_Energy-PV_Cum
        Battery_Charge = min(max(Delta, Battery_Charge),values['batteries']['Battery1']['maximum_energy'])
        # print("{:2d}".format(n), "{:8.4f}".format(Timefrac), "{:8.4f}".format(PV_data_1.iat[n,0]), "{:8.4f}".format(PV_data_2.iat[n,0]),
        #       "{:8.0f}".format(PV_Cum), "{:8.0f}".format(Usage_Cum), "{:9.0f}".format(Delta), "{:8.0f}".format(Battery_Charge))
        
    Charge_Time = (16-iteration)/4                              # Number of Hours remaining to charge the battery
    Charge_Rate = min(1.1*Battery_Charge/Charge_Time,5000)      # Charge Rate in Watts.  10% added to allow for any inverter-forced reduction in charge rate as battery becomes full
    
    print("{:5d}".format(iteration),"{:14.0f}".format(Battery_Energy),"{:13.0f}".format(Battery_Charge),"{:13.0f}".format(Charge_Rate))

    # Not sure about the commands to the inverter yet, hence commented out
    # # If Charge_Rate > 0, set inverter to charge using the above charge rate
    # if Charge_Rate > 0:
    #     Has_Charged = 1
    #     mode = "Charge from solar power and grid"
    #     inverter.write("rc_cmd_mode", 4)
    #     inverter.write("maximum_charge_peak_power", Charge_Rate)

    # # Else, switch to either Max Self-Consumption or Dis/Charge Off
    # if Has_Charged == 1:
    #     mode = "Charge from solar power"
    #     inverter.write("rc_cmd_mode", 3)
    # else:
    #     mode = "Maximize self-consumption"
    #     inverter.write("rc_cmd_mode", 7)

    # Set internal loop variables back to zero
    Battery_Charge = 0

    time.sleep(30)

# When the programme ends, set inverter back to Max Self-Consumption
# mode = "Maximize self-consumption"
# inverter.write("rc_cmd_mode", 7)
