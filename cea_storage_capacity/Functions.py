import os
#import numpy as np

__author__ = "Jaime Cevallos-Sierra"
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ['IN+ - Instituto Superior Técnico/Jaime Cevallos-Sierra']
__maintainer__ = "Jaime Cevallos-Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"


def Sum_Content(kWh_list):
    suma = 0.0
    lista = []
    for row in kWh_list:
        suma += float(row)
        lista.append(suma)
    return lista
    pass


def Sum_Stored(kWh_PB, kWh_Demand, Qmax):
    suma = 0.0
    lista = []
    for i in range(len(kWh_PB)):
        if float(kWh_PB[i]) > float(kWh_PB[i-1]):
            suma += (float(kWh_PB[i]) - float(kWh_PB[i-1]))
            lista.append(suma)
        else:
            if float(kWh_PB[i]) == Qmax:
                if float(kWh_Demand[i]) > 0:
                    suma += float(kWh_Demand[i])
                    lista.append(suma)
                else: lista.append(suma)
            else: lista.append(suma)

    return lista[len(lista)-1]
    pass


def add(data):
    s = 0.0
    for n in data:
        s = s + float(n)
    return round(s,2)


def normalize_list(data):
    lista = []
    for n in data:
        if n > 0: lista.append(n)
        else: lista.append('0.0')
    return lista


def AV_store(stored, limit, vol):
    act_state = 0.0
    if stored < (limit * vol / 1000):
        act_state = (limit * vol / 1000) - stored
    return round(act_state, 3)


def ambient_Loss(max, min, area, coefficient):
    return round(coefficient * area * (float(max) - float(min)) / 1000, 3)


"""def get_random(mean, stdev):
    random = np.random.normal(mean, stdev)
    if random < 0: random = 0
    return random"""


def Estimate_Vehicles(people, rate):
    max_, min_ = 0, 0
    for i in range(0,744):
        if float(people[i]) > max_: max_ = float(people[i])
        if float(people[i]) < min_: min_ = float(people[i])

    return round((max_ - min_) / rate,0)


def get_path_pb(input_path, name, value):
    if value == 'F':
        # OUTPUT FOLDER PATH
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\power_bank\\"
    elif value == 1:
        # BUILDING NEW FILE
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\power_bank\\" + name + "_PB.csv"
    elif value == 2:
        # BUILDING DEMAND FOLDER
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\demand\\" + name + ".csv"
    elif value == 3:
        # BUILDING SOURCE FILE
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\solar\\" + name + "_PV.csv"
    else:
        output_path = "Error!!!"

    return output_path

def get_path_sc(input_path, name, value):
    if value == 'F':
        # OUTPUT FOLDER PATH
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\water_tank\\"
    elif value == 1:
        # BUILDING NEW FILE
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\water_tank\\" + name + "_SC.csv"
    elif value == 2:
        # BUILDING DEMAND FOLDER
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\demand\\" + name + ".csv"
    elif value == 3:
        # BUILDING SOURCE FILE
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\solar\\" + name + "_SC_ET.csv"
    else:
        output_path = "Error!!!"

    return output_path

def get_path_h2(input_path, name, value):
    if value == 'F':
        # OUTPUT FOLDER PATH
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\hydrogen\\"
    elif value == 1:
        # BUILDING NEW FILE
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\hydrogen\\" + name + "_H2.csv"
    elif value == 2:
        # BUILDING DEMAND FOLDER
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\solar\\" + name + "_PV.csv"
    elif value == 3:
        # BUILDING SOURCE FILE
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\storage\\power_bank\\" + name + "_PB.csv"
    else:
        output_path = "Error!!!"

    return output_path


"""
def get_path(input_path, name, value, s):
    if value == 'F':
        # OUTPUT FOLDER PATH
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\storage-capacity\\"
    elif value == 1:
        # OUTPUT STORAGE FOLDER
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\storage-capacity\\" + name + "_ST.csv"
    elif value == 2:
        # DEMAND FOLDER
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\demand\\" + name + ".csv"
    elif value == 3:
        # PV POTENTIAL FOLDER
        output_path = os.path.dirname(input_path) + "\\outputs\\data\\potentials\\solar\\" + name + "_PV.csv"
    else:
        output_path = "None"
    return output_path
"""