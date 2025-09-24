# coding=utf-8
from __future__ import division
from __future__ import print_function

import cea.config
import cea.inputlocator
import cea.plugin

import cea_storage_capacity.Power_Bank as bpb
import cea_storage_capacity.Water_Tank as swt
import cea_storage_capacity.H2_Tank as h2p

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"


class StorageCapacityPlugin(cea.plugin.CeaPlugin):
    pass

def main(config):

    locator1 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
    summary_bpb = bpb.bank_potential(locator1.get_total_demand.read(),
                                    locator1.get_input_folder(),
                                    config.battery_bank.pv_potential_used,
                                    config.battery_bank.power_capacity,
                                    config.battery_bank.rated_voltage,
                                    config.battery_bank.battery_capacity,
                                    config.battery_bank.maximum_discharge,
                                    config.battery_bank.conversion_efficiency)
    locator1.power_bank.write(summary_bpb)

    pass


if __name__ == '__main__':
    main(cea.config.Configuration())


"""
locator1 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
    summary_bpb = bpb.bank_potential(locator1.get_total_demand.read(),
                                    locator1.get_input_folder(),
                                    config.battery_bank.pv_potential_used,
                                    config.battery_bank.power_capacity,
                                    config.battery_bank.rated_voltage,
                                    config.battery_bank.battery_capacity,
                                    config.battery_bank.maximum_discharge,
                                    config.battery_bank.conversion_efficiency)
    locator1.power_bank.write(summary_bpb)


    locator2 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
    summary_swt = swt.collector_performance(locator2.get_total_demand.read(),
                                            locator2.get_input_folder(),
                                            config.water_tank.sc_potential_used,
                                            config.water_tank.water_capacity,
                                            config.water_tank.heat_capacity,
                                            config.water_tank.inlet_temperature,
                                            config.water_tank.outlet_temperature,
                                            config.water_tank.max_temperature,
                                            config.water_tank.loss_coefficient)
    locator2.collector_performance.write(summary_swt)


    if config.hydrogen_tank.calculate_performance_h2:
        locator3 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
        if config.hydrogen_tank.calculate_performance_pb:
            summary_h2 = h2p.hydrogen_production(locator3.get_total_demand.read(), locator3.get_input_folder(),
                                                 config.hydrogen_tank.h2_conversion_efficiency,
                                                 config.hydrogen_tank.energy_density,
                                                 config.hydrogen_tank.tank_capacity,
                                                 config.hydrogen_tank.fuel_economy,
                                                 config.hydrogen_tank.vehicle_km_travelled,
                                                 config.hydrogen_tank.carbon_emissions, True)
        else:
            summary_h2 = h2p.hydrogen_production(locator3.get_total_demand.read(), locator3.get_input_folder(),
                                                 config.hydrogen_tank.h2_conversion_efficiency,
                                                 config.hydrogen_tank.energy_density,
                                                 config.hydrogen_tank.tank_capacity,
                                                 config.hydrogen_tank.fuel_economy,
                                                 config.hydrogen_tank.vehicle_km_travelled,
                                                 config.hydrogen_tank.carbon_emissions, False)
        locator3.hydrogen_production.write(summary_h2)
"""