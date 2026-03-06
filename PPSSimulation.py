from datetime import datetime, timedelta

import numpy as np

import dataloading as load
from time import time as timestamp, sleep


import pandas as pd

# ----------------------------
# Kapazitätstabelle
# Einheit = Aufträge pro Tag
# 80% von max. Kapazität
# ----------------------------
lookup_capa_per_day = pd.read_csv('./capa_per_wpg.csv', delimiter=';', encoding='UTF-8')
lookup_parallel_per_day = pd.read_csv('./capa_per_wpg.csv', delimiter=';', encoding='UTF-8')
# load a daily capacity of at least one opc per day
lookup_capa_per_day = lookup_capa_per_day.set_index('Workplace')['MaxOPCs'].mul(0.8).to_dict()
lookup_parallel_per_day = lookup_parallel_per_day.set_index('Workplace')['parallel'].to_dict()
for key in lookup_capa_per_day.keys():
    if lookup_capa_per_day[key] < 1:
        lookup_capa_per_day[key] = 1

class sim_clock():
    def __init__(self, date=datetime.today(), hour=datetime.now().hour):
        self.date = date.replace(hour=hour, minute=0, second=0, microsecond=0)

    def next_day(self, delta = 1):
        self.date += timedelta(days=delta)
        return self.date

    def tick(self, delta = 1):
        self.date += timedelta(hours=delta)

    def difference(self, other_date):
        return (self.date - other_date.date).days * 24 + (self.date - other_date.date).seconds // 3600

class Workplace:
    def __init__(self, name, capa_per_day=None, parallel_processes=None):
        self.name = name
        self.location = None
        if capa_per_day is None:
            self.load_capa_from_file()
        else:
            self.capa_per_day = capa_per_day # use the floor of capa_per_day
        if parallel_processes is None:
            self.load_parallel_from_file()
        else:
            self.parallel_processes = parallel_processes # use the floor of capa_per_day
        self.input_wip: list[ProductionOrder] = []
        self.output_wip: list[ProductionOrder] = []

    # def run(self, date = sim_clock()):
    #     """
    #     Process work-in-progress items according to workplace capacity.
    #
    #     Moves items from input queue to output queue based on the daily capacity limit.
    #     Input queue is updated to remove processed items.
    #
    #     Returns:
    #         None
    #     """
    #     if self.parallel_processes is None:
    #         raise Exception ('No Capacity defined for Workplace')
    #     if type(self.parallel_processes) is not int:
    #         self.parallel_processes = int(self.parallel_processes)
    #     # Convert up to capa_per_day items from input to output
    #     if len(self.input_wip) < self.parallel_processes:
    #         self.output_wip = self.input_wip
    #     else:
    #         self.output_wip = list(self.input_wip)[:self.parallel_processes]
    #     for pa in self.output_wip:
    #         pa.current_step.mark_complete(date)
    #     #self.input_wip = list(self.input_wip)[self.parallel_processes:]
    #
    # def ship_output_wip(self, date = sim_clock()):
    #     if len(self.output_wip)<1:
    #         return
    #     for pa in self.output_wip:
    #         if pa.next_step is None:
    #             pa.FinishedDate = date.date
    #             break
    #         pa.next_step.workplace.input_wip.append(pa)
    #     self.output_wip = []
    #
    # def run_and_ship(self, date = sim_clock()):
    #     self.run(date)
    #     self.ship_output_wip()

    def load_parallel_from_file(self, default=1, mute=True):
        try:
            self.parallel_processes = lookup_parallel_per_day[self.name]
        except KeyError as e:
            if not mute:
                print(f'Could not find {self.name} in lookup_capa_per_day')
            if default:
                self.parallel_processes = default
            else:
                raise e

    def load_capa_from_file(self, default=1, mute=True):
        try:
            self.capa_per_day = lookup_capa_per_day[self.name]
        except KeyError as e:
            if not mute:
                print(f'Could not find {self.name} in lookup_capa_per_day')
            if default:
                self.capa_per_day = default
            else:
                raise e

