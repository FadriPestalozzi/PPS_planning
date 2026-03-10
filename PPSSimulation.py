from datetime import datetime, timedelta
from time import time as timestamp, sleep

import numpy as np
import pandas as pd

import plotting as plt

import dataloading as load

# ----------------------------
# Kapazitätstabelle
# Einheit = Aufträge pro Tag
# 80% von max. Kapazität
# ----------------------------
def update_capacity():
    """
    Updates the capacity data by retrieving it using SQL queries and saving it
    into a CSV file. The query is loaded from a SQL file and the output is
    saved with specified encoding and delimiter.

    :return: None
    """
    load.get_sql_data('./capa_per_day.sql').to_csv('capa_per_wpg.csv', index=False, encoding='utf-8', sep=';')


lookup_capa_per_day = pd.read_csv('./capa_per_wpg.csv', delimiter=';', encoding='UTF-8')
# lookup_capa_per_day = lookup_capa_per_day.set_index('Workplace')['MaxOPCs'].mul(0.8).to_dict()
lookup_capa_per_day = lookup_capa_per_day.set_index('Workplace')['Q3OPCs'].mul(1.0).to_dict()
lookup_parallel_per_day = pd.read_csv('./processingslots_per_workplace.csv', delimiter=';', encoding='UTF-8')
lookup_parallel_per_day = lookup_parallel_per_day.set_index('Workplace')['processing_slots'].to_dict()

# load a daily capacity of at least one opc per day
for key in lookup_capa_per_day.keys():
    if lookup_capa_per_day[key] < 1:
        lookup_capa_per_day[key] = 1

# ----------------------------
# Schichtzeiten
# ----------------------------
lookup_schichtzeiten_per_wp = pd.read_csv('./shiftmodell_per_workplace.csv', delimiter=';', encoding='UTF-8')
lookup_schichtzeiten_per_wp = lookup_schichtzeiten_per_wp.set_index('Workplace').apply(
    lambda row: [row["Morning"], row["Evening"], row["Night"], row["Day"]], axis=1).to_dict()


def time_based_simulation(production_orders, opcs, workplaces, dispatchdepartments,
                          logpath=f'./logs/log{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt',
                          steps=168):
    simtime = sim_clock()
    fig, [ax, ax2] = plt.initialize_plot()
    with open(logpath, 'a+', encoding='UTF-8') as f:
        f.write(f'Logfile for {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}\n')
        f.write('Dispatchlists:\n')
        for disp in dispatchdepartments.values():
            for wp in disp.workplaces:
                f.write(f'Workplace: {wp.name} has {len(wp.input_wip)} WIP\n')
                f.write(','.join([str(elem.PA) + ' ' + str(elem.current_step.opcID) + ' ' + str(
                    round(elem.current_step.TotalActiveTime, 2)) + '/' + str(
                    round(elem.current_step.PlannedOperationTime, 2)) for elem in wp.input_wip]) + '\n')
        f.write('\n')

        for step in range(steps):
            simtime.tick()
            plt.update_plot(fig, ax, ax2, dispatchdepartments, workplaces, simtime.string())
            with open(logpath, 'a+', encoding='UTF-8') as f:
                print(f'Step: {step}', simtime.date)
                f.write(f'Step: {step}, {simtime.date}\n')
                for disp in dispatchdepartments.values():
                    disp.run(simtime, f)
                # first process all wps, then ship them. Else process A, shipping to B then processing B results in PAs jumping multiple times in a sim day
                for disp in dispatchdepartments.values():
                    disp.ship_output_wip(simtime, f)
    plt.savefig(f'./finish.png')


