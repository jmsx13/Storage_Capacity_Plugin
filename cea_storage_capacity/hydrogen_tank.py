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


"""
                        kWh_demand,kWh_available,density,electrolyzer_eff,fuelcell_eff,compressor_req
"""

def H2_Storage_Supply (demand_kWh, available_kWh, h2_density, Elyzer_eff, FC_eff, Compr_req):
    H2_produced, H2_tank, H2_demand = [], [], []
    E_fc_demand, Elyzer_loss, E_fc_loss = [], [], []
    E_fc_sold, E_fc_bought = [], []

    for i in range(len(available_kWh)):

        ### CALCULATE HYDROGEN PRODUCTION TO TANK
        H2_produced.append(round(float(available_kWh[i]) / ((h2_density / (Elyzer_eff / 100)) + Compr_req), 3))
        Elyzer_loss.append(round(float(available_kWh[i]) * (1 - Elyzer_eff / 100), 3))

        ### FILLING THE TANK / COMPRESSION
        try:
            if H2_produced[i] > 0:
                H2_tank.append(round(H2_tank[i - 1] + H2_produced[i], 3))
                E_fc_sold.append(round(0.0, 3))
            else:
                H2_tank.append(round(H2_tank[i - 1], 3))
                E_fc_sold.append(round(float(available_kWh[i]), 3))
        except:
            H2_tank.append(round(0.0, 3))
            E_fc_sold.append(round(0.0, 3))


        ### CALCULATE HYDROGEN DEMAND FROM FUEL CELL
        if H2_tank[i] > 0:
            if H2_tank[i] > (float(demand_kWh[i]) * (2 - FC_eff / 100)) / (h2_density / (FC_eff / 100)):
                E_fc_loss.append(round(float(demand_kWh[i]) * (1 - FC_eff / 100), 3))
                E_fc_demand.append(round(float(demand_kWh[i]) + E_fc_loss[i], 3))
                H2_demand.append(round(E_fc_demand[i] / (h2_density / (FC_eff / 100)), 3))
            else:
                E_fc_loss.append(round(H2_tank[i] * (1 - FC_eff / 100), 3))
                H2_demand.append(round(H2_tank[i], 3))
                E_fc_demand.append(round(H2_demand[i] * h2_density * (FC_eff / 100) + E_fc_loss[i], 3))      #round(H2_tank[i] + E_fc_loss[i], 3)
        else:
            E_fc_loss.append(round(0.0, 3))
            E_fc_demand.append(round(0.0, 3))
            H2_demand.append(round(0.0, 3))


        ### SUPPLYING TO FUEL CELL / EXPANSION
        if H2_tank[i] > 0:
            if H2_tank[i] > H2_demand[i] / (FC_eff / 100):
                E_fc_bought.append(round(0.0, 3))
                H2_tank[i] = round(H2_tank[i] - H2_demand[i], 3)
            else:
                E_fc_bought.append(round(float(demand_kWh[i]) - (H2_tank[i] * h2_density * FC_eff / 100), 3))
                H2_tank[i] = 0
        else:
            E_fc_bought.append(round(float(demand_kWh[i]), 3))


    return H2_produced, H2_tank, H2_demand, E_fc_demand, E_fc_sold, E_fc_bought, Elyzer_loss, E_fc_loss
    pass


def hydrogen_production(ww_demand_df, input_path, source, density, electrolyzer_eff, compressor_req, fuelcell_eff, occupancy, fuel_economy, vkt, emissions):
    labels = ["Date",
              "E_demand_kWh",
              "E_available_kWh",
              "H2_produced_kg",
              "H2_stored_kg",
              "H2_demand_kg",
              "FC_supply_kWh",
              "E_bgt_fc_kWh",
              "E_sld_fc_kWh",
              "El_loss_kWh",
              "FC_loss_kWh"]
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

            if source == 'E_sld_grid_kWh':
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_DM:
                    kWh_available = [row['E_sld_GRID_kWh'] for row in csv.DictReader(file_DM)]
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_DM:
                    kWh_demand = [row['E_bgt_GRID_kWh'] for row in csv.DictReader(file_DM)]
            else:
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_H2:
                    kWh_available = [row['E_PV_gen_kWh'] for row in csv.DictReader(file_H2)]
                with open(fun.get_path_h2(input_path, name, 3), 'r') as file_DM:
                    kWh_demand = [row['GRID_kWh'] for row in csv.DictReader(file_DM)]

            h2_produced, h2_tank, h2_demand, fc_demand, pb_fc_sold, pb_fc_bought, elyzer_loss, fc_loss = H2_Storage_Supply(kWh_demand,
                                             kWh_available,
                                             density,
                                             electrolyzer_eff,
                                             fuelcell_eff,
                                             compressor_req)

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
    result_df['E_el_loss_kWh'] = building_elz_loss
    result_df['E_fc_loss_kWh'] = building_fc_loss

    return result_df


def main(config):

    locator3 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
    summary_h2 = hydrogen_production(locator3.get_total_demand.read(), locator3.get_input_folder(),
                                     config.hydrogen_tank.electric_source,
                                     config.hydrogen_tank.energy_density,
                                     config.hydrogen_tank.electrolyzer_efficiency,
                                     config.hydrogen_tank.compressor_requirement,
                                     config.hydrogen_tank.fuel_cell_efficiency,
                                     config.hydrogen_tank.vehicle_occupancy,
                                     config.hydrogen_tank.fuel_economy,
                                     config.hydrogen_tank.vehicle_km_travelled,
                                     config.hydrogen_tank.carbon_emissions)
    locator3.hydrogen_production.write(summary_h2)

    pass


if __name__ == '__main__':
    main(cea.config.Configuration())