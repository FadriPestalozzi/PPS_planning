import numpy as np
import pandas as pd

import dataloading as load
import PPSSimulation as pps

# I first want to generate all the necessary workplaces and dispatchlists

# get POs as dataframe
production_orders = load.get_sql_data('.\\load_PO_data.sql')
# get opcs as dataframe
opcs = load.get_sql_data('.\\load_opc_data.sql')

dipatchdepartments = np.unique(opcs[["Dispatchdepartment"]].to_numpy().flatten()).sort()
workplaces = np.unique(opcs[["WorkplaceName"]].to_numpy().flatten()).sort()

