
import csv
import os.path
import cea_storage_capacity.Functions as fun

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"

def bank_potential(energy_demand_df, input_path, potential, per_capita, voltage, bat_capacity, max_discharge, conversion_ef):
    result_df = energy_demand_df[["Name"]].copy()
    people_df = energy_demand_df[["people0"]].copy()
    building_prod, building_dem, building_sto, building_cons, = [], [], [], []
    building_people, building_size, building_maxstr = [], [], []
    building_pb_stored, building_grd_bgt, building_grd_sld, building_cnv_lss = [], [], [], []
    count = 0
    labels = ["Date",
              "GRID_kWh",
              "E_PV_gen_kWh",
              "E_dem_GRID_kWh",
              "E_av_sto_kWh",
              "E_sto_PB_kWh",
              "E_bgt_GRID_kWh",
              "E_sld_GRID_kWh",
              "E_conv_Loss"]

    if not os.path.exists(fun.get_path_pb(input_path, '', 'F')): os.makedirs(fun.get_path_pb(input_path, '', 'F'))

    for name in result_df['Name']:

        inhabitants = people_df['people0'][int(list(result_df['Name']).index(name))]
        size = per_capita * inhabitants * 1000 / voltage
        kWh_production = []

        with open(fun.get_path_pb(input_path, name, 1), 'w', newline='') as file_ST:
            writer = csv.writer(file_ST)

            with open(fun.get_path_pb(input_path, name, 3), 'r') as file_PV:
                date = [row['Date'] for row in csv.DictReader(file_PV)]
            with open(fun.get_path_pb(input_path, name, 3), 'r') as file_PV:
                kWh_panel = [row['E_PV_gen_kWh'] for row in csv.DictReader(file_PV)]
            with open(fun.get_path_pb(input_path, name, 2), 'r') as file_DM:
                kWh_demand = [row['GRID_kWh'] for row in csv.DictReader(file_DM)]

            for row in kWh_panel:
                kWh_production.append(float(row) * (float(potential)/100))

            kWh_av_store = [float(x) * conversion_ef/100 - float(y) for (x, y) in zip(kWh_production, kWh_demand)]
            kWh_requested = [float(y) - float(x) * conversion_ef/100 for (x, y) in zip(kWh_production, kWh_demand)]

            kWh_PB, kWh_bought, kWh_sold, kWh_loss, kWh_stored = Calculate_PB_Performance(kWh_demand,
                                                                                          kWh_production,
                                                                                          size,
                                                                                          voltage,
                                                                                          bat_capacity,
                                                                                          max_discharge,
                                                                                          conversion_ef)

            writer.writerow(labels)
            linea = zip(date,
                        kWh_demand,
                        kWh_production,
                        fun.normalize_list(kWh_requested),
                        fun.normalize_list(kWh_av_store),
                        kWh_PB,
                        kWh_bought,
                        kWh_sold,
                        kWh_loss)

            for row in linea: writer.writerow(row)

        result_df['Name'][count] = name
        building_dem.append(fun.add(kWh_demand))
        building_prod.append(fun.add(kWh_production))
        building_people.append(round(inhabitants, 2))
        building_size.append(round(size, 0))
        building_maxstr.append(round(kWh_stored, 3))
        building_cons.append(fun.add(fun.normalize_list(kWh_requested)))
        building_sto.append(fun.add(fun.normalize_list(kWh_av_store)))
        building_pb_stored.append(round(fun.Sum_Stored(kWh_PB),2))
        building_grd_bgt.append(fun.add(kWh_bought))
        building_grd_sld.append(fun.add(kWh_sold))
        building_cnv_lss.append(fun.add(kWh_loss))
        count += 1

        date.clear()
        kWh_production.clear()
        kWh_panel.clear()
        kWh_demand.clear()
        kWh_av_store.clear()

    result_df['GRID_kWh'] = building_dem
    result_df['E_PV_gen_kWh'] = building_prod
    result_df["people0"] = building_people
    result_df['Bank_size_Ah'] = building_size
    result_df['Emax_str_kWh'] = building_maxstr
    result_df['E_dem_GRID_kWh'] = building_cons
    result_df['E_av_sto_kWh'] = building_sto
    result_df['E_sto_PB_kWh'] = building_pb_stored
    result_df['E_bgt_GRID_kWh'] = building_grd_bgt
    result_df['E_sld_GRID_kWh'] = building_grd_sld
    result_df['E_loss_kWh'] = building_cnv_lss

    return result_df



