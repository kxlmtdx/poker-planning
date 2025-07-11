USE [PlanningPoker]
GO
/****** Object:  UserDefinedFunction [dbo].[CalculateMedianEstimate]    Script Date: 05.06.2025 21:27:12 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- Создаем функцию для расчета медианной оценки
CREATE FUNCTION [dbo].[CalculateMedianEstimate](@IssueId UNIQUEIDENTIFIER)
RETURNS DECIMAL(10, 2)
AS
BEGIN
    DECLARE @MedianEstimate DECIMAL(10, 2);
    DECLARE @Estimates TABLE (Estimate DECIMAL(10, 2), RowNum INT);
    
    INSERT INTO @Estimates (Estimate, RowNum)
    SELECT Estimate, ROW_NUMBER() OVER (ORDER BY Estimate)
    FROM Votes
    WHERE IssueId = @IssueId AND IsCurrent = 1;
    
    DECLARE @Count INT = (SELECT COUNT(*) FROM @Estimates);
    
    IF @Count = 0
        SET @MedianEstimate = NULL;
    ELSE IF @Count % 2 = 1
        SELECT @MedianEstimate = Estimate 
        FROM @Estimates 
        WHERE RowNum = (@Count + 1) / 2;
    ELSE
        SELECT @MedianEstimate = AVG(Estimate)
        FROM @Estimates
        WHERE RowNum IN (@Count / 2, @Count / 2 + 1);
    
    RETURN @MedianEstimate;
END;
GO
/****** Object:  Table [dbo].[Users]    Script Date: 05.06.2025 21:27:12 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
	[UserId] [bigint] NOT NULL,
	[Username] [nvarchar](100) NULL,
	[FirstName] [nvarchar](100) NULL,
	[LastName] [nvarchar](100) NULL,
	[IsScrumMaster] [bit] NULL,
	[RegistrationDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Votes]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Votes](
	[VoteId] [uniqueidentifier] NOT NULL,
	[IssueId] [uniqueidentifier] NULL,
	[UserId] [bigint] NULL,
	[Estimate] [decimal](10, 2) NOT NULL,
	[VoteDate] [datetime] NULL,
	[IsCurrent] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[VoteId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[CurrentVotes]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- Create a view to get current votes for an issue
CREATE VIEW [dbo].[CurrentVotes] AS
SELECT 
    v.VoteId,
    v.IssueId,
    v.UserId,
    u.Username,
    u.FirstName,
    u.LastName,
    v.Estimate,
    v.VoteDate
FROM 
    Votes v
JOIN 
    Users u ON v.UserId = u.UserId
WHERE 
    v.IsCurrent = 1;
GO
/****** Object:  Table [dbo].[Issues]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Issues](
	[IssueId] [uniqueidentifier] NOT NULL,
	[SessionId] [uniqueidentifier] NULL,
	[Title] [nvarchar](500) NOT NULL,
	[Description] [nvarchar](max) NULL,
	[CreatedBy] [bigint] NULL,
	[CreationDate] [datetime] NULL,
	[Status] [nvarchar](20) NULL,
	[FinalEstimate] [decimal](10, 2) NULL,
	[FinalizedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[IssueId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  View [dbo].[GetSessionSummary]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- Пересоздаем представление с исправленной функцией
CREATE VIEW [dbo].[GetSessionSummary] AS
SELECT 
    i.IssueId,
    i.Title,
    i.Status,
    i.FinalEstimate,
    COUNT(v.VoteId) AS VoteCount,
    AVG(v.Estimate) AS AverageEstimate,
    dbo.CalculateMedianEstimate(i.IssueId) AS MedianEstimate
FROM 
    Issues i
LEFT JOIN 
    Votes v ON i.IssueId = v.IssueId AND v.IsCurrent = 1
GROUP BY 
    i.IssueId, i.Title, i.Status, i.FinalEstimate;
GO
/****** Object:  Table [dbo].[GoogleSheetExports]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GoogleSheetExports](
	[ExportId] [uniqueidentifier] NOT NULL,
	[SessionId] [uniqueidentifier] NULL,
	[SpreadsheetId] [nvarchar](200) NULL,
	[SheetUrl] [nvarchar](500) NULL,
	[ExportDate] [datetime] NULL,
	[Status] [nvarchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[ExportId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GroupMembers]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GroupMembers](
	[GroupId] [bigint] NOT NULL,
	[UserId] [bigint] NOT NULL,
	[JoinDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[GroupId] ASC,
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Groups]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Groups](
	[GroupId] [bigint] NOT NULL,
	[GroupName] [nvarchar](200) NULL,
	[CreatedBy] [bigint] NULL,
	[CreationDate] [datetime] NULL,
	[IsActive] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[GroupId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Results]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Results](
	[ResultId] [uniqueidentifier] NOT NULL,
	[SessionId] [uniqueidentifier] NULL,
	[ResultData] [nvarchar](max) NOT NULL,
	[GeneratedDate] [datetime] NULL,
	[SentToMaster] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[ResultId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Sessions]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Sessions](
	[SessionId] [uniqueidentifier] NOT NULL,
	[GroupId] [bigint] NULL,
	[CreatedBy] [bigint] NULL,
	[StartDate] [datetime] NULL,
	[EndDate] [datetime] NULL,
	[Status] [nvarchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[SessionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[VoteHistory]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[VoteHistory](
	[HistoryId] [uniqueidentifier] NOT NULL,
	[VoteId] [uniqueidentifier] NULL,
	[PreviousEstimate] [decimal](10, 2) NULL,
	[NewEstimate] [decimal](10, 2) NOT NULL,
	[ChangeDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[HistoryId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebSocketConnections]    Script Date: 05.06.2025 21:27:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebSocketConnections](
	[ConnectionId] [nvarchar](100) NOT NULL,
	[UserId] [bigint] NULL,
	[SessionId] [uniqueidentifier] NULL,
	[ConnectionDate] [datetime] NULL,
	[LastActivity] [datetime] NULL,
	[IsActive] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[ConnectionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[GoogleSheetExports] ADD  DEFAULT (newid()) FOR [ExportId]
GO
ALTER TABLE [dbo].[GoogleSheetExports] ADD  DEFAULT (getdate()) FOR [ExportDate]
GO
ALTER TABLE [dbo].[GoogleSheetExports] ADD  DEFAULT ('Pending') FOR [Status]
GO
ALTER TABLE [dbo].[GroupMembers] ADD  DEFAULT (getdate()) FOR [JoinDate]
GO
ALTER TABLE [dbo].[Groups] ADD  DEFAULT (getdate()) FOR [CreationDate]
GO
ALTER TABLE [dbo].[Groups] ADD  DEFAULT ((1)) FOR [IsActive]
GO
ALTER TABLE [dbo].[Issues] ADD  DEFAULT (newid()) FOR [IssueId]
GO
ALTER TABLE [dbo].[Issues] ADD  DEFAULT (getdate()) FOR [CreationDate]
GO
ALTER TABLE [dbo].[Issues] ADD  DEFAULT ('Pending') FOR [Status]
GO
ALTER TABLE [dbo].[Results] ADD  DEFAULT (newid()) FOR [ResultId]
GO
ALTER TABLE [dbo].[Results] ADD  DEFAULT (getdate()) FOR [GeneratedDate]
GO
ALTER TABLE [dbo].[Results] ADD  DEFAULT ((0)) FOR [SentToMaster]
GO
ALTER TABLE [dbo].[Sessions] ADD  DEFAULT (newid()) FOR [SessionId]
GO
ALTER TABLE [dbo].[Sessions] ADD  DEFAULT (getdate()) FOR [StartDate]
GO
ALTER TABLE [dbo].[Sessions] ADD  DEFAULT ('Active') FOR [Status]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT ((0)) FOR [IsScrumMaster]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT (getdate()) FOR [RegistrationDate]
GO
ALTER TABLE [dbo].[VoteHistory] ADD  DEFAULT (newid()) FOR [HistoryId]
GO
ALTER TABLE [dbo].[VoteHistory] ADD  DEFAULT (getdate()) FOR [ChangeDate]
GO
ALTER TABLE [dbo].[Votes] ADD  DEFAULT (newid()) FOR [VoteId]
GO
ALTER TABLE [dbo].[Votes] ADD  DEFAULT (getdate()) FOR [VoteDate]
GO
ALTER TABLE [dbo].[Votes] ADD  DEFAULT ((1)) FOR [IsCurrent]
GO
ALTER TABLE [dbo].[WebSocketConnections] ADD  DEFAULT (getdate()) FOR [ConnectionDate]
GO
ALTER TABLE [dbo].[WebSocketConnections] ADD  DEFAULT (getdate()) FOR [LastActivity]
GO
ALTER TABLE [dbo].[WebSocketConnections] ADD  DEFAULT ((1)) FOR [IsActive]
GO
ALTER TABLE [dbo].[GoogleSheetExports]  WITH CHECK ADD FOREIGN KEY([SessionId])
REFERENCES [dbo].[Sessions] ([SessionId])
GO
ALTER TABLE [dbo].[GroupMembers]  WITH CHECK ADD FOREIGN KEY([GroupId])
REFERENCES [dbo].[Groups] ([GroupId])
GO
ALTER TABLE [dbo].[GroupMembers]  WITH CHECK ADD FOREIGN KEY([UserId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[Groups]  WITH CHECK ADD FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[Issues]  WITH CHECK ADD FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[Issues]  WITH CHECK ADD FOREIGN KEY([SessionId])
REFERENCES [dbo].[Sessions] ([SessionId])
GO
ALTER TABLE [dbo].[Results]  WITH CHECK ADD FOREIGN KEY([SessionId])
REFERENCES [dbo].[Sessions] ([SessionId])
GO
ALTER TABLE [dbo].[Sessions]  WITH CHECK ADD FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[Sessions]  WITH CHECK ADD FOREIGN KEY([GroupId])
REFERENCES [dbo].[Groups] ([GroupId])
GO
ALTER TABLE [dbo].[VoteHistory]  WITH CHECK ADD FOREIGN KEY([VoteId])
REFERENCES [dbo].[Votes] ([VoteId])
GO
ALTER TABLE [dbo].[Votes]  WITH CHECK ADD FOREIGN KEY([IssueId])
REFERENCES [dbo].[Issues] ([IssueId])
GO
ALTER TABLE [dbo].[Votes]  WITH CHECK ADD FOREIGN KEY([UserId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[WebSocketConnections]  WITH CHECK ADD FOREIGN KEY([SessionId])
REFERENCES [dbo].[Sessions] ([SessionId])
GO
ALTER TABLE [dbo].[WebSocketConnections]  WITH CHECK ADD FOREIGN KEY([UserId])
REFERENCES [dbo].[Users] ([UserId])
GO
