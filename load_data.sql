/*
load data columns
- OPC OperationCycleID
- WPG WorkPlaceGroup

DPE_OPC States 
0 = not started / 1 = ongonig / 2 = stopped / 3 = done
*/

SELECT TOP (100000) *
FROM [DycoPlanEx].[dbo].[BF_DispatchList] AS DPE_DL
INNER JOIN [DycoPlanEx].[dbo].[Operationcycles] AS DPE_OPC
	ON DPE_OPC.ProductionOrder = DPE_DL.PA
ORDER BY WA DESC

/*
column names loaded

	WA	PA	Customer	Product	ProductDescription	Revision	Version	Start	Actual	Target	StartDate	DueDate	ForecastDate	ActualPosition	ActualCC	DependentCC	CR	CRNew	State	DisplayState	CurrentAmountPanels	LastPosition	LastCC	NextCC	OperationCount	OpcID	OrderType	PlanNumber	ResponsibleEngineer	ResponsibleInterrupt	VBT	VBTDescription	PPS	PPSDescription	Priority	PlannedOperationTime	Solderresist	LastEndBooking	ADHCStatus	InterruptShortName	Workplace	LastGrindingAvailable	Technology	PrismaCostCenter	CostCenterNumber	ConfirmedDate	Delta	Info1	Info2	InterruptText	Department	DepartmentID	Responsible	PpsInfo	PpsDate	ArDelta	PosDoneDate	PhaseCode	PhaseCat	CurrentMachineName	SapOrderType	PPSAdminDate	PPSAdminDescription	WorkPackageCapacityCountSum	WorkPackageCapacityCountOpenSum	WorkPackageCapacityCountDoneSum	WorkPackageCapacityCountPercentage	FinishedWorkTime	OrderBackLogPercentage	WorkTimeProgressPercentage	OrderBackLogAssignedMainOrder	OrderBackLogForecastEnd	OrderBackLogForecastDays	RemainingProcessTime	RemainingWorkTime	ProcessingTime	LastBookingTime	LastEndBookingTime	FinishedProcessTime	ActualCCName	LastCCName	NextCCName	LastMachines	ProcessChain	DeliveryForecastPpsDate	DeliveryCriticalityPpsBool	OriginalDeliveryForecastPpsDate	SetupTime	LastChangedOn	ID	ProductionOrderID	PosNumber	Predecessor	CostCenterNumber	PlannedAmountPieces	PlannedAmountBoards	PlannedOperationTime	State	DisplayState	ActualAmountPieces	ActualAmountBoards	ActualOperationTime	PlannedEndDate	CR	WPG_ID	ProductionOrder	AdhocChangeState	ChangeID	SAPSyncState	DWHSyncState	BufferTime	ProcessTime	InterruptTime	Info1	Info2	MC_Booked	MrbStateSuspend	MrbStateSuspendText	ModifiedDate	MrbRevisionId	InfoLink

*/




