from __future__ import annotations

import logging
import os
import traceback
import uuid
from contextlib import ContextDecorator
from typing import Any, Optional

import pyodbc

from load_environment import ConfigLoader
from decrypt import decrypt_keys


def new_execution() -> uuid.UUID:
    """Generate a fresh UUID4 to correlate log rows for one run."""
    return uuid.uuid4()


class DBLogger:
    """Write structured events into ``dbo.AIWOApproval``."""

    INSERT_SQL = (
        "INSERT INTO dbo.AIWOApproval ("
        "LogLevel, Step, [Order], Seq_Key, ExecutionId, Phase, "
        "ModelName, ModelVersion, ModelProbability, Decision, "
        "APIName, APIEndpoint, StatusCode, ResponseMs, RetryCount, "
        "Message, ErrorDetails) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )

    def __init__(
        self,
        environment: str = "dev",
        connection: Optional[pyodbc.Connection] = None,
    ) -> None:
        self._stream = logging.getLogger("aiwo_fallback")
        if not self._stream.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            self._stream.addHandler(handler)
            self._stream.setLevel(logging.INFO)

        if connection is not None:
            self.conn: Optional[pyodbc.Connection] = connection
            return

        try:
            cfg_loader = ConfigLoader(environment)
            db_cfg = cfg_loader.get_database_config()
            server = db_cfg["server"]
            database = db_cfg["database"]
            username = decrypt_keys("user_uid")
            password = decrypt_keys("password_pwd")

            conn_str = (
                "DRIVER={SQL Server};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password}"
            )
            self.conn = pyodbc.connect(conn_str, autocommit=False)
        except Exception as exc:  # pragma: no cover - connection may fail
            self._stream.error(
                f"DBLogger: could not open DB connection ({exc}). Falling back to console."
            )
            self.conn = None

    def log(
        self,
        level: str,
        step: str,
        *,
        order: float | None = None,
        seq_key: float | None = None,
        execution_id: uuid.UUID | None = None,
        phase: str | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        model_probability: float | None = None,
        decision: str | None = None,
        api_name: str | None = None,
        api_endpoint: str | None = None,
        status_code: int | None = None,
        response_ms: int | None = None,
        retry_count: int | None = None,
        message: str = "",
        error_details: str | None = None,
    ) -> None:
        params: list[Any] = [
            level.upper(),
            step,
            order,
            seq_key,
            str(execution_id) if execution_id else None,
            phase,
            model_name,
            model_version,
            model_probability,
            decision,
            api_name,
            api_endpoint,
            status_code,
            response_ms,
            retry_count,
            message,
            error_details,
        ]

        if self.conn:
            try:
                cur = self.conn.cursor()
                cur.fast_executemany = True
                cur.execute(self.INSERT_SQL, params)
                self.conn.commit()
                cur.close()
            except Exception as exc:  # pragma: no cover - DB write may fail
                self._stream.error(f"DBLogger: INSERT failed ({exc}) -> console fallback")
                self._fallback(level, step, message)
        else:
            self._fallback(level, step, message)

    def _fallback(self, level: str, step: str, message: str) -> None:
        self._stream.log(getattr(logging, level.upper(), logging.INFO), f"{step}: {message}")


class db_logged(ContextDecorator):
    """Context manager / decorator to auto-log start, success and failures."""

    def __init__(
        self,
        step: str,
        phase: str | None = None,
        api_name: str | None = None,
        *,
        logger: Optional[DBLogger] = None,
        execution_id: Optional[uuid.UUID] = None,
    ) -> None:
        self.step = step
        self.phase = phase
        self.api_name = api_name
        self.logger = logger or globals().get("logger")
        self.execution_id = execution_id or globals().get("EXEC_ID")

    def __enter__(self):
        if self.logger:
            self.logger.log(
                level="INFO",
                step=self.step,
                phase=self.phase,
                api_name=self.api_name,
                execution_id=self.execution_id,
                message="start",
            )
        return self

    def __exit__(self, exc_type, exc, tb):
        if not self.logger:
            return False

        if exc_type is None:
            self.logger.log(
                level="INFO",
                step=self.step,
                phase=self.phase,
                api_name=self.api_name,
                execution_id=self.execution_id,
                message="success",
            )
        else:
            trace = "".join(traceback.format_exception(exc_type, exc, tb))
            self.logger.log(
                level="ERROR",
                step=self.step,
                order=args.ORDEM,
                phase=self.phase,
                api_name=self.api_name,
                execution_id=self.execution_id,
                message=str(exc),
                error_details=trace,
            )
        return False

