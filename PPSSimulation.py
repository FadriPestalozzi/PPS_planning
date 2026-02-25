from collections import deque

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

        :return:
        """
        self.output_wip = self.input_wip[:self.capa_per_day]
        self.input_wip =  self.input_wip[self.capa_per_day:]
        return None

class ProductionOrder:
    def __init__(self, id, operationcycles):
        self.id = id
        self.operationcycles = operationcycles
        self.current_step = 10
        self.current_dispatchdep = None
        self.next_step = 0
        self.next_dispatchdep = None
        self.age = 0


class OperationCycle:
    def __init__(self, PA, PosNumber, opcID, WorkPlaceName, Dispatchdepartment, Machine, AdhocChangeState, opc_state, opc_state_text, PlannedAmountPieces, ActualAmountPieces, PlannedAmountBoards, ActualAmountBoards, PlannedOperationTime, ActualOperationTime, TotalInterruptTime, TotalActiveTime, opc_endtimestamp):
        self.PA = PA
        self.PosNumber = PosNumber
        self.opcID = opcID
        self.WorkPlaceName = WorkPlaceName
        self.Dispatchdepartment = Dispatchdepartment
        self.Machine = Machine
        self.AdhocChangeState = AdhocChangeState
        self.opc_state = opc_state
        self.opc_state_text = opc_state_text
        self.PlannedAmountPieces = PlannedAmountPieces
        self.ActualAmountPieces =
        self.PlannedAmountBoards =
        self.ActualAmountBoards =
        self.PlannedOperationTime =
        self.ActualOperationTime =
        self.TotalInterruptTime =
        self.TotalActiveTime =
        self.opc_endtimestamp =