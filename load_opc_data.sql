SELECT
   opc.ProductionOrder as PA
   ,opc.PosNumber
   ,opc.ID as opcID
   ,wp.Name as WorkPlaceName
   ,dp.Name as Dispatchdepartment
   ,m.Name as Machine
   ,opc.AdhocChangeState
   ,opc.State as opc_state
   ,Case opc.State
		When 0 Then 'not started'
		When 1 Then 'on-going'
		When 2 Then 'stopped'
		When 3 Then 'done'
	End as opc_state_text
   ,opc.PlannedAmountPieces
   ,opc.ActualAmountPieces
   ,opc.PlannedAmountBoards
   ,opc.ActualAmountBoards
   ,opc.PlannedOperationTime
   ,opc.ActualOperationTime
   ,opc.InterruptTime as TotalInterruptTime
   ,opc.ProcessTime as TotalActiveTime
   ,b.Timestamp as opc_endtimestamp
FROM Operationcycles opc With (NoLock)
inner join Workplaces wp With (NoLock) on opc.CostCenterNumber = wp.Number and IsWPG=1
inner join DispatchDepartments dp With (NoLock) on wp.DispatchDepartmentID = dp.ID
left join Bookings b With (NoLock) on b.OperationCycleID = opc.ID and b.Cancel<>1 and b.Type=2
left join Machines m With (NoLock) on b.MachineID = m.PK_MachinesID
Where ProductionOrder in (Select Number from ProductionOrders With (NoLock) where StartDate> GETDATE()-365 or FinishedDate is NULL)
Order by PA, PosNumber;

/*
load data columns
- OPC OperationCycleID
- WPG WorkPlaceGroup


DPE_OPC States
0 = not started / 1 = ongonig / 2 = stopped / 3 = done
*/