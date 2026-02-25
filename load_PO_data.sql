SELECT
	  po.[Number] as PA
      ,p.Number as ProductNumber
	  ,p.Version as ProductVersion
	  ,p.Revision as ProductRevision
      ,[PlanNumber]
	  ,NameDE as PhasenCode
      ,[PiecesPerBoard]
      ,[TargetAmount]
      ,[Customer]
      ,[StartDate]
      ,[FinishedDate]
      --,[Delta] as ARDelta_PPS
      ,[PPSAdminDate]
      ,[SapOrderType]
      ,[IsDeleted]
      ,[DeliveryForecastPpsDate]
      ,[DeliveryCriticalityPpsBool]
  FROM [ProductionOrders] po with (NoLock)
  inner join Products p with (NoLock) on ProductID = p.ID
  inner join DWH_Dyconex.global.Enumerations AS ge with (NoLock) on ge.ValueInt=[PhaseCode] and GroupNumber=1
  Where po.[Number] in (Select Number from ProductionOrders With (NoLock) where StartDate> GETDATE()-365 or FinishedDate is NULL)
  order by PA;