def day_based_simulation(production_orders, opcs, workplaces, dispatchdepartments,
                          logpath=f'./logs/log{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt',steps=21):
    simtime = sim_clock()
    fig, [ax, ax2] = plt.initialize_plot(dispatchdepartments, workplaces)
    with open(logpath, 'a+', encoding='UTF-8') as f:
        f.write(f'Logfile for {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}\n')
        f.write('Dispatchlists:\n')
        for disp in dispatchdepartments.values():
            for wp in disp.workplaces:
                f.write(f'Workplace: {wp.name} has {len(wp.input_wip)} WIP\n')
                f.write(','.join([str(elem.PA) + ' ' + str(elem.current_step.opcID) for elem in wp.input_wip]) + '\n')
        f.write('\n')

        for step in range(steps):
            simtime.next_day()
            plt.update_plot(fig, ax, ax2, dispatchdepartments, workplaces, simtime.string())
            with open(logpath, 'a+', encoding='UTF-8') as f:
                print(f'Step: {step}', simtime.date)
                f.write(f'Step: {step}, {simtime.date}\n')
                for disp in dispatchdepartments.values():
                    disp.step(f)
                # first process all wps, then ship them. Else process A, shipping to B then processing B results in PAs jumping multiple times in a sim day
                for disp in dispatchdepartments.values():
                    disp.ship_output_wip(simtime, f)


    def update(step=0):
        with open(logpath, 'a+', encoding='UTF-8') as f:
            f.write(f'Step: {step} \n')
            for disp in dispatchdepartments.values():
                disp.step(logfile=f)
            # first process all wps, then ship them. Else process A, shipping to B then processing B results in PAs jumping multiple times in a sim day
            for disp in dispatchdepartments.values():
                disp.ship_output_wip(logfile=f)

        # updating the graph
        heights = [sum([len(workplaces[wp.name].input_wip) for wp in dispatchdepartments[disp].workplaces]) for disp in
                   dispatchdepartments.keys()]
        ax.cla()
        ax.bar(names, heights)
        ax.set_xlabel("Dispatch Department")
        ax.set_ylabel("WIP in PA")
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_ylim(0, 150)
        ax2.bar(['fertig'], [len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp == 'Abschlussbuchung'])
        sleep(.2)
        plt.title('Tag ' + str(step))
        plt.draw()
        plt.pause(0.001)


        plt.savefig(f'./finish.png')


class sim_clock():
    def __init__(self, date=datetime.today(), hour=datetime.now().hour):
        self.date = date.replace(hour=hour, minute=0, second=0, microsecond=0)

    def next_day(self, delta=1):
        self.date += timedelta(days=delta)
        return self.date

    def tick(self, delta=1):
        self.date += timedelta(hours=delta)

    def difference(self, other_date):
        # datetime defines the difference of timestamp(n+1) - timestamp(n) as -1hour, hence the negative sign
        return -round((other_date.date - self.date).total_seconds() / 3600, 0)

    def string(self):
        return self.date.strftime("%Y-%m-%d_%H-%M-%S")

    def copy(self):
        b = type(self).__new__(type(self))
        b.__dict__.update(self.__dict__)
        return b


