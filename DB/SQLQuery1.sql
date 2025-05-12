CREATE DATABASE ConversationData;
GO
USE ConversationData;
GO

CREATE TABLE andritzButton_logs (
    Id INT PRIMARY KEY IDENTITY(1,1),
    userId NVARCHAR(100) NOT NULL,
    button NVARCHAR(100) NOT NULL,
    botTimeStamp DATETIME DEFAULT GETDATE()
);
