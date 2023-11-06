
import csv
import os.path
import cea_storage_capacity.Functions as fun

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"

def collector_performance(ww_demand_df, input_path, potential, per_capita, heat_cap, inlet, outlet, max_temp, loss_coef):
    labels = ["Date",
              "Qww_sys_kWh",
              "Q_SC_gen_kWh",
              "T_ext_C",
              #"Qww_dm_kWh",
              #"Qww_av_kWh",
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
    type = 'FP'

    if not os.path.exists(fun.get_path_sc(input_path, '', 'F')): os.makedirs(fun.get_path_sc(input_path, '', 'F'))

    for name in result_df['Name']:

        inhabitants = people_df['people0'][int(list(result_df['Name']).index(name))]
        size = per_capita * inhabitants
        area = 6 * (size/1000)**(2/3)
        ww_supply_kWh = []

        if type == 'FP': tech = 4
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
                ww_supply_kWh.append(float(row) * float(potential)/100)

            #ww_available = [float(x) - float(y) for (x,y) in zip(ww_supply_kWh , ww_demand_kWh)]
            #ww_requested = [float(y) - float(x) for (x,y) in zip(ww_supply_kWh , ww_demand_kWh)]

            Qww_Tank, Qww_used_tank, Qww_conventional, Qww_str_loss, Qww_amb_loss, temp_tnk_C, Q_stored = Calculate_SC_Performance(ww_demand_kWh,
                                                                                                          ww_supply_kWh,
                                                                                                          size,
                                                                                                          area,
                                                                                                          heat_cap,
                                                                                                          inlet,
                                                                                                          outlet,
                                                                                                          max_temp,
                                                                                                          temp_ext_C,
                                                                                                          loss_coef)

            Total_ww_stored = fun.Sum_Stored(Qww_Tank)

            writer.writerow(labels)
            linea = zip(date,
                        ww_demand_kWh,
                        ww_supply_kWh,
                        temp_ext_C,
                        #fun.normalize_list(ww_requested),
                        #fun.normalize_list(ww_available),
                        Qww_Tank,
                        temp_tnk_C,
                        Qww_used_tank,
                        Qww_conventional,
                        Qww_str_loss,
                        Qww_amb_loss)

            for row in linea: writer.writerow(row)

        result_df['Name'][count] = name
        building_demand.append(round(fun.add(ww_demand_kWh),2))
        building_production.append(round(fun.add(ww_supply_kWh),2))
        building_people.append(round(inhabitants,2))
        #building_request.append(round(fun.add(fun.normalize_list(ww_requested)),2))
        #building_stored.append(round(fun.add(fun.normalize_list(ww_available)),2))
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
        #ww_available.clear()
        #ww_requested.clear()

    result_df["Qww_sys_kWh"] = building_demand
    result_df["Q_SC_gen_kWh"] = building_production
    result_df["people0"] = building_people
    result_df["Tank_size_kg"] = building_size
    result_df["Tank_area_kg"] = building_area
    result_df["Qmax_str_kWh"] = building_maxstr
    #result_df["Qww_dm_kWh"] = building_request
    #result_df["Qww_av_kWh"] = building_stored
    result_df["Qww_tank_kWh"] = building_ww_usd_tnk
    result_df["Qww_conv_kWh"] = building_ww_cnv_dem
    result_df["Qww_str_loss_kWh"] = building_ww_str_loss
    result_df["Qww_amb_loss_kWh"] = building_ww_amb_loss

    return result_df



def Calculate_SC_Performance(Qww_demand, Qww_supply, tank, area, capacity, inlet, outlet, max_temp, temp_ext, loss_coef):
    WaterTank, Qww_usedTank, Qww_conventional, Qww_str_loss, Qww_amb_loss, temp_tank = [], [], [], [], [], []
    Qmin_supply = round(capacity * tank * (outlet - float(temp_ext[0])) / 3600, 3)
    Qmax_stored = round(capacity * tank * (max_temp - float(temp_ext[0])) / 3600, 3)

    for i in range(len(Qww_demand)):
        if float(Qww_demand[i]) > 0:
            try:
                if float(Qww_supply[i]) > 0:
                    if float(Qww_supply[i]) + (float(WaterTank[i-1]) - Qmin_supply) > float(Qww_demand[i]):
                        if float(Qww_supply[i]) + float(WaterTank[i-1]) - float(Qww_demand[i]) - float(Qww_amb_loss[i - 1]) > Qmax_stored:
                            WaterTank.append(Qmax_stored)
                            Qww_usedTank.append(round(float(Qww_demand[i]),3))
                            Qww_conventional.append(0.0)
                            Qww_str_loss.append(round(float(WaterTank[i - 1]) + float(Qww_supply[i]) - float(Qww_demand[i])
                                          - Qmax_stored - float(Qww_amb_loss[i - 1]) , 3))
                            Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i - 1], temp_ext[i], area, loss_coef),3))
                            temp_tank.append(round(float(max_temp), 1))
                        else:
                            WaterTank.append(round(float(WaterTank[i - 1]) + float(Qww_supply[i]) - float(Qww_demand[i])
                                                         - Qww_amb_loss[i - 1], 3))
                            Qww_usedTank.append(round(float(Qww_demand[i]),3))
                            Qww_conventional.append(0.0)
                            Qww_str_loss.append(0.0)
                            Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i - 1], temp_ext[i], area, loss_coef),2))
                            temp_tank.append(round(temp_tank[i-1] + ((WaterTank[i] - WaterTank[i-1]) * 3600) /
                                                                                                (capacity*tank), 1))
                    else:
                        if float(Qww_supply[i]) + float(WaterTank[i-1]) > Qmin_supply:
                            WaterTank.append(round(Qmin_supply, 3))
                            Qww_usedTank.append(round(float(Qww_supply[i]) + float(WaterTank[i-1])  - Qmin_supply, 3))
                            Qww_conventional.append(round(float(Qww_demand[i]) - (float(Qww_supply[i]) +
                                                                        float(WaterTank[i-1]) - Qmin_supply), 3))
                            Qww_str_loss.append(0.0)
                            Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i - 1], temp_ext[i], area, loss_coef),2))
                            temp_tank.append(round(outlet, 2))
                        else:
                            WaterTank.append(round(float(WaterTank[i - 1]) + float(Qww_supply[i]) - float(Qww_amb_loss[i - 1]), 3))
                            Qww_usedTank.append(0.0)
                            Qww_conventional.append(float(Qww_demand[i]))
                            Qww_str_loss.append(0.0)
                            Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i - 1], temp_ext[i], area, loss_coef),2))
                            temp_tank.append(round(float(temp_tank[i - 1]) + (float(WaterTank[i]) -
                                                            float(WaterTank[i - 1])) * 3600 / (capacity * tank), 1))
                else:
                    if float(WaterTank[i-1]) - Qmin_supply > float(Qww_demand[i]):
                        WaterTank.append(round(WaterTank[i - 1] - float(Qww_demand[i]) - Qww_amb_loss[i - 1], 3))
                        Qww_usedTank.append(round(float(Qww_demand[i]), 3))
                        Qww_conventional.append(0.0)
                        Qww_str_loss.append(0.0)
                        Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i - 1], temp_ext[i], area, loss_coef),2))
                        temp_tank.append(round(float(temp_tank[i - 1]) + (float(WaterTank[i]) -
                                                            float(WaterTank[i - 1])) * 3600 / (capacity * tank), 1))
                    else:
                        if float(WaterTank[i - 1]) > Qmin_supply:
                            WaterTank.append(round(float(Qmin_supply), 3))
                            Qww_usedTank.append(round(float(WaterTank[i - 1]) - Qmin_supply, 3))
                            Qww_conventional.append(round(float(Qww_demand[i]) - (WaterTank[i-1] - Qmin_supply),3))
                            Qww_str_loss.append(0.0)
                            Qww_amb_loss.append(round(fun.ambient_Loss(WaterTank[i-1], temp_ext[i], area, loss_coef),2))
                            temp_tank.append(round(outlet, 1))
                        else:
                            WaterTank.append(round(WaterTank[i - 1] - float(Qww_amb_loss[i - 1]), 3))
                            Qww_usedTank.append(0.0)
                            Qww_conventional.append(float(Qww_demand[i]))
                            Qww_str_loss.append(0.0)
                            Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i-1], temp_ext[i], area, loss_coef),2))
                            temp_tank.append(round(
                                float(temp_tank[i-1]) + (float(WaterTank[i]) - float(WaterTank[i - 1])) * 3600 /
                                (capacity * tank), 1))

            except:
                if float(Qww_demand[i]) > float(Qww_supply[i]):
                    WaterTank.append(round(capacity * tank * (inlet - float(temp_ext[i])) / 3600, 3))
                    Qww_usedTank.append(0.0)
                    Qww_conventional.append(round(float(Qww_demand[i]), 3))
                    Qww_str_loss.append(0.0)
                    Qww_amb_loss.append(round(fun.ambient_Loss(inlet, temp_ext[i], area, loss_coef),2))
                    temp_tank.append(round(float(temp_ext[i]),1))
                else:
                    if (float(Qww_supply[i]) - float(Qww_demand[i])) > Qmax_stored:
                        WaterTank.append(Qmax_stored)
                        Qww_usedTank.append(0.0)
                        Qww_conventional.append(0.0)
                        Qww_str_loss.append(round(float(Qww_supply[i]) - float(Qww_demand[i]) - Qmax_stored, 3))
                        Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i-1], temp_ext[i], area, loss_coef), 3))
                        temp_tank.append(round(float(inlet), 1))
                    else:
                        WaterTank.append(round(float(Qww_supply[i]) - float(Qww_demand[i]), 3))
                        Qww_usedTank.append(0.0)
                        Qww_conventional.append(0.0)
                        Qww_str_loss.append(0.0)
                        Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i-1], temp_ext[i], area, loss_coef),2))
                        temp_tank.append(round(float(temp_tank[i-1]),1))
        else:
            try:
                if float(Qww_supply[i]) > 0:
                    if float(WaterTank[i - 1]) + float(Qww_supply[i]) - Qww_amb_loss[i - 1] > Qmax_stored > 0:
                        WaterTank.append(Qmax_stored)
                        Qww_usedTank.append(0.0)
                        Qww_conventional.append(0.0)
                        Qww_str_loss.append(round(float(WaterTank[i-1]) + float(Qww_supply[i]) - Qmax_stored -
                                                  float(Qww_amb_loss[i - 1]),3))
                        Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i - 1], temp_ext[i], area, loss_coef), 3))
                        temp_tank.append(round(max_temp,1))
                    else:
                        WaterTank.append(round(float(WaterTank[i - 1]),3))
                        Qww_usedTank.append(0.0)
                        Qww_conventional.append(0.0)
                        Qww_str_loss.append(round(float(Qww_supply[i]),3))
                        Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i-1], temp_ext[i], area, loss_coef), 3))
                        temp_tank.append(
                            round(float(temp_tank[i - 1]) + ((WaterTank[i] - WaterTank[i - 1]) * 3600) / (capacity * tank),
                                  1))
                else:
                    WaterTank.append(round(float(WaterTank[i - 1]) - Qww_amb_loss[i - 1],3))
                    Qww_usedTank.append(0.0)
                    Qww_conventional.append(0.0)
                    Qww_str_loss.append(0.0)
                    Qww_amb_loss.append(round(fun.ambient_Loss(temp_tank[i-1], temp_ext[i], area, loss_coef), 3))
                    temp_tank.append(
                        round(float(temp_tank[i - 1]) + ((WaterTank[i] - WaterTank[i - 1]) * 3600) / (capacity * tank),
                              1))
            except:
                WaterTank.append(0.0)
                Qww_usedTank.append(0.0)
                Qww_conventional.append(0.0)
                Qww_str_loss.append(0.0)
                Qww_amb_loss.append(0.0)
                temp_tank.append(round(float(temp_ext[i]),1))


    return WaterTank, Qww_usedTank, Qww_conventional, Qww_str_loss, Qww_amb_loss, temp_tank, Qmax_stored
    pass
