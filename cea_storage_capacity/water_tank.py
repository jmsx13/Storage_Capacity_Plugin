# coding=utf-8
from __future__ import division
from __future__ import print_function

import cea.config
import cea.inputlocator
import cea.plugin

import csv
import os.path
import cea_storage_capacity.Functions as fun

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"



def Size_WT_Capacity(Qww_demand, Qww_supply, people, temp_ext, cp, min_inlet, outlet, max_temp, loss_coef, step, tolerance):
    WaterTank, temp_tank,Qww_conventional, Qww_amb_loss = [], [], [], []
    Total_Bought, Capacities = [], []
    position = 1
    area = 0.0

    if people: Flag = True
    else: Flag = False

    Total_Bought.append(fun.add(Qww_demand))
    Capacities.append(0)

    TCapacity = step * people

    while Flag:
        for i in range(len(Qww_demand)):

            Qmin_supply = round(TCapacity * cp * outlet / 3600, 3)
            Qmax_stored = round(TCapacity * cp * max_temp / 3600, 3)

            try:
                if WaterTank[i-1] + Qww_supply[i] >= Qmin_supply:
                    if  WaterTank[i - 1] + Qww_supply[i] - float(Qww_demand[i]) - Qww_amb_loss[i - 1] > Qmax_stored:
                        WaterTank.append(round(Qmax_stored, 3))
                    else:
                        WaterTank.append(round(WaterTank[i - 1] + Qww_supply[i] - float(Qww_demand[i]) - Qww_amb_loss[i - 1], 3))
                else:
                    WaterTank.append(round(WaterTank[i - 1] + Qww_supply[i] - Qww_amb_loss[i - 1], 3))

                temp_tank.append(round(temp_tank[i-1] + (3600 * (WaterTank[i] - WaterTank[i-1]) / (TCapacity * cp)), 1))

                Qww_amb_loss.append(round(loss_coef * area * (temp_tank[i - 1] - float(temp_ext[i])) / 1000, 3))

            except Exception as e:
                if float(temp_ext[0]) > min_inlet:
                    WaterTank.append(round(TCapacity * cp * float(temp_ext[0]) / 3600, 3))
                    temp_tank.append(float(temp_ext[0]))
                else:
                    WaterTank.append(round(TCapacity * cp * min_inlet / 3600, 3))
                    temp_tank.append(min_inlet)

                Qww_amb_loss.append(0.0)


            if WaterTank[i] >= Qmin_supply:
                if WaterTank[i] + Qww_supply[i] >= float(Qww_demand[i]):
                    Qww_conventional.append(0.0)
                else:
                    Qww_conventional.append(
                        round(float(Qww_demand[i]) - (WaterTank[i] - Qmin_supply) - Qww_supply[i], 3))
            else:
                Qww_conventional.append(round(float(Qww_demand[i]), 3))


        Total_Bought.append(fun.add(Qww_conventional))
        Capacities.append(TCapacity)

        #print("TC1:", Capacities[position], "Bgt1:", Total_Bought[position], ", Area:", area)

        try:
            if Capacities[position] > 0 and Total_Bought[position-1] - fun.add(Qww_conventional) <= 0:
                Flag = False
            else:
                Slope = round((Capacities[position - 1] - Capacities[position]) / (Total_Bought[position - 1] - Total_Bought[position]) , 2)
                if Slope <= -tolerance:
                    area = 6 * ( TCapacity / 1000 ) ** (2 / 3)
                    Flag = False
                #print("TC1:", Capacities[position - 1], ", TC2:", Capacities[position], ", Bgt1:", Total_Bought[position-1], ", Bgt2:", Total_Bought[position], ", E:", Elasticity)
        except:
            Flag = True

        WaterTank.clear()
        temp_tank.clear()
        Qww_conventional.clear()
        Qww_amb_loss.clear()

        TCapacity += step * people
        position += 1

    return Capacities[len(Capacities) - 1], Total_Bought[len(Total_Bought) - 1], round(area,3)
    pass



