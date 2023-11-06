
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
              "E_demand_kWh",
              "E_available_kWh",
              "H2_produced_kg",
              "H2_stored_kg",
              "H2_demand_kg",
              "FC_supply_kWh",
              "E_bgt_fc_kWh",
              "E_sld_fc_kWh",
              "Elyzer_lss_kWh",
              "Cogen_lss_kWh"]
    result_df = ww_demand_df[["Name"]].copy()
    building_demand, building_available = [], []
    building_h2_production, building_h2_stored, building_h2_demand = [], [], []
    building_fc_supply, building_bgt_grid, building_sld_grid = [], [], []
    building_elz_loss, building_fc_loss = [], []
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
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_DM:
                    kWh_demand = [row['E_bgt_GRID_kWh'] for row in csv.DictReader(file_DM)]
            else:
                with open(fun.get_path_h2(input_path, name, 2), 'r') as file_H2:
                    kWh_available = [row['E_PV_gen_kWh'] for row in csv.DictReader(file_H2)]
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_DM:
                    kWh_demand = [row['GRID_kWh'] for row in csv.DictReader(file_DM)]

            h2_produced, elyzer_loss, h2_tank, h2_demand, fc_demand, fc_loss, \
            pb_fc_sold, pb_fc_bought = H2_Storage_Cogen(kWh_available,
                                                        density,
                                                        90,
                                                        8.6,
                                                        90,
                                                        kWh_demand,
                                                        capacity)

            writer.writerow(labels)
            linea = zip(date,
                        kWh_demand,
                        kWh_available,
                        h2_produced,
                        h2_tank,
                        h2_demand,
                        fc_demand,
                        pb_fc_bought,
                        pb_fc_sold,
                        elyzer_loss,
                        fc_loss)
            for row in linea: writer.writerow(row)

        result_df['Name'][count] = name
        building_demand.append(fun.add(kWh_demand))
        building_available.append(fun.add(kWh_available))
        building_h2_production.append(fun.add(h2_produced))
        building_h2_stored.append(fun.Sum_Stored(h2_tank))
        building_h2_demand.append(fun.add(h2_demand))
        building_fc_supply.append(fun.add(fc_demand))
        building_bgt_grid.append(fun.add(pb_fc_bought))
        building_sld_grid.append(fun.add(pb_fc_sold))
        building_elz_loss.append(fun.add(elyzer_loss))
        building_fc_loss.append(fun.add(fc_loss))
        count += 1

        date.clear()
        kWh_available.clear()

    result_df['E_demand_kWh'] = building_demand
    result_df['E_available_kWh'] = building_available
    result_df['H2_produced_kg'] = building_h2_production
    result_df['H2_stored_kg'] = building_h2_stored
    result_df['H2_demand_kg'] = building_h2_demand
    result_df['E_fc_supply_kWh'] = building_fc_supply
    result_df['E_bgt_grid_kWh'] = building_bgt_grid
    result_df['E_sld_grid_kWh'] = building_sld_grid
    result_df['E_elz_loss_kWh'] = building_elz_loss
    result_df['E_fc_loss_kWh'] = building_fc_loss

    return result_df

