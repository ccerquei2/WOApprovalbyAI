# WOApprovalbyAI

This project automates work order approvals using machine learning models and language model agents.

## Database logging

The logger reads database connection settings via `ConfigLoader` and uses decrypted credentials. All runtime events are written to the `dbo.AIWOApproval` table.

```sql
CREATE TABLE dbo.AIWOApproval (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Timestamp DATETIME2(3) NOT NULL  DEFAULT SYSUTCDATETIME(),
    LogLevel  VARCHAR(10)   NOT NULL,
    Step      VARCHAR(100)  NOT NULL,
    [Order]   FLOAT         NULL,
    Seq_Key   FLOAT         NULL,
    ExecutionId UNIQUEIDENTIFIER NOT NULL,
    Phase            VARCHAR(50)  NULL,
    ModelName        VARCHAR(100) NULL,
    ModelVersion     VARCHAR(20)  NULL,
    ModelProbability FLOAT        NULL,
    Decision         VARCHAR(20)  NULL,
    APIName          VARCHAR(50)  NULL,
    APIEndpoint      VARCHAR(255) NULL,
    StatusCode       INT          NULL,
    ResponseMs       INT          NULL,
    RetryCount       SMALLINT     NULL,
    Message          VARCHAR(MAX) NOT NULL,
    ErrorDetails     VARCHAR(MAX) NULL,
    HostMachine      VARCHAR(100) NOT NULL DEFAULT HOST_NAME(),
    UserName         VARCHAR(50)  NOT NULL DEFAULT SUSER_SNAME()
);
```