def Calculate_SC_Performance(Qww_demand, Qww_supply, tank, area, cp, min_inlet, outlet, max_temp, temp_ext, loss_coef):
    WaterTank, Qww_usedTank, Qww_conventional, Qww_str_loss, Qww_amb_loss, temp_tank = [], [], [], [], [], []

    Qmin_supply = round(tank * cp * outlet / 3600, 3)
    Qmax_stored = round(tank * cp * max_temp / 3600, 3)

    for i in range(len(Qww_demand)):

        try:
            if WaterTank[i - 1] + Qww_supply[i] >= Qmin_supply:
                if WaterTank[i - 1] + Qww_supply[i] - float(Qww_demand[i]) - Qww_amb_loss[i - 1] > Qmax_stored:
                    WaterTank.append(round(Qmax_stored, 3))
                else:
                    WaterTank.append(round(WaterTank[i - 1] + Qww_supply[i] - float(Qww_demand[i]) - Qww_amb_loss[i - 1], 3))
            else:
                WaterTank.append(round(WaterTank[i - 1] + Qww_supply[i] - Qww_amb_loss[i - 1], 3))

            temp_tank.append(temp_tank[i - 1] + (3600 * (WaterTank[i] - WaterTank[i - 1]) / (tank * cp)))
            Qww_amb_loss.append(round(loss_coef * area * (temp_tank[i - 1] - float(temp_ext[i])) / 1000, 3))

        except:

            if float(temp_ext[i]) > min_inlet:
                WaterTank.append(round(tank * cp * float(temp_ext[0]) / 3600, 3))
                temp_tank.append(float(temp_ext[0]))
            else:
                WaterTank.append(round(tank * cp * min_inlet / 3600, 3))
                temp_tank.append(min_inlet)

            Qww_amb_loss.append(0.0)

        # Heat used from Tank, Conventional demand
        if WaterTank[i] >= Qmin_supply:
            if WaterTank[i] + Qww_supply[i] >= float(Qww_demand[i]):
                Qww_usedTank.append(round(float(Qww_demand[i]),3))
                Qww_conventional.append(0.0)
            else:
                Qww_usedTank.append(round(WaterTank[i],3))
                Qww_conventional.append(round(float(Qww_demand[i]) - (WaterTank[i] - Qmin_supply) - Qww_supply[i],3))
        else:
            Qww_usedTank.append(0.0)
            Qww_conventional.append(round(float(Qww_demand[i]),3))

        # Storage Losses
        if WaterTank[i-1] + Qww_supply[i] - float(Qww_demand[i]) - Qww_amb_loss[i-1] <= Qmax_stored:
            Qww_str_loss.append(0.0)
        else:
            Qww_str_loss.append(round(Qww_supply[i] - (Qmax_stored - WaterTank[i-1]),3))

    return WaterTank, Qww_usedTank, Qww_conventional, Qww_str_loss, Qww_amb_loss, temp_tank, Qmax_stored
    pass


