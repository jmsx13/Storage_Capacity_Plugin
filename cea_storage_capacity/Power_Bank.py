
import cea_storage_capacity.Functions as fun

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"

def Size_PB_Capacity(Electric_demand, PV_supply, step, tolerance, efficiency):
    PowerBank, Bought_GRID = [], []
    Total_Bought, Capacities = [], []
    BCapacity = 0.0
    position = 0
    Flag = True

    while Flag:
        for i in range(len(Electric_demand)):
            try:
                if float(Electric_demand[i]) > 0:
                    if float(PV_supply[i]) * efficiency/100 + PowerBank[i-1] > float(Electric_demand[i]):
                        if float(PV_supply[i]) * efficiency/100 + PowerBank[i-1] > BCapacity:
                            PowerBank.append(round(BCapacity, 3))
                        else:
                            PowerBank.append(round(float(PV_supply[i]) * efficiency/100 + PowerBank[i-1] - float(Electric_demand[i]), 3))
                    else:
                        PowerBank.append(round(0.0, 3))

                    if PowerBank[i-1] * efficiency/100 > float(Electric_demand[i]):
                        Bought_GRID.append(round(0.0, 3))
                    else:
                        Bought_GRID.append(round(float(Electric_demand[i]) - PowerBank[i-1] * efficiency/100, 3))

                else:
                    if float(PV_supply[i]) * efficiency/100 + PowerBank[i-1] > BCapacity:
                        PowerBank.append(round(BCapacity, 3))
                    else:
                        PowerBank.append(round(float(PV_supply[i]) * efficiency/100 + PowerBank[i-1], 3))
                    Bought_GRID.append(round(0.0, 3))
            except:
                PowerBank.append(round(float(PV_supply[i]) * efficiency/100 , 3))
                Bought_GRID.append(round(float(Electric_demand[i]), 3))

        Total_Bought.append(fun.add(Bought_GRID))
        Capacities.append(BCapacity)
        #print("Capacity:", Capacities[len(Capacities)-1],"Bought:", Total_Bought[len(Total_Bought)-1])
        try:
            Slope = round(100 * (Capacities[position - 1] - Capacities[position]) / (Total_Bought[position - 1] - Total_Bought[position]),1)
            #print("Capacity:",Capacities[position],", Bought:",Total_Bought[position],"Elasticity:",Elasticity)
            if Slope <= -tolerance:
                Flag = False
        except:
            if Total_Bought[position]<=1:
                Flag = False
            else:
                Flag = True

        PowerBank.clear()
        Bought_GRID.clear()

        BCapacity += round(step,3)
        position += 1

    #print("Building:")
    #print ("Capacities:",Capacities, "\nBought:", Total_Bought)
    return Capacities[len(Capacities)-1], Total_Bought[len(Total_Bought)-1]



def Calculate_PB_Performance(Electric_demand, PV_supply, str_capacity, voltage, c_rate, max_discharge, efficiency):
    PowerBank, Buy_GRID, Sell_GRID, Conv_Loss = [], [], [], []
    max_value = str_capacity * (max_discharge/100)
    conversion_eff = efficiency/100
    power_limit = (str_capacity * c_rate) * voltage / 1000

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
                                Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) +
                                                      float(PowerBank[i - 1])), 3))
                                Sell_GRID.append(round(0.0, 3))
                                Conv_Loss.append(round((1 - conversion_eff) * (float(PV_supply[i]) +
                                                                               float(PowerBank[i - 1])), 3))
                            else:
                                PowerBank.append(round(float(PowerBank[i - 1]) - power_limit, 3))
                                Buy_GRID.append(round(float(Electric_demand[i]) - conversion_eff * (float(PV_supply[i]) +
                                                                                         power_limit), 3))                    # revise change of negative sign before power_limit
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