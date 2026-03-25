from time import sleep
from datetime import datetime
import matplotlib; matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import PPSSimulation as pps
import dataloading as load

# import webapp as web

if __name__ == '__main__':
    # start with getting the data set from sql
    days_offset = 14
    production_orders, opcs, workplaces, dispatchdepartments, opcs_by_PA = pps.build_dataset(days_offset=days_offset,
                                                                                             opcs_data=load.get_data('./data/opcs.csv'),
                                                                                             production_orders_data=load.get_data('./data/production_orders.csv')
                                                                                             ,mute=False)
    pps.day_based_simulation(production_orders, opcs, workplaces, dispatchdepartments, days_offset=days_offset)
