
import csv
import os.path
import cea_storage_capacity.Functions as fun

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"

def hydrogen_production(ww_demand_df, input_path, efficiency, density, capacity, economy, vehicle_kmt, co2_emission, case):
    labels = ["Date",
              "E_available_kWh",
              "H2_produced_Kg",
              "O2_produced_Kg",
              "H2O_needed_Kg",
              "co2_avoided",
              "E_conv_loss_kWh",
              "H2_str_loss_kg",
              "H2_supply_kg",
              "D_travelled_Km",
              "Av_FCVs_sup_d",
              "CO2_avoided_kg"]
    result_df = ww_demand_df[["Name"]].copy()
    building_ava, building_h2_prod, building_o2_prod, building_h2o_need = [], [], [], []
    building_avn_fcv, building_max_str, building_co2_avd, building_cons = [], [], [], []
    building_con_loss, building_str_loss, building_h2_sup = [], [], []
    count = 0

    if not os.path.exists(fun.get_path_h2(input_path, '', 'F')): os.makedirs(fun.get_path_h2(input_path, '', 'F'))

    for name in result_df['Name']:
        with open(fun.get_path_h2(input_path, name, 1), 'w', newline='') as file_SC:
            writer = csv.writer(file_SC)

            with open(fun.get_path_h2(input_path, name, 2), 'r') as file_DM:
                date = [row['Date'] for row in csv.DictReader(file_DM)]

            if case:
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_DM:
                    kWh_available = [row['E_sld_GRID_kWh'] for row in csv.DictReader(file_DM)]
            else:
                with open(fun.get_path_h2(input_path, name, 2), 'r') as file_H2:
                    kWh_available = [row['E_PV_gen_kWh'] for row in csv.DictReader(file_H2)]

            h2_produced, o2_produced, h2o_needed, h2_con_losses = H2_production(kWh_available, density, efficiency)
            tank_performance, h2_str_losses, h2_supplied, max_stored = H2_supply_cap(date, h2_produced, capacity)
            dist_travelled, FCVs_supplied, co2_avoided = H2_supply_results(h2_supplied, economy, vehicle_kmt, co2_emission)

            writer.writerow(labels)
            linea = zip(date,
                        kWh_available,
                        h2_produced,
                        o2_produced,
                        h2o_needed,
                        tank_performance,
                        h2_con_losses,
                        h2_str_losses,
                        h2_supplied,
                        dist_travelled,
                        FCVs_supplied,
                        co2_avoided)
            for row in linea: writer.writerow(row)

        result_df['Name'][count] = name
        building_ava.append(fun.add(kWh_available))
        building_h2_prod.append(fun.add(h2_produced))
        building_o2_prod.append(fun.add(o2_produced))
        building_h2o_need.append(fun.add(h2o_needed))
        building_con_loss.append(fun.add(h2_con_losses))
        building_str_loss.append(fun.add(h2_str_losses))
        building_max_str.append(max_stored)
        building_h2_sup.append(fun.add(h2_supplied))
        building_cons.append(fun.add(dist_travelled))
        building_avn_fcv.append(round(fun.add(FCVs_supplied) / 365,1))
        building_co2_avd.append(round(fun.add(co2_avoided)/1000,3))
        count += 1

        date.clear()
        kWh_available.clear()

    result_df['E_available_kWh'] = building_ava
    result_df['H2_produced_kg'] = building_h2_prod
    result_df['O2_produced_kg'] = building_o2_prod
    result_df['H2O_required_kg'] = building_h2o_need
    result_df['E_con_losses_kWh'] = building_con_loss
    result_df['H2_str_losses_kg'] = building_str_loss
    result_df['Max_stored_kg'] = building_max_str
    result_df['D_travelled_km'] = building_cons
    result_df['Av_num_vehicles'] = building_avn_fcv
    result_df['CO2_avoided_Ton'] = building_co2_avd

    return result_df