class Workplace:
    def __init__(self, name, capa_per_day=None, parallel_processes=None):
        self.name = name
        self.location = None
        if capa_per_day is None:
            self.load_capa_from_file()
        else:
            self.capa_per_day = capa_per_day  # use the floor of capa_per_day
        if parallel_processes is None:
            self.load_parallel_from_file()
        else:
            self.parallel_processes = parallel_processes  # use the floor of capa_per_day
        self.input_wip: list[ProductionOrder] = []
        self.output_wip: list[ProductionOrder] = []

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

    def run(self, date=sim_clock(), logfile=None):
        """
        Process work-in-progress items according to workplace capacity.

        Moves items from input queue to output queue based on the daily capacity limit.
        Input queue is updated to remove processed items.

        Returns:
            None
        """
        for wp in self.workplaces:
            if wp.parallel_processes is None:
                raise Exception('No parallel processing defined for workplace')
            if type(wp.parallel_processes) is not int:
                wp.parallel_processes = int(wp.parallel_processes)
            # Progress up to parallel_processes items from input to output
            # process the whole wip if parallel places exist, else only the first couple
            if len(wp.input_wip) < wp.parallel_processes:
                for pa in wp.input_wip:
                    pa.current_step.progress(date, logfile=logfile)
            else:
                for pa in wp.input_wip[:wp.parallel_processes]:
                    pa.current_step.progress(date, logfile=logfile)
            # now check all finished opcs and move them to output_wip
            for pa in wp.input_wip:
                # if logfile:
                # logfile.write(f'{wp.name} {pa.PA} ( {round(pa.current_step.TotalActiveTime,2)} / {round(pa.current_step.PlannedOperationTime,2)})\n')
                if pa.current_step.opc_state == 3:
                    # if logfile:
                    #     logfile.write(f'{wp.name} {pa.PA} {pa.current_step.PosNumber} was finished at {date.date} and is shipped from {pa.current_step.workplace.name} to {pa.next_step.workplace.name if pa.next_step else 'None' }\n')
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

    def step(self, logfile=None):
        for wp in self.workplaces:
            if wp.capa_per_day is None:
                return Exception('No Capacity defined for Workplace')
            if type(wp.capa_per_day) is not int:
                wp.capa_per_day = int(wp.capa_per_day)
                # Convert up to capa_per_day items from input to output
            wp.output_wip = list(wp.input_wip)[:wp.capa_per_day]
            wp.input_wip = list(wp.input_wip)[wp.capa_per_day:]
            if logfile:
                logfile.write(f'{wp.name} has {len(wp.output_wip)} finished PAs\n')
                logfile.write(','.join([str(elem.PA) + ' ' + str(elem.current_step.opcID) for elem in wp.output_wip]) + '\n')

    def ship_output_wip(self, date=sim_clock(), logfile=None):
        for wp in self.workplaces:
            if len(wp.output_wip) < 1:
                break
            for pa in wp.output_wip:
                if pa.next_step is None:
                    pa.FinishedDate = date.date
                    break
                pa.next_step.workplace.input_wip.append(pa)
            wp.output_wip = []

    def run_and_ship(self, date=sim_clock()):
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

        :param operationcycles: List of operation cycles associated with this production order
        """
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
    Represents an operational cycle, encapsulating data about planned and
    actual production performance, operational states, progress tracking,
    and timestamps.

    Provides mechanisms to monitor and update the progress of an operation
    against planned metrics. Tracks active states, interruptions, and the
    completion status of the operation, allowing for comprehensive insights
    into the efficiency and performance of processes.

    :ivar opcID: Unique identifier for the operation cycle instance.
    :type opcID: any
    :ivar PA: Planned activity related to this operation.
    :type PA: any
    :ivar PosNumber: Position or serial number of the operation instance.
    :type PosNumber: any
    :ivar workplace: Workplace or station associated with the operation cycle.
    :type workplace: any
    :ivar dispatchdepartment: Department responsible for dispatching associated tasks.
    :type dispatchdepartment: any
    :ivar machine: The machine associated with this operation.
    :type machine: any
    :ivar AdhocChangeState: Indicator of any ad-hoc state changes during operation.
    :type AdhocChangeState: any
    :ivar opc_state: Numeric or coded state of the operation (e.g., running, complete).
    :type opc_state: any
    :ivar opc_state_text: Descriptive state of the operation.
    :type opc_state_text: any
    :ivar PlannedAmountPieces: Number of units planned to be produced.
    :type PlannedAmountPieces: any
    :ivar ActualAmountPieces: Actual number of units produced.
    :type ActualAmountPieces: any
    :ivar PlannedAmountBoards: Number of boards planned for production.
    :type PlannedAmountBoards: any
    :ivar ActualAmountBoards: Actual number of boards produced.
    :type ActualAmountBoards: any
    :ivar PlannedOperationTime: Total time planned for the operation.
    :type PlannedOperationTime: any
    :ivar ActualOperationTime: Total time actually spent during the operation.
    :type ActualOperationTime: any
    :ivar TotalInterruptTime: Total duration of interruptions during the operation.
    :type TotalInterruptTime: any
    :ivar TotalActiveTime: Accumulated active processing time during the operation.
    :type TotalActiveTime: int
    :ivar opc_endtimestamp: Timestamp marking the conclusion of this operation cycle.
    :type opc_endtimestamp: any
    :ivar next_step: Next step or operational process to follow this cycle.
    :type next_step: any
    :ivar lastchangetimestamp: Timestamp of the last recorded state or time change.
    :type lastchangetimestamp: any
    """

    def __init__(self, PA=None, PosNumber=None, opcID=None, workplace=None,
                 dispatchdepartment=None, machine=None, AdhocChangeState=None,
                 opc_state=None, opc_state_text=None, PlannedAmountPieces=None,
                 ActualAmountPieces=None, PlannedAmountBoards=None,
                 ActualAmountBoards=None, PlannedOperationTime=None,
                 ActualOperationTime=None, TotalInterruptTime=None,
                 TotalActiveTime=None, opc_endtimestamp=None, next_step=None):
        """
        Initializes an instance of the class with various parameters to represent
        and manage operational data attributes.

        :param PA: Optional; Represents the process area for the operational data.
        :param PosNumber: Optional; Position number indicating the specific aspect
                          of the operation.
        :param opcID: Optional; Unique identifier for the OPC (OLE for Process
                      Control) operation.
        :param workplace: Optional; Specifies the workplace or location associated
                          with the operation.
        :param dispatchdepartment: Optional; Indicates the dispatch department
                                   handling the operation.
        :param machine: Optional; Represents the machine involved in the process.
        :param AdhocChangeState: Optional; Defines status changes that occur ad hoc
                                 in the operation.
        :param opc_state: Optional; Holds the OPC state code indicating the
                          operational status.
        :param opc_state_text: Optional; Descriptive text of the OPC state for
                               more readability.
        :param PlannedAmountPieces: Optional; Denotes the planned number of pieces
                                     to be processed.
        :param ActualAmountPieces: Optional; Denotes the actual number of pieces
                                    processed.
        :param PlannedAmountBoards: Optional; Represents the planned number of
                                     boards for the operation.
        :param ActualAmountBoards: Optional; Represents the actual number of
                                    boards processed.
        :param PlannedOperationTime: Optional; Duration planned for the operation
                                      in a time format.
        :param ActualOperationTime: Optional; Actual duration the operation took
                                     in a time format.
        :param TotalInterruptTime: Optional; Total downtime or interrupt time
                                   experienced during the operation.
        :param TotalActiveTime: Optional; Represents the total active time compiled
                                during the operation. Defaults to zero.
        :param opc_endtimestamp: Optional; Timestamp indicating the moment the
                                 operation ended.
        :param next_step: Optional; The next step or operation to be processed
                          after completion of the current one.
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

    def progress(self, sim_date, logfile=None):
        if self.lastchangetimestamp is None:
            self.lastchangetimestamp = sim_date.copy()
        self.TotalActiveTime += sim_date.difference(self.lastchangetimestamp)
        if logfile:
            logfile.write('progress ' + ' '.join(
                ['PA', str(self.PA.PA), 'opc', str(self.opcID), 'workplace', str(self.workplace.name),
                 'TotalActiveTime', str(self.TotalActiveTime), 'PlannedOperationTime',
                 str(self.PlannedOperationTime), 'lastchangetimestamp', str(self.lastchangetimestamp.date), 'sim_date',
                 str(sim_date.date), 'difference', str(sim_date.difference(
                    self.lastchangetimestamp)), '\n']))
        self.lastchangetimestamp = sim_date.copy()
        if self.TotalActiveTime >= self.PlannedOperationTime:
            self.mark_complete()
        return

    def mark_complete(self, date: sim_clock = sim_clock(), machine=None):
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
            production_orders[row['PA']] = ProductionOrder(*row, operationcycles=opcs_by_PA[row['PA']])
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
            opc.next_step = production_orders[pa].operationcycles[
                production_orders[pa].operationcycles.index(opc) + 1] if production_orders[pa].operationcycles.index(
                opc) + 1 < len(production_orders[pa].operationcycles) else None

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
        if production_orders[pa].FinishedDate:  # skip all the finished PAs
            continue
        opcs_of_PA = opcs_by_PA[pa]
        for opc in reversed(opcs_of_PA):  # go from the end of the list to prevent starting on a skipped opc
            if opc.opc_state != 0:
                production_orders[pa].current_step = opc
                production_orders[pa].next_step = opc.next_step
                break
        if production_orders[pa].current_step:
            if production_orders[pa].current_step.workplace:
                production_orders[pa].current_step.workplace.input_wip.append(production_orders[pa])

    print(f'Loading time elapsed: {timestamp() - t0}')
    return production_orders, opcs, workplaces, dispatchdepartments, opcs_by_PA