def Calculate_PB_Performance(Electric_demand, PV_supply, str_capacity, voltage, battery_cap, max_discharge, conversion):
    PowerBank, Buy_GRID, Sell_GRID, Conv_Loss = [], [], [], []
    max_value = str_capacity * (max_discharge/100)
    conversion_eff = conversion/100
    power_limit = (str_capacity * battery_cap) * voltage / 1000

    for i in range(len(Electric_demand)):
        if float(Electric_demand[i]) > 0:
            try:
                if conversion_eff * (float(PV_supply[i]) + float(PowerBank[i - 1])) > float(Electric_demand[i]):
                    if conversion_eff * float(PV_supply[i]) > float(Electric_demand[i]):
                        if fun.AV_store(PowerBank[i - 1], max_value, voltage) > conversion_eff * float(
                                PV_supply[i]) - float(Electric_demand[i]):
                            if conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) < power_limit:
                                PowerBank.append(round(conversion_eff * float(PV_supply[i]) + float(PowerBank[i - 1])
                                                       - float(Electric_demand[i]), 3))
                                Buy_GRID.append(round(0.0, 3))
                                Sell_GRID.append(round(0.0, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                            else:
                                PowerBank.append(round(float(PowerBank[i - 1]) + power_limit, 3))
                                Buy_GRID.append(round(0.0, 3))
                                Sell_GRID.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) -
                                                       power_limit, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                        else:
                            if fun.AV_store(PowerBank[i - 1], max_value, voltage) < power_limit:
                                PowerBank.append(max_value * voltage / 1000)
                                Buy_GRID.append(round(0.0, 3))
                                Sell_GRID.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) -
                                                       fun.AV_store(PowerBank[i - 1], max_value, voltage), 3))
                                Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                            else:
                                PowerBank.append(round(PowerBank[i - 1] + power_limit, 3))
                                Buy_GRID.append(round(0.0, 3))
                                Sell_GRID.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) -
                                                       power_limit, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                    else:
                        if conversion_eff * float(PowerBank[i - 1]) > float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]):
                            if float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]) < power_limit:
                                PowerBank.append(round(float(PowerBank[i - 1]) - (1 + (1 - conversion_eff)) *
                                                       (float(Electric_demand[i]) - conversion_eff * float(PV_supply[i])), 3))
                                Buy_GRID.append(round(0.0, 3))
                                Sell_GRID.append(round(0.0, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * float(Electric_demand[i]), 3))
                            else:
                                PowerBank.append(round(float(PowerBank[i - 1]) - power_limit, 3))
                                Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) +
                                                                                         power_limit), 3))
                                Sell_GRID.append(round(0.0, 3))
                                Conv_Loss.append(
                                    round((1 - conversion_eff) * (float(PV_supply[i]) + power_limit), 3))
                        else:
                            if float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]) < power_limit:
                                PowerBank.append(round(0.0, 3))
                                Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]) -
                                                      float(PowerBank[i - 1]), 3))
                                Sell_GRID.append(round(0.0, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * (float(PV_supply[i]) +
                                                                               float(PowerBank[i - 1])), 3))
                            else:
                                PowerBank.append(round(float(PowerBank[i - 1]) - power_limit, 3))
                                Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) -
                                                                                         power_limit), 3))
                                Sell_GRID.append(round(0.0, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * (float(PV_supply[i]) + power_limit),3))
                else:
                    if float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]) < conversion_eff * float(
                            PowerBank[i - 1]):
                        if float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]) < power_limit:
                            PowerBank.append(round(float(PowerBank[i - 1]) - (1 + (1 - conversion_eff)) * float(Electric_demand[i])
                                                   + conversion_eff * float(PV_supply[i]), 3))
                            Buy_GRID.append(round(0.0, 3))
                            Sell_GRID.append(round(0.0, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * float(Electric_demand[i]), 3))
                        else:
                            PowerBank.append(round(float(PowerBank[i - 1]) - power_limit * conversion_eff, 3))
                            Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) +
                                                                                     power_limit), 3))
                            Sell_GRID.append(round(0.0, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * (float(PV_supply[i]) + power_limit), 3))
                    else:
                        if PowerBank[i - 1] == 0:
                            PowerBank.append(round(0.0, 3))
                            Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]), 3))
                            Sell_GRID.append(round(0.0, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                        elif float(conversion_eff * PowerBank[i - 1]) < power_limit:
                            PowerBank.append(round(0.0, 3))
                            Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) +
                                                                                     float(PowerBank[i - 1])), 3))
                            Sell_GRID.append(round(0.0, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * (float(PV_supply[i]) +
                                                                           float(PowerBank[i - 1])), 3))
                        else:
                            PowerBank.append(round(float(PowerBank[i - 1]) - power_limit, 3))
                            Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) +
                                                                                     power_limit), 3))
                            Sell_GRID.append(round(0.0, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * (float(PV_supply[i]) + float(PowerBank[i - 1])), 3))
            except:
                if float(Electric_demand[i]) > conversion_eff * float(PV_supply[i]):
                    PowerBank.append(round(0.0, 3))
                    Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * float(PV_supply[i]), 3))
                    Sell_GRID.append(round(0.0, 3))
                    Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                else:
                    if conversion_eff * float(PV_supply[i]) > (float(Electric_demand[i]) + fun.AV_store(0, max_value, voltage)):
                        if conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) > power_limit:
                            PowerBank.append(round(power_limit, 3))
                            Buy_GRID.append(round(0.0, 3))
                            Sell_GRID.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) -
                                                   power_limit, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                        else:
                            PowerBank.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]), 3))
                            Buy_GRID.append(round(0.0, 3))
                            Sell_GRID.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) -
                                                   fun.AV_store(PowerBank[i], max_value, voltage), 3))
                            Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                    else:
                        if conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) > power_limit:
                            PowerBank.append(round(power_limit, 3))
                            Buy_GRID.append(round(0.0, 3))
                            Sell_GRID.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]) -
                                                   power_limit, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
                        else:
                            PowerBank.append(round(conversion_eff * float(PV_supply[i]) - float(Electric_demand[i]), 3))
                            Buy_GRID.append(round(0.0, 3))
                            Sell_GRID.append(round(0.0, 3))
                            Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))
        else:
            PowerBank.append(round(0.0, 3))
            Buy_GRID.append(round(0.0, 3))
            Sell_GRID.append(round(conversion_eff * float(PV_supply[i]), 3))
            Conv_Loss.append(round((1 - conversion_eff) * float(PV_supply[i]), 3))


    return PowerBank, Buy_GRID, Sell_GRID, Conv_Loss, max_value * voltage / 1000
    pass