def H2_Storage_Cogen (available_kWh, density, Elyzer_eff, Compr_req, FC_eff, demand_kWh, max_capacity):
    H2_produced, H2_tank, H2_demand = [], [], []
    E_fc_demand, Elyzer_loss, E_fc_loss = [], [], []
    E_fc_sold, E_fc_bought = [], []

    for i in range(len(available_kWh)):

        ### CALCULATE HYDROGEN PRODUCTION TO TANK
        try:
            if H2_tank[i - 1] < max_capacity:
                Elyzer_loss.append(round(float(available_kWh[i]) * (1 - Elyzer_eff / 100), 3))
                H2_produced.append(round(float(available_kWh[i]) / ((density / (Elyzer_eff / 100)) + Compr_req), 3))
            else:
                Elyzer_loss.append(round(0.0, 3))
                H2_produced.append(round(0.0, 3))
        except:
            Elyzer_loss.append(round(float(available_kWh[i]) * (1 - Elyzer_eff / 100), 3))
            H2_produced.append(round(float(available_kWh[i]) / ((density / (Elyzer_eff / 100)) + Compr_req), 3))


        ### FILLING THE TANK / COMPRESSION
        try:
            if H2_produced[i] > 0:
                if H2_tank[i-1] + H2_produced[i] - (float(demand_kWh[i]) * (2 - FC_eff / 100)) / (density * FC_eff / 100) > max_capacity:
                    H2_tank.append(round(max_capacity,3))
                    E_fc_sold.append(round(float(available_kWh[i]) - (H2_tank[i] - H2_tank[i-1])*density*Elyzer_eff/100, 3))
                    H2_produced[i] = round(H2_tank[i] - H2_tank[i-1],3)
                else:
                    H2_tank.append(round(H2_tank[i - 1] + H2_produced[i], 3))
                    E_fc_sold.append(round(0.0, 3))
            else:
                H2_tank.append(round(H2_tank[i - 1], 3))
                E_fc_sold.append(round(float(available_kWh[i]), 3))
        except:
            H2_tank.append(round(0.0, 3))
            E_fc_sold.append(round(0.0, 3))


        ### CALCULATE HYDROGEN DEMAND FROM FUEL CELL
        try:
            if H2_tank[i] > 0:
                if H2_tank[i] > (float(demand_kWh[i]) * (2 - FC_eff / 100)) / (density * FC_eff / 100):
                    E_fc_loss.append(round(float(demand_kWh[i]) * (1 - FC_eff / 100), 3))
                    E_fc_demand.append(round(float(demand_kWh[i]) + E_fc_loss[i], 3))
                    H2_demand.append(round(E_fc_demand[i] / (density * FC_eff / 100), 3))
                else:
                    E_fc_loss.append(round(H2_tank[i] * (1 - FC_eff / 100), 3))
                    E_fc_demand.append(round(H2_tank[i] + E_fc_loss[i], 3))
                    H2_demand.append(round(H2_tank[i], 3))
            else:
                E_fc_loss.append(round(0.0, 3))
                E_fc_demand.append(round(0.0, 3))
                H2_demand.append(round(0.0, 3))
        except:
            E_fc_loss.append(round(0.0, 3))
            E_fc_demand.append(round(0.0, 3))
            H2_demand.append(round(0.0, 3))


        ### SUPPLYING TO FUEL CELL / RELEASE
        try:
            if H2_tank[i] > H2_demand[i]:
                E_fc_bought.append(round(0.0, 3))
                H2_tank[i] = round(H2_tank[i] - H2_demand[i], 3)
            else:
                E_fc_bought.append(round(float(demand_kWh[i]) - H2_tank[i] * density * FC_eff / 100, 3))
                H2_tank[i] = 0
        except:
            E_fc_bought.append(round(float(demand_kWh[i]), 3))

        """
        ### CALCULATE HYDROGEN PRODUCTION TO TANK
                
        ### CALCULATE HYDROGEN DEMAND FROM FUEL CELL
        try:
            if H2_tank[i-1] > 0:
                if (H2_tank[i-1] * density * FC_eff/100) > float(demand_kWh):
                    E_fc_loss.append(round(float(demand_kWh[i]) * (1 - FC_eff/100), 3))
                    E_fc_demand.append(round(float(demand_kWh[i]) + E_fc_loss[i], 3))
                else:
                    E_fc_loss.append(round(H2_tank[i-1] * density * (1 - FC_eff/100), 3))
                    E_fc_demand.append(round(H2_tank[i-1] * density * FC_eff/100, 3))
                H2_demand.append(round(E_fc_demand[i] / (density * FC_eff/100), 3))
            else:
                E_fc_loss.append(round(0.0, 3))
                E_fc_demand.append(round(0.0, 3))
                H2_demand.append(round(0.0, 3))
        except:
            E_fc_loss.append(round(0.0, 3))
            E_fc_demand.append(round(0.0, 3))
            H2_demand.append(round(0.0, 3))

        ### FILLING THE TANK / COMPRESSION
        try:
            if H2_tank[i - 1] + H2_produced[i] - H2_demand[i] > max_capacity:
                H2_tank.append(round(max_capacity, 3))
                E_fc_sold.append(round(float(available_kWh[i]) - (H2_produced[i] + H2_tank[i-1] - max_capacity) * density * FC_eff/100, 3))
            else:
                H2_tank.append(round(H2_tank[i - 1] + H2_produced[i], 3))
                if available_kWh[i] > 0: E_fc_sold.append(round(available_kWh[i], 3))
                else: E_fc_sold.append(round(0.0, 3))
        except:
            H2_tank.append(round(H2_produced[i], 3))
            E_fc_sold.append(round(0.0, 3))

        
        try:
            if H2_tank[i-1] + H2_produced[i] - H2_demand[i] > max_capacity:
                H2_tank.append(round(max_capacity,3))
                E_fc_sold.append(round(float(available_kWh[i]) - (H2_produced[i] + H2_tank[i-1] - max_capacity) * density * FC_eff/100,3))
            else:
                H2_tank.append(round(H2_tank[i-1] + H2_produced[i], 3))
                E_fc_sold.append(round(0.0, 3))
        except:
            H2_tank.append(round(H2_produced[i], 3))
            E_fc_sold.append(round(0.0, 3))
        
        ### SUPPLYING TO FUEL CELL / RELEASE
        try:
            if H2_tank[i - 1] > H2_demand[i]:
                E_fc_bought.append(round(0.0, 3))
            else:
                E_fc_bought.append(round(0.0, 3))
        except:
            E_fc_bought.append(round(0.0, 3))
        """
        """ 
        try:
            if H2_tank[i-1] > H2_demand[i]:
                E_fc_bought.append(round(0.0, 3))
                H2_tank[i] = round(H2_tank[i] - H2_demand[i], 3)
            else:
                E_fc_bought.append(round(float(demand_kWh[i]) - H2_tank[i] * density * FC_eff/100, 3))
                H2_tank[i] = 0
        except:
            E_fc_bought.append(round(float(demand_kWh[i]), 3))
        """

    return H2_produced, Elyzer_loss, H2_tank, H2_demand, E_fc_demand, E_fc_loss, E_fc_sold, E_fc_bought
    pass