class Dispatchdepartment:
    def __init__(self, name):
        self.name = name
        self.workplaces: list[Workplace] = []


    def run(self, date = sim_clock()):
        """
        Process work-in-progress items according to workplace capacity.

        Moves items from input queue to output queue based on the daily capacity limit.
        Input queue is updated to remove processed items.

        Returns:
            None
        """
        for wp in self.workplaces:
            if wp.parallel_processes is None:
                raise Exception ('No parallel processing defined for workplace')
            if type(wp.parallel_processes) is not int:
                wp.parallel_processes = int(wp.parallel_processes)
            # Progress up to parallel_processes items from input to output
            # process the whole wip if parallel places exist, else only the first couple
            if len(wp.input_wip) < wp.parallel_processes:
                for pa in wp.input_wip:
                    pa.current_step.progress(date)
            else:
                for pa in wp.input_wip[:wp.parallel_processes]:
                    pa.current_step.progress(date)
            # now check all finished opcs and move them to output_wip
            for pa in wp.input_wip:
                if pa.current_step.opc_state == 3:
                    wp.output_wip.append(pa)
                    pa.current_step = pa.next_step
                    try:
                        wp.input_wip.remove(pa)
                    except ValueError:
                        print(f'Could not remove {pa.PA} from input_wip', wp.name)
                        print('in, out', wp.input_wip, wp.output_wip)
                try:
                    pa.next_step = pa.next_step.next_step
                except AttributeError as e:
                    # there is no next step, PA is finished
                    pa.next_step = None
        return

    def ship_output_wip(self, date = sim_clock()):
        for wp in self.workplaces:
            if len(wp.output_wip)<1:
                break
            for pa in wp.output_wip:
                if pa.next_step is None:
                    pa.FinishedDate = date.date
                    break
                pa.next_step.workplace.input_wip.append(pa)
            wp.output_wip = []

    def run_and_ship(self, date = sim_clock()):
        self.run(date)
        self.ship_output_wip(date)

    def get_dispatchlist(self):
        dispatchlist = []
        for wp in self.workplaces:
            dispatchlist.extend(wp.output_wip)
        return dispatchlist

class ProductionOrder:
    """
    Represents a production order in the manufacturing system.

    Attributes:
        id (str): Unique identifier for the production order
        operationcycles (list): List of operation cycles associated with this order
        current_step (int): Current production step number
        current_dispatchdep (str): Current dispatch department
        next_step (int): Next production step number
        next_dispatchdep (str): Next dispatch department
        age (int): Age of the production order
        PA (str): Production order number
        ProductNumber (str): Product number identifier
        ProductVersion (str): Version of the product
        ProductRevision (str): Revision of the product
        PlanNumber (str): Planning number
        PhasenCode (str): Phase code
        PiecesPerBoard (int): Number of pieces per board
        TargetAmount (int): Target production amount
        Customer (str): Customer identifier
        StartDate (datetime): Start date of production
        FinishedDate (datetime): Completion date
        PPSAdminDate (datetime): PPS administration date
        SapOrderType (str): SAP order type
        IsDeleted (bool): Deletion status
        DeliveryForecastPpsDate (datetime): Forecast delivery date
        DeliveryCriticalityPpsBool (bool): Delivery criticality flag
    """

    def __init__(self,
                 PA=None,
                 ProductNumber=None,
                 ProductVersion=None,
                 ProductRevision=None,
                 PlanNumber=None,
                 PhasenCode=None,
                 PiecesPerBoard=None,
                 TargetAmount=None,
                 Customer=None,
                 StartDate=None,
                 FinishedDate=None,
                 PPSAdminDate=None,
                 SapOrderType=None,
                 IsDeleted=None,
                 DeliveryForecastPpsDate=None,
                 DeliveryCriticalityPpsBool=None,
                 operationcycles=None,
                 current_step=None,
                 current_dispatchdep=None,
                 next_step=None,
                 next_dispatchdep=None,
                 age=None):
        """
        Initialize a new ProductionOrder instance.

        :param id: Unique identifier for the production order
        :param operationcycles: List of operation cycles associated with this production order
        """
        self.id = id
        self.operationcycles = operationcycles
        self.current_step: OperationCycle = current_step
        self.current_dispatchdep = current_dispatchdep
        self.next_step = next_step
        self.next_dispatchdep = next_dispatchdep
        self.age = age
        self.PA = PA
        self.ProductNumber = ProductNumber
        self.ProductVersion = ProductVersion
        self.ProductRevision = ProductRevision
        self.PlanNumber = PlanNumber
        self.PhasenCode = PhasenCode
        self.PiecesPerBoard = PiecesPerBoard
        self.TargetAmount = TargetAmount
        self.Customer = Customer
        self.StartDate = StartDate
        self.FinishedDate = FinishedDate
        self.PPSAdminDate = PPSAdminDate
        self.SapOrderType = SapOrderType
        self.IsDeleted = IsDeleted
        self.DeliveryForecastPpsDate = DeliveryForecastPpsDate
        self.DeliveryCriticalityPpsBool = DeliveryCriticalityPpsBool