def collector_performance(ww_demand_df, input_path, SC_type, cp, min_inlet, outlet, max_temp, U_value, step, slope):
    labels = ["Date",
              "Qww_sys_kWh",
              "Q_SC_gen_kWh",
              "T_ext_C",
              "Qww_stored_kWh",
              "T_tnk_C",
              "Qww_tank_kWh",
              "Qww_conv_kWh",
              "Qww_str_loss_kWh",
              "Qww_amb_loss_kWh"]
    result_df = ww_demand_df[["Name"]].copy()
    people_df = ww_demand_df[["people0"]].copy()
    building_production, building_demand, building_request, building_stored = [], [], [], []
    building_people, building_size, building_area, building_maxstr = [], [], [], []
    building_tank_str, building_ww_usd_tnk, building_ww_cnv_dem, building_ww_str_loss, building_ww_amb_loss = [], [], [], [], []
    count = 0

    if not os.path.exists(fun.get_path_sc(input_path, '', 'F')): os.makedirs(fun.get_path_sc(input_path, '', 'F'))

    for name in result_df['Name']:

        people = people_df['people0'][int(list(result_df['Name']).index(name))]
        ww_supply_kWh = []

        if SC_type == 'FP': tech = 4
        else: tech = 3

        with open(fun.get_path_sc(input_path, name, 1), 'w', newline='') as file_SC:
            writer = csv.writer(file_SC)

            with open(fun.get_path_sc(input_path, name, 2), 'r') as file_DM:
                date = [row['DATE'] for row in csv.DictReader(file_DM)]
            with open(fun.get_path_sc(input_path, name, 2), 'r') as file_DM:
                ww_demand_kWh = [row['Qww_sys_kWh'] for row in csv.DictReader(file_DM)]
            with open(fun.get_path_sc(input_path, name, 2), 'r') as file_DM:
                temp_ext_C = [row['T_ext_C'] for row in csv.DictReader(file_DM)]
            with open(fun.get_path_sc(input_path, name, tech), 'r') as file_SC_ET:
                supply_kWh = [row['Q_SC_gen_kWh'] for row in csv.DictReader(file_SC_ET)]

            for row in supply_kWh:
                ww_supply_kWh.append(float(row))

            size, Qww_conv, area = Size_WT_Capacity(ww_demand_kWh, ww_supply_kWh, people, temp_ext_C, cp, min_inlet, outlet, max_temp, U_value, step, slope)

            Qww_Tank, Qww_used_tank, Qww_conventional, Qww_str_loss, Qww_amb_loss, temp_tnk_C, Q_stored = Calculate_SC_Performance(ww_demand_kWh,
                                                                                                                                   ww_supply_kWh,
                                                                                                                                   size,
                                                                                                                                   area,
                                                                                                                                   cp,
                                                                                                                                   min_inlet,
                                                                                                                                   outlet,
                                                                                                                                   max_temp,
                                                                                                                                   temp_ext_C,
                                                                                                                                   U_value)

            Total_ww_stored = fun.Sum_Stored(Qww_Tank)

            writer.writerow(labels)
            linea = zip(date,
                        ww_demand_kWh,
                        ww_supply_kWh,
                        temp_ext_C,
                        Qww_Tank,
                        fun.Decimals(temp_tnk_C),
                        Qww_used_tank,
                        Qww_conventional,
                        Qww_str_loss,
                        Qww_amb_loss)

            for row in linea: writer.writerow(row)

        result_df['Name'][count] = name
        building_demand.append(round(fun.add(ww_demand_kWh),2))
        building_production.append(round(fun.add(ww_supply_kWh),2))
        building_people.append(round(people,0))
        building_size.append(round(size,0))
        building_area.append(round(area, 2))
        building_maxstr.append(round(Q_stored,2))
        if Total_ww_stored > 0: building_tank_str.append(round(Total_ww_stored,2))
        else: building_tank_str.append(0.0)
        building_ww_usd_tnk.append(round(fun.add(Qww_used_tank),2))
        building_ww_cnv_dem.append(round(fun.add(Qww_conventional),2))
        building_ww_str_loss.append(round(fun.add(Qww_str_loss),2))
        building_ww_amb_loss.append(round(fun.add(Qww_amb_loss), 2))
        count += 1

        date.clear()
        ww_demand_kWh.clear()
        supply_kWh.clear()
        ww_supply_kWh.clear()
        temp_ext_C.clear()

    result_df["Qww_sys_kWh"] = building_demand
    result_df["Q_SC_gen_kWh"] = building_production
    result_df["people0"] = building_people
    result_df["Tank_size_kg"] = building_size
    result_df["Tank_area_m2"] = building_area
    result_df["Qmax_str_kWh"] = building_maxstr
    result_df["Qww_tank_kWh"] = building_ww_usd_tnk
    result_df["Qww_conv_kWh"] = building_ww_cnv_dem
    result_df["Qww_str_loss_kWh"] = building_ww_str_loss
    result_df["Qww_amb_loss_kWh"] = building_ww_amb_loss

    return result_df


def main(config):

    locator2 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
    summary_swt = collector_performance(locator2.get_total_demand.read(),
                                        locator2.get_input_folder(),
                                        config.water_tank.collector_type,
                                        config.water_tank.heat_capacity,
                                        config.water_tank.minimum_inlet_temp,
                                        config.water_tank.supply_temperature,
                                        config.water_tank.maximum_temperature,
                                        config.water_tank.loss_coefficient,
                                        config.water_tank.incremental_step,
                                        config.water_tank.slope_curve)
    locator2.collector_performance.write(summary_swt)

    pass


if __name__ == '__main__':
    main(cea.config.Configuration())