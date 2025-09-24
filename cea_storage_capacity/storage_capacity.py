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
__credits__ = ['IN+ - Instituto Superior Técnico / Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"


class StorageCapacityPlugin(cea.plugin.CeaPlugin):
    pass

def main(config):

    if config.storage_potential.calculate_performance_pb:
        locator1 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
        summary_bpb = bpb.bank_potential(locator1.get_total_demand.read(),
                                         locator1.get_input_folder(),
                                         config.storage_potential.pv_potential_used,
                                         config.storage_potential.power_capacity,
                                         config.storage_potential.rated_voltage,
                                         config.storage_potential.battery_capacity,
                                         config.storage_potential.maximum_discharge,
                                         config.storage_potential.conversion_efficiency)
        locator1.power_bank.write(summary_bpb)


    if config.storage_potential.calculate_performance_sc:
        locator2 = cea.inputlocator.InputLocator(config.scenario, config.plugins)
        summary_swt = swt.collector_performance(locator2.get_total_demand.read(),
                                                locator2.get_input_folder(),
                                                config.storage_potential.sc_potential_used,
                                                config.storage_potential.water_capacity,
                                                config.storage_potential.heat_capacity,
                                                config.storage_potential.inlet_temperature,
                                                config.storage_potential.outlet_temperature,
                                                config.storage_potential.max_temperature,
                                                config.storage_potential.loss_coefficient)
        locator2.collector_performance.write(summary_swt)


    if config.storage_potential.calculate_performance_h2:
        locator3 = cea.inputlocator.InputLocator(config.scenario, config.plugins)

        if config.storage_potential.calculate_performance_pb: case = True
        else: case = False

        summary_h2 = h2p.hydrogen_production(locator3.get_total_demand.read(), locator3.get_input_folder(),
                                             config.storage_potential.h2_energy_density,
                                             config.storage_potential.electrolyzer_efficiency,
                                             config.storage_potential.fuelcell_efficiency,
                                             config.storage_potential.compressor_requirement,
                                             config.storage_potential.tank_capacity, case)
        locator3.hydrogen_production.write(summary_h2)

    pass


if __name__ == '__main__':
    main(cea.config.Configuration())
