from collections import defaultdict

import numpy as np
import pandas as pd
from time import time as timestamp
import dataloading as load
import PPSSimulation as pps


def build_dataset():
    """
    Loads and processes production orders and operation cycles data from SQL files.
    Creates ProductionOrder and OperationCycle objects and organizes them into collections.

    Returns:
        tuple: Contains:
            - production_orders (dict): Dictionary of ProductionOrder objects keyed by PA
            - opcs (list): List of all OperationCycle objects
            - workplaces (ndarray): Sorted array of unique workplace names
            - opcs_by_PA (dict): Dictionary of OperationCycle objects grouped by PA
    """
    print('Loading data')
    t0 = timestamp()

    # get POs as dataframe
    production_orders_data = load.get_sql_data('.\\load_PO_data.sql')
    # get opcs as dataframe
    opcs_data = load.get_sql_data('.\\load_opc_data.sql')

    workplaces = np.unique(opcs_data[["WorkPlaceName"]].to_numpy().flatten()).sort()

    opcs = []
    opcs_by_PA = {}

    # generate and group opcs by PA
    for _, row in opcs_data.iterrows():
        obj = pps.OperationCycle(*row)
        opcs.append(obj)
        if row['PA'] not in opcs_by_PA:
            opcs_by_PA[row['PA']] = [obj]
        else:
            opcs_by_PA[row['PA']].append(obj)

    # generate all PA, reference opcs
    production_orders = {}
    for _, row in production_orders_data.iterrows():
        try:
            production_orders[row['PA']] = pps.ProductionOrder(row['PA'], opcs_by_PA[row['PA']])
        except KeyError as e:
            print(f'Could not find {row["PA"]} in opcs_by_PA')
            print(e)
            continue
        except Exception as e:
            print(f'Could not create ProductionOrder for {row["PA"]}')
            continue

    print(f'Loading time elapsed: {timestamp() - t0}')

    return production_orders, opcs, workplaces, opcs_by_PA


if __name__ == '__main__':
    # start with getting the data set from sql
    build_dataset()
