from collections import deque, defaultdict

import pandas as pd

# ----------------------------
# Kapazitätstabelle
# Einheit = Aufträge pro Tag
# 80% von max. Kapazität
# ----------------------------
lookup_capa_per_day = pd.read_csv('./capa_per_day.csv', delimiter='\t')
lookup_capa_per_day = lookup_capa_per_day.set_index('CostCenterName')['Maximum'].mul(0.8).to_dict()

class Workplace:
    def __init__(self, name, capa_per_day):
        self.name = name
        self.location = None
        self.capa_per_day = capa_per_day
        self.input_wip = deque()
        self.output_wip = deque()

    def run(self):
        """
        Process work-in-progress items according to workplace capacity.

        Moves items from input queue to output queue based on the daily capacity limit.
        Input queue is updated to remove processed items.

        Returns:
            None
        """
        # Convert up to capa_per_day items from input to output
        self.output_wip = deque(list(self.input_wip)[:self.capa_per_day])
        self.input_wip = deque(list(self.input_wip)[self.capa_per_day:])
        return None

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
                 id=None,
                 operationcycles=None,
                 current_step=None,
                 current_dispatchdep=None,
                 next_step=None,
                 next_dispatchdep=None,
                 age=None,
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
                 DeliveryCriticalityPpsBool=None):
        """
        Initialize a new ProductionOrder instance.

        :param id: Unique identifier for the production order
        :param operationcycles: List of operation cycles associated with this production order
        """
        self.id = id
        self.operationcycles = operationcycles
        self.current_step = current_step
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
    :ivar Dispatchdepartment: Department responsible for dispatching the work.
    :ivar Machine: Identification or name of the machine involved in the cycle.
    :ivar AdhocChangeState: Indicates if an ad-hoc change is applied to the cycle state.
    :ivar opc_state: Numeric representation of the operational cycle's state.
    :ivar opc_state_text: Text description of the operational cycle's state.
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
    def __init__(self, PA=None, PosNumber=None, opcID=None, WorkPlaceName=None,
                 Dispatchdepartment=None, Machine=None, AdhocChangeState=None,
                 opc_state=None, opc_state_text=None, PlannedAmountPieces=None,
                 ActualAmountPieces=None, PlannedAmountBoards=None,
                 ActualAmountBoards=None, PlannedOperationTime=None,
                 ActualOperationTime=None, TotalInterruptTime=None,
                 TotalActiveTime=None, opc_endtimestamp=None):
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

        :param Dispatchdepartment: Department responsible for dispatching related
                                   processes or tasks.
        :type Dispatchdepartment: optional, any

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
        self.WorkPlaceName = WorkPlaceName
        self.Dispatchdepartment = Dispatchdepartment
        self.Machine = Machine
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
        self.TotalActiveTime = TotalActiveTime
        self.opc_endtimestamp = opc_endtimestamp