class OperationCycle:
    """
    Represents an operational cycle within a workplace or machine process.

    This class is designed to model the various attributes and metrics
    associated with an operational cycle, such as planned and actual amounts,
    cycle state, timing information, and other relevant data points.

    :ivar PA: Optional process number or ID associated with the cycle.
    :ivar PosNumber: Position number of the operation within a sequence.
    :ivar opcID: Unique identifier for the operational cycle.
    :ivar WorkPlaceName: Name of the workplace where the operation is performed.
    :ivar dispatchdepartment: Department responsible for dispatching the work.
    :ivar Machine: Identification or name of the machine involved in the cycle.
    :ivar AdhocChangeState: Indicates if an ad-hoc change is applied to the cycle state.
    :ivar opc_state: Numeric representation of the operational cycle's state. 0 = not started / 1 = ongonig / 2 = stopped / 3 = done
    :ivar opc_state_text: Text description of the operational cycle's state. 0 = not started / 1 = ongonig / 2 = stopped / 3 = done
    :ivar PlannedAmountPieces: Planned number of workpieces for the cycle.
    :ivar ActualAmountPieces: Actual number of workpieces completed in the cycle.
    :ivar PlannedAmountBoards: Planned number of boards for the cycle.
    :ivar ActualAmountBoards: Actual number of boards completed in the cycle.
    :ivar PlannedOperationTime: Planned operation time (in seconds or another unit).
    :ivar ActualOperationTime: Actual operation time (in seconds or another unit).
    :ivar TotalInterruptTime: Total interrupt time occurring during the cycle.
    :ivar TotalActiveTime: Total active time logged for the cycle.
    :ivar opc_endtimestamp: Timestamp when the operational cycle ended.
    """
    def __init__(self, PA=None, PosNumber=None, opcID=None, workplace=None,
                 dispatchdepartment=None, machine=None, AdhocChangeState=None,
                 opc_state=None, opc_state_text=None, PlannedAmountPieces=None,
                 ActualAmountPieces=None, PlannedAmountBoards=None,
                 ActualAmountBoards=None, PlannedOperationTime=None,
                 ActualOperationTime=None, TotalInterruptTime=None,
                 TotalActiveTime=None, opc_endtimestamp=None, next_step=None):
        """
        Represents a data structure to handle and store operational data regarding a
        workplace's planned and actual performance, operational state, and timestamps.
        This structure allows tracking, analysis, and comparison of planned versus
        actual performance metrics, including operation timings and completion state.

        This class is used for encapsulating all data involving the operational
        state and details of a machine or process. Using attributes, it provides
        information related to the planned and successful achievements, the state
        of operation, as well as related department and workplace details.

        :param PA: Planned activity identifier. Can hold information related to
                   the planned operation.
        :type PA: optional, any

        :param PosNumber: Position or serial number associated with this specific
                          operational record.
        :type PosNumber: optional, any

        :param opcID: Unique identifier for the operational process control (OPC).
        :type opcID: optional, any

        :param WorkPlaceName: Name or identifier for the workplace or station
                              related to this machine or process.
        :type WorkPlaceName: optional, any

        :param dispatchdepartment: Department responsible for dispatching related
                                   processes or tasks.
        :type dispatchdepartment: optional, any

        :param Machine: Machine identifier or name being tracked within this
                        operational data.
        :type Machine: optional, any

        :param AdhocChangeState: Specifies whether there was an ad-hoc state
                                 change during the operation.
        :type AdhocChangeState: optional, any

        :param opc_state: Numeric or coded representation of the operational
                          state of the process or machine.
        :type opc_state: optional, any

        :param opc_state_text: Text description of the operational state of the
                               process or machine.
        :type opc_state_text: optional, any

        :param PlannedAmountPieces: Number of pieces that were initially
                                     planned to be produced.
        :type PlannedAmountPieces: optional, any

        :param ActualAmountPieces: Actual number of pieces produced during the
                                   operation.
        :type ActualAmountPieces: optional, any

        :param PlannedAmountBoards: Number of boards (or equivalent elements)
                                     planned for production.
        :type PlannedAmountBoards: optional, any

        :param ActualAmountBoards: Actual number of boards (or equivalent
                                   elements) produced.
        :type ActualAmountBoards: optional, any

        :param PlannedOperationTime: Time planned for the operation, in seconds
                                     or a predefined time unit.
        :type PlannedOperationTime: optional, any

        :param ActualOperationTime: Actual operation duration calculated in
                                    seconds or a predefined time unit.
        :type ActualOperationTime: optional, any

        :param TotalInterruptTime: Total time during the operation in which
                                   processes were interrupted.
        :type TotalInterruptTime: optional, any

        :param TotalActiveTime: Total active time the machine or process was
                                operational.
        :type TotalActiveTime: optional, any

        :param opc_endtimestamp: The timestamp marking the operation's
                                 conclusion or cut-off point.
        :type opc_endtimestamp: optional, any
        """
        self.opcID = opcID
        self.PA = PA
        self.PosNumber = PosNumber
        self.workplace = workplace
        self.dispatchdepartment = dispatchdepartment
        self.machine = machine
        self.AdhocChangeState = AdhocChangeState
        self.opc_state = opc_state
        self.opc_state_text = opc_state_text
        self.PlannedAmountPieces = PlannedAmountPieces
        self.ActualAmountPieces = ActualAmountPieces
        self.PlannedAmountBoards = PlannedAmountBoards
        self.ActualAmountBoards = ActualAmountBoards
        self.PlannedOperationTime = PlannedOperationTime
        self.ActualOperationTime = ActualOperationTime
        self.TotalInterruptTime = TotalInterruptTime
        self.TotalActiveTime = 0
        self.opc_endtimestamp = opc_endtimestamp
        self.next_step = next_step
        self.lastchangetimestamp = None

    def progress(self, sim_date):
        if self.lastchangetimestamp is None:
            self.lastchangetimestamp = sim_date
        self.TotalActiveTime += sim_date.difference(self.lastchangetimestamp)
        self.lastchangetimestamp = sim_date
        if self.TotalActiveTime >= self.PlannedOperationTime:
            self.mark_complete()

    def mark_complete(self, date: sim_clock = sim_clock(), machine = None):
        self.opc_state = 3
        self.opc_state_text = 'done'
        self.opc_endtimestamp = date.date
        self.machine = machine


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

    workplaces_data = np.unique(opcs_data[["WorkPlaceName"]].to_numpy().flatten())
    dispatchdepartments_data = np.unique(opcs_data[["Dispatchdepartment"]].to_numpy().flatten())

    dispatchdepartments = {}
    for dispatchdepartment in dispatchdepartments_data:
        dispatchdepartments[dispatchdepartment] = Dispatchdepartment(dispatchdepartment)

    workplaces = {}
    for workplace in workplaces_data:
        workplaces[workplace] = Workplace(workplace)

    opcs = {}
    opcs_by_PA = {}
    # generate and group opcs by PA
    for _, row in opcs_data.iterrows():
        obj = OperationCycle(*row)
        opcs[obj.opcID] = obj
        if row['PA'] not in opcs_by_PA:
            opcs_by_PA[row['PA']] = [obj]
        else:
            opcs_by_PA[row['PA']].append(obj)

    # generate all PA, reference opcs
    production_orders = {}
    for _, row in production_orders_data.iterrows():
        try:
            production_orders[row['PA']] = ProductionOrder(*row, operationcycles = opcs_by_PA[row['PA']])
        except KeyError as e:
            print(f'Could not find {row["PA"]} in opcs_by_PA')
            print(e)
            continue
        except Exception as e:
            print(f'Could not create ProductionOrder for {row["PA"]}')
            print(row)
            print(e)
            continue

    for pa in production_orders.keys():
        for opc in production_orders[pa].operationcycles:
            opc.next_step = production_orders[pa].operationcycles[production_orders[pa].operationcycles.index(opc)+1] if production_orders[pa].operationcycles.index(opc)+1 < len(production_orders[pa].operationcycles) else None

    for opc in opcs.values():
        try:
            opc.PA = production_orders[opc.PA]
        except KeyError as e:
            print(f'Could not find {opc.PA} in production_orders')
            print(e)
            continue
        try:
            opc.workplace = workplaces[opc.workplace]
        except KeyError as e:
            print(f'Could not find {opc.workplace} in workplaces')
            print(e)
            continue
        try:
            opc.dispatchdepartment = dispatchdepartments[opc.dispatchdepartment]
        except KeyError as e:
            print(f'Could not find {opc.dispatchdepartment} in dispatchdepartments')
            print(e)
            continue

    # create a mapping of dispatchdepartments and workplaces from opcs
    for opc in opcs.values():
        if opc.workplace and opc.dispatchdepartment and opc.workplace not in opc.dispatchdepartment.workplaces:
            opc.dispatchdepartment.workplaces.append(opc.workplace)

    # find active opc_id
    for pa in production_orders.keys():
        if production_orders[pa].FinishedDate: # skip all the finished PAs
            continue
        opcs_of_PA = opcs_by_PA[pa]
        for opc in reversed(opcs_of_PA): # go from the end of the list to prevent starting on a skipped opc
            if opc.opc_state!=0:
                production_orders[pa].current_step = opc
                production_orders[pa].next_step = opc.next_step
                break
        if production_orders[pa].current_step:
            if production_orders[pa].current_step.workplace:
                production_orders[pa].current_step.workplace.input_wip.append(production_orders[pa])

    print(f'Loading time elapsed: {timestamp() - t0}')
    return production_orders, opcs, workplaces, dispatchdepartments, opcs_by_PA