def H2_supply_results(H2_supply, fuel_economy, vehicle_kmt, co2_emissions):
    km_travelled, fcvs_supplied, co2_avoided = [], [], []

    for i in range(len(H2_supply)):
        if H2_supply[i] > 0:
            km_travelled.append(round(H2_supply[i] * fuel_economy, 3))
            fcvs_supplied.append(round(H2_supply[i] * fuel_economy/vehicle_kmt,1))
            co2_avoided.append(round(H2_supply[i] * fuel_economy/co2_emissions,3))
        else:
            km_travelled.append(round(0.0, 3))
            fcvs_supplied.append(round(0.0, 1))
            co2_avoided.append(round(0.0, 3))

    return km_travelled, fcvs_supplied, co2_avoided


def H2_supply_cap(date, h2_produced, max_capacity):
    H2_tank_str, H2_str_loss, H2_supply = [], [], []
    max_stored = 0
    time = 23

    for i in range(len(h2_produced)):

        data = date[i].rsplit(' ', 1)
        tempo = data[1].split(':')

        ###  SIMULATING SUPPLY  ###
        try:
            if float(tempo[0]) == float(time):
                H2_tank_str.append(round(0.0, 3))
                H2_str_loss.append(round(0.0, 3))
                H2_supply.append(round(H2_tank_str[i-1], 3))
            else:
                if h2_produced[i] > 0:
                    if H2_tank_str[i - 1] + float(h2_produced[i]) > max_capacity:
                        H2_tank_str.append(round(max_capacity,3))
                        H2_str_loss.append(round(float(h2_produced[i]) - (max_capacity - H2_tank_str[i-1]),3))
                        H2_supply.append(round(0.0, 3))
                    else:
                        H2_tank_str.append(round(H2_tank_str[i-1] + float(h2_produced[i]), 3))
                        H2_str_loss.append(round(0.0, 3))
                        H2_supply.append(round(0.0, 3))
                else:
                    H2_tank_str.append(round(H2_tank_str[i - 1], 3))
                    H2_str_loss.append(round(0.0, 3))
                    H2_supply.append(round(0.0, 3))

        except:
            if h2_produced[i] > 0:
                if float(h2_produced[i]) < max_capacity:
                    H2_tank_str.append(round(h2_produced[i], 3))
                    H2_str_loss.append(round(0.0, 3))
                    H2_supply.append(round(0.0, 3))
                else:
                    H2_tank_str.append(round(max_capacity, 3))
                    H2_str_loss.append(round(h2_produced[i] - max_capacity, 3))
                    H2_supply.append(round(0.0, 3))
            else:
                H2_tank_str.append(round(0.0, 3))
                H2_str_loss.append(round(0.0, 3))
                H2_supply.append(round(0.0, 3))

        if H2_tank_str[i] > max_stored: max_stored = H2_tank_str[i]

        #print("i:", i, ": ", len(H2_supply), len(Tank_state), len(H2_str_loss), len(Km_travelled))

    return H2_tank_str, H2_str_loss, H2_supply, max_stored


def H2_production(E_available, density, efficiency):
    h2_produced,  o2_produced, h2o_needed, E_conv_loss = [], [], [], []

    for i in range(len(E_available)):
        if float(E_available[i]) > 0:
            h2_produced.append(round(float(E_available[i]) * 1 * efficiency / (density * 100), 3))
            o2_produced.append(round(float(E_available[i]) * 8 * efficiency / (density * 100), 3))
            h2o_needed.append(round(float(E_available[i]) * 9 * efficiency / (density * 100), 3))
            E_conv_loss.append(round(float(E_available[i]) * (1 - efficiency/100),3))
        else:
            h2_produced.append(round(0.0, 3))
            o2_produced.append(round(0.0, 3))
            h2o_needed.append(round(0.0, 3))
            E_conv_loss.append(round(0.0, 3))

    return h2_produced, o2_produced, h2o_needed, E_conv_loss
    pass
