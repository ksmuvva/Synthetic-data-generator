"""SQL format handler for generating INSERT statements."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class SQLFormatter(BaseFormatter):
    """SQL format handler for INSERT statements."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize SQL formatter.

        Args:
            config: SQL configuration
        """
        super().__init__(config)
        self.table_name = config.get("table_name", "data")
        self.batch_size = config.get("batch_size", 1000)  # Number of rows per INSERT
        self.include_drop = config.get("include_drop", False)
        self.include_create = config.get("include_create", True)
        self.dialect = config.get("dialect", "standard")  # standard, mysql, postgresql, sqlite

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to SQL INSERT statements.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                # Write header comment
                f.write(f"-- SQL INSERT statements for table: {self.table_name}\n")
                f.write(f"-- Generated rows: {len(df)}\n")
                f.write(f"-- Columns: {', '.join(df.columns)}\n\n")

                # Write DROP statement if requested
                if self.include_drop:
                    f.write(f"DROP TABLE IF EXISTS {self.table_name};\n\n")

                # Write CREATE statement if requested
                if self.include_create:
                    f.write(self._generate_create_statement(df))
                    f.write("\n\n")

                # Write INSERT statements
                self._write_insert_statements(df, f)

        except Exception as e:
            raise FormatError(f"Failed to export SQL: {e}")

    def _generate_create_statement(self, df: pd.DataFrame) -> str:
        """
        Generate CREATE TABLE statement.

        Args:
            df: DataFrame to analyze

        Returns:
            CREATE TABLE SQL statement
        """
        lines = [f"CREATE TABLE {self.table_name} ("]
        column_defs = []

        for col in df.columns:
            dtype = df[col].dtype
            sql_type = self._map_dtype_to_sql(dtype)
            column_defs.append(f"    {col} {sql_type}")

        lines.append(",\n".join(column_defs))
        lines.append(");")

        return "\n".join(lines)

    def _map_dtype_to_sql(self, dtype) -> str:
        """
        Map pandas dtype to SQL type.

        Args:
            dtype: Pandas dtype

        Returns:
            SQL type string
        """
        dtype_str = str(dtype)

        if "int" in dtype_str:
            return "INTEGER"
        elif "float" in dtype_str:
            return "REAL"
        elif "bool" in dtype_str:
            return "BOOLEAN"
        elif "datetime" in dtype_str:
            return "TIMESTAMP"
        elif "date" in dtype_str:
            return "DATE"
        else:
            # Default to TEXT/VARCHAR
            if self.dialect == "mysql":
                return "VARCHAR(255)"
            elif self.dialect == "postgresql":
                return "TEXT"
            else:
                return "TEXT"

    def _write_insert_statements(self, df: pd.DataFrame, file) -> None:
        """
        Write INSERT statements to file.

        Args:
            df: DataFrame to export
            file: File handle
        """
        columns = ", ".join(df.columns)

        # Process in batches
        for i in range(0, len(df), self.batch_size):
            batch = df.iloc[i : i + self.batch_size]

            if self.dialect in ["mysql", "postgresql"]:
                # Multi-row INSERT for MySQL/PostgreSQL
                file.write(f"INSERT INTO {self.table_name} ({columns}) VALUES\n")

                values_list = []
                for _, row in batch.iterrows():
                    values = self._format_values(row)
                    values_list.append(f"    ({values})")

                file.write(",\n".join(values_list))
                file.write(";\n\n")
            else:
                # Single-row INSERTs for standard SQL/SQLite
                for _, row in batch.iterrows():
                    values = self._format_values(row)
                    file.write(f"INSERT INTO {self.table_name} ({columns}) VALUES ({values});\n")

                file.write("\n")

    def _format_values(self, row: pd.Series) -> str:
        """
        Format row values for SQL INSERT.

        Args:
            row: DataFrame row

        Returns:
            Formatted values string
        """
        formatted = []
        for value in row:
            if pd.isna(value):
                formatted.append("NULL")
            elif isinstance(value, (int, float)):
                formatted.append(str(value))
            elif isinstance(value, bool):
                formatted.append("TRUE" if value else "FALSE")
            else:
                # Escape single quotes in strings
                str_value = str(value).replace("'", "''")
                formatted.append(f"'{str_value}'")

        return ", ".join(formatted)

    def get_extension(self) -> str:
        """Get file extension."""
        return ".sql"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for SQL export."""
        if df is None or df.empty:
            return False

        # Check for invalid column names (SQL reserved keywords should be avoided)
        # For now, just check they're not empty
        invalid_cols = [col for col in df.columns if not str(col).strip()]
        if invalid_cols:
            raise FormatError("DataFrame contains empty column names")

        return True
