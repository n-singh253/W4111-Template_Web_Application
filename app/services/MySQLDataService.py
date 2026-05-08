from __future__ import annotations

import os
import re
from collections.abc import Sequence
from typing import Any

from .AbstractBaseDataService import AbstractBaseDataService


class MySQLDataService(AbstractBaseDataService):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._table_name = self._quote_identifier(str(config["table_name"]))
        primary_key_fields = config.get("primary_key_fields") or [
            config.get("primary_key_field", "id")
        ]
        if isinstance(primary_key_fields, str):
            primary_key_fields = [primary_key_fields]
        self._primary_key_fields = [str(field) for field in primary_key_fields]
        self._primary_key_separator = str(config.get("primary_key_separator", ":"))

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
            raise ValueError(f"Invalid SQL identifier: {identifier!r}")
        return f"`{identifier}`"

    def _connect(self):
        try:
            import pymysql
            import pymysql.cursors
        except ImportError as exc:
            raise RuntimeError("PyMySQL is required for MySQLDataService") from exc

        return pymysql.connect(
            host=str(self.config.get("host") or os.getenv("MYSQL_HOST", "localhost")),
            port=int(self.config.get("port") or os.getenv("MYSQL_PORT", "3306")),
            user=str(self.config.get("user") or os.getenv("MYSQL_USER", "root")),
            password=str(self.config.get("password") or os.getenv("MYSQL_PASSWORD", "")),
            database=str(
                self.config.get("database") or os.getenv("MYSQL_DATABASE", "classicmodels")
            ),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def _primary_key_template(self, primary_key: Any) -> dict:
        if isinstance(primary_key, dict):
            return {field: primary_key[field] for field in self._primary_key_fields}
        if len(self._primary_key_fields) == 1:
            return {self._primary_key_fields[0]: primary_key}
        if isinstance(primary_key, Sequence) and not isinstance(primary_key, str):
            values = list(primary_key)
        else:
            values = str(primary_key).split(self._primary_key_separator)
        if len(values) != len(self._primary_key_fields):
            raise ValueError("Composite primary key does not match configured fields")
        return dict(zip(self._primary_key_fields, values))

    def _where_clause(self, template: dict) -> tuple[str, list]:
        if not template:
            return "", []
        clauses: list[str] = []
        values: list = []
        for key, value in template.items():
            column = self._quote_identifier(str(key))
            if value is None:
                clauses.append(f"{column} IS NULL")
            else:
                clauses.append(f"{column} = %s")
                values.append(value)
        return " WHERE " + " AND ".join(clauses), values

    def _primary_key_value(self, row: dict) -> str:
        values = [str(row[field]) for field in self._primary_key_fields]
        return self._primary_key_separator.join(values)

    def retrieveByPrimaryKey(self, primary_key: str) -> dict:
        template = self._primary_key_template(primary_key)
        where_clause, values = self._where_clause(template)
        sql = f"SELECT * FROM {self._table_name}{where_clause} LIMIT 1"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                row = cursor.fetchone()
        return dict(row) if row else {}

    def retrieveByTemplate(self, template: dict) -> list[dict]:
        where_clause, values = self._where_clause(template)
        sql = f"SELECT * FROM {self._table_name}{where_clause}"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def create(self, payload: dict) -> str:
        data = dict(payload)
        if not data:
            raise ValueError("Payload cannot be empty")
        columns = [self._quote_identifier(str(key)) for key in data.keys()]
        placeholders = ", ".join(["%s"] * len(columns))
        sql = (
            f"INSERT INTO {self._table_name} ({', '.join(columns)}) "
            f"VALUES ({placeholders})"
        )
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, list(data.values()))
            connection.commit()
        return self._primary_key_value(data)

    def updateByPrimaryKey(self, primary_key: str, payload: dict) -> int:
        data = {
            key: value
            for key, value in dict(payload).items()
            if key not in self._primary_key_fields
        }
        if not data:
            return 0
        assignments = ", ".join(
            f"{self._quote_identifier(str(key))} = %s" for key in data.keys()
        )
        primary_key_template = self._primary_key_template(primary_key)
        where_clause, where_values = self._where_clause(primary_key_template)
        sql = f"UPDATE {self._table_name} SET {assignments}{where_clause}"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, list(data.values()) + where_values)
                updated = cursor.rowcount
            connection.commit()
        return int(updated)

    def deleteByPrimaryKey(self, primary_key: str) -> int:
        primary_key_template = self._primary_key_template(primary_key)
        where_clause, values = self._where_clause(primary_key_template)
        sql = f"DELETE FROM {self._table_name}{where_clause}"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                deleted = cursor.rowcount
            connection.commit()
        return int(deleted)
