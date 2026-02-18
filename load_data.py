########## import the following columns based on load_data.sql
# WA
# PA
# Customer
# Product
# Revision
# Version
# Start AS PcsStart
# Actual AS PcsActual
# Target AS PcsTarget
# StartDate AS WAStartDate
# DueDate AS WADueDate
# ForecastDate AS WAForecastDate
# ActualPosition
# State
# DisplayState
# CurrentAmountPanels
# LastPosition
# LastCC	NextCC	OperationCount	OpcID	OrderType	PlanNumber	ResponsibleEngineer	ResponsibleInterrupt	VBT	VBTDescription	PPS	PPSDescription	Priority	PlannedOperationTime	Solderresist	LastEndBooking	ADHCStatus	InterruptShortName	Workplace	LastGrindingAvailable	Technology	PrismaCostCenter	
# CostCenterNumber	ConfirmedDate	Delta	Info1	Info2	InterruptText	Department	DepartmentID	Responsible	PpsInfo	PpsDate	ArDelta	PosDoneDate	PhaseCode	PhaseCat	CurrentMachineName	SapOrderType	PPSAdminDate	PPSAdminDescription	WorkPackageCapacityCountSum	WorkPackageCapacityCountOpenSum	WorkPackageCapacityCountDoneSum	WorkPackageCapacityCountPercentage	FinishedWorkTime	OrderBackLogPercentage	WorkTimeProgressPercentage	OrderBackLogAssignedMainOrder	OrderBackLogForecastEnd	OrderBackLogForecastDays	RemainingProcessTime	RemainingWorkTime	ProcessingTime	LastBookingTime	LastEndBookingTime	FinishedProcessTime	ActualCCName	LastCCName	NextCCName	LastMachines	ProcessChain	DeliveryForecastPpsDate	DeliveryCriticalityPpsBool	OriginalDeliveryForecastPpsDate	SetupTime	LastChangedOn	ID	ProductionOrderID	PosNumber	Predecessor	CostCenterNumber	PlannedAmountPieces	PlannedAmountBoards	PlannedOperationTime	State	DisplayState	ActualAmountPieces	ActualAmountBoards	ActualOperationTime	PlannedEndDate	CR	
# WPG_ID	ProductionOrder	AdhocChangeState	ChangeID	SAPSyncState	DWHSyncState	BufferTime	ProcessTime	InterruptTime	Info1	Info2	MC_Booked	MrbStateSuspend	MrbStateSuspendText	ModifiedDate	MrbRevisionId	InfoLink

import numpy as np
import pandas as pd

