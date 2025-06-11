import os
import uuid
import logging
import traceback
import pyodbc
from contextlib import ContextDecorator


def new_execution():
    """Return a new execution UUID."""
    return uuid.uuid4()


class DBLogger:
    """Logger that writes records to SQL Server."""

    INSERT_SQL = (
        "INSERT INTO dbo.AIWOApproval ("
        "LogLevel, Step, [Order], Seq_Key, ExecutionId, Phase, "
        "ModelName, ModelVersion, ModelProbability, Decision, "
        "APIName, APIEndpoint, StatusCode, ResponseMs, RetryCount, "
        "Message, ErrorDetails) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )

    def __init__(self, connection=None):
        self.stream_logger = logging.getLogger("aiwo_fallback")
        if not self.stream_logger.handlers:
            handler = logging.StreamHandler()
            self.stream_logger.addHandler(handler)
            self.stream_logger.setLevel(logging.INFO)

        if connection is not None:
            self.conn = connection
        else:
            conn_str = os.getenv("AI_WO_DB")
            if not conn_str:
                raise ValueError("Environment variable AI_WO_DB not set")
            try:
                self.conn = pyodbc.connect(conn_str)
            except Exception as e:  # pragma: no cover - connection may fail
                self.stream_logger.error(
                    f"DB connection failed: {e}. Falling back to console logging.")
                self.conn = None

    def log(self, level, step, order=None, seq_key=None, execution_id=None,
            phase=None, model_name=None, model_version=None, model_probability=None,
            decision=None, api_name=None, api_endpoint=None, status_code=None,
            response_ms=None, retry_count=None, message="", error_details=None):
        params = [level, step, order, seq_key,
                  str(execution_id) if execution_id else None, phase,
                  model_name, model_version, model_probability, decision,
                  api_name, api_endpoint, status_code, response_ms, retry_count,
                  message, error_details]
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.fast_executemany = True
                cursor.execute(self.INSERT_SQL, params)
                self.conn.commit()
                cursor.close()
            except Exception as e:  # pragma: no cover - DB may fail
                self.stream_logger.error(f"DB log failed: {e}")
                self.stream_logger.log(getattr(logging, level.upper(), logging.INFO),
                                       f"{step}: {message}")
        else:
            self.stream_logger.log(getattr(logging, level.upper(), logging.INFO),
                                   f"{step}: {message}")


class db_logged(ContextDecorator):
    """Context manager/decorator for automatic DB logging."""

    def __init__(self, step, phase=None, api_name=None, logger=None, execution_id=None):
        self.step = step
        self.phase = phase
        self.api_name = api_name
        self.logger = logger
        self.execution_id = execution_id

    def __enter__(self):
        if self.logger is None:
            self.logger = globals().get("logger")
        if self.execution_id is None:
            self.execution_id = globals().get("EXEC_ID")
        if self.logger:
            self.logger.log(level="INFO", step=self.step, phase=self.phase,
                            api_name=self.api_name, execution_id=self.execution_id,
                            message="start")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.logger:
            if exc_type is None:
                self.logger.log(level="INFO", step=self.step, phase=self.phase,
                                api_name=self.api_name, execution_id=self.execution_id,
                                message="success")
            else:
                err = "".join(traceback.format_exception(exc_type, exc, tb))
                self.logger.log(level="ERROR", step=self.step, phase=self.phase,
                                api_name=self.api_name, execution_id=self.execution_id,
                                message=str(exc), error_details=err)
        return False
