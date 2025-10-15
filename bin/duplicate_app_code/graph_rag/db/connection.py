"""
Database connection utilities for the Agentic Graph RAG system.

This module provides a robust and centralized way to manage the connection
to the Snowflake database. It includes utilities for:

- **Connectivity**: Establishing and managing the connection to Snowflake using
  `sqlalchemy` and the Snowflake SQLAlchemy dialect.
- **Session Management**: A singleton `DatabaseConnection` class to manage the
  database engine and provide sessions for database operations.
- **Configuration**: A `DatabaseConfig` class to manage database connection
  settings from environment variables.
- **Lifecycle Management**: Functions for initializing the database, testing the
  connection, and closing the connection.
- **Snowflake-Specific Handling**: An event listener that automatically
  rewrites SQL queries to handle Snowflake's `VARIANT` data type.
"""

import os
import time
from contextlib import contextmanager
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine as sqlmodel_create_engine

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """
    Manages database configuration settings from environment variables.

    This class reads all necessary database connection settings from the
    environment and provides a method to validate that all required settings
    are present.
    """

    def __init__(self):
        """Initializes the database configuration from environment variables."""
        # Snowflake credentials
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
        self.role = os.getenv("SNOWFLAKE_ROLE")

        # Connection pool settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))

        # Retry settings
        self.max_retries = int(os.getenv("DB_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("DB_RETRY_DELAY", "1.0"))

        # Echo SQL (for debugging)
        self.echo_sql = os.getenv("DB_ECHO_SQL", "false").lower() == "true"

    def validate(self) -> None:
        """
        Validates that all required database configuration settings are present.

        Raises:
            ValueError: If any required environment variables are missing.
        """
        required_fields = [
            "account", "user", "password", "warehouse", "database"
        ]

        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field.upper())

        if missing_fields:
            raise ValueError(
                f"Missing required environment variables: "
                f"{', '.join(f'SNOWFLAKE_{f}' for f in missing_fields)}"
            )

    def get_connection_string(self) -> str:
        """
        Builds the Snowflake connection string from the configuration.

        Returns:
            The Snowflake connection string.
        """
        from urllib.parse import quote_plus

        self.validate()

        # Snowflake SQLAlchemy connection string format
        # snowflake://<user>:<password>@<account>/<database>/<schema>?warehouse=<warehouse>&role=<role>
        # URL-encode credentials to handle special characters

        user_encoded = quote_plus(self.user)
        password_encoded = quote_plus(self.password)

        conn_str = (
            f"snowflake://{user_encoded}:{password_encoded}@{self.account}/"
            f"{self.database}/{self.schema}"
            f"?warehouse={self.warehouse}"
        )

        if self.role:
            conn_str += f"&role={self.role}"

        return conn_str


class DatabaseConnection:
    """
    A singleton class that manages the database engine and sessions.

    This class provides a centralized way to manage the database connection,
    including connection pooling, session management, transaction handling,
    and retry logic. It also includes an event listener to handle
    Snowflake-specific SQL syntax for `VARIANT` data types.
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initializes the database connection manager.

        Args:
            config: A `DatabaseConfig` object. If not provided, a default
                configuration will be created from environment variables.
        """
        self.config = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self._initialized = False

    def create_engine(self) -> Engine:
        """
        Creates the SQLAlchemy engine with connection pooling.

        Returns:
            The configured SQLAlchemy engine.
        """
        if self.engine is not None:
            return self.engine

        connection_string = self.config.get_connection_string()

        # Create engine with connection pooling
        self.engine = create_engine(
            connection_string,
            echo=self.config.echo_sql,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=True,  # Test connections before using
            connect_args={
                "client_session_keep_alive": True,  # Keep Snowflake sessions alive
                "supports_native_json": True,  # Enable native JSON/VARIANT support
            }
        )

        # Set up event listeners
        self._setup_event_listeners()

        return self.engine

    def _setup_event_listeners(self) -> None:
        """
        Sets up SQLAlchemy event listeners for connection handling.

        This method sets up an event listener that automatically rewrites
        `INSERT ... VALUES` statements to `INSERT ... SELECT` statements when
        `VARIANT` columns are present. This is necessary because Snowflake
        does not allow expressions like `PARSE_JSON` in the `VALUES` clause.
        """
        if self.engine is None:
            return

        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Handle new connections."""
            # Set session parameters if needed
            pass

        @event.listens_for(self.engine, "before_cursor_execute", retval=True)
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """
            Rewrites `INSERT ... VALUES` to `INSERT ... SELECT` for `VARIANT` columns.
            """
            # Only process INSERT statements with VARIANT columns
            if not statement.strip().upper().startswith("INSERT"):
                return statement, parameters

            # Check if parameters contain PARSE_JSON expressions (from bind_expression)
            has_parse_json = "PARSE_JSON" in statement

            if has_parse_json and " VALUES " in statement.upper():
                # Rewrite INSERT ... VALUES to INSERT ... SELECT
                # Example: INSERT INTO table (col1, col2) VALUES (%(col1)s, PARSE_JSON(%(col2)s))
                # Becomes: INSERT INTO table (col1, col2) SELECT %(col1)s, PARSE_JSON(%(col2)s)

                # Simply replace VALUES with SELECT
                statement = statement.replace(" VALUES (", " SELECT ")
                # Remove the closing parenthesis after VALUES
                statement = statement.rstrip(")")

            return statement, parameters

        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Handle connection checkout from pool."""
            # Verify connection is alive
            pass

    def init_db(self) -> None:
        """
        Initializes the database by creating all tables.

        This method creates all the tables defined in the data models.
        """
        if self._initialized:
            return

        engine = self.create_engine()

        # Import all models to ensure they're registered
        from ..models.project import Project
        from ..models.schema import Schema
        from ..models.node import Node
        from ..models.edge import Edge
        from ..models.file_record import FileRecord
        from ..models.ontology_proposal import OntologyProposal
        from ..models.chunk import Chunk

        # Create all tables
        SQLModel.metadata.create_all(engine)

        self._initialized = True
        print("✓ Database initialized successfully")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Provides a database session with automatic cleanup.

        This method should be used as a context manager to ensure that the
        session is properly closed and that transactions are committed or
        rolled back as needed.

        Yields:
            A `sqlmodel.Session` object.
        """
        if self.engine is None:
            self.create_engine()

        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_with_retry(
        self,
        func,
        *args,
        **kwargs
    ):
        """
        Executes a database function with exponential backoff and retry logic.

        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the function.

        Raises:
            The last exception if all retries fail.
        """
        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Database operation failed (attempt {attempt + 1}/{self.config.max_retries}). "
                          f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"Database operation failed after {self.config.max_retries} attempts.")
            except SQLAlchemyError as e:
                # Don't retry on other SQL errors
                raise e

        raise last_exception

    def test_connection(self) -> bool:
        """
        Tests the database connection.

        Returns:
            `True` if the connection is successful, `False` otherwise.
        """
        try:
            engine = self.create_engine()
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            print("✓ Database connection successful")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def close(self) -> None:
        """Closes the database engine and all connections."""
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
            self._initialized = False
            print("✓ Database connections closed")


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """
    Gets the global database connection instance.

    This function returns a singleton `DatabaseConnection` instance.

    Returns:
        The `DatabaseConnection` instance.
    """
    global _db_connection

    if _db_connection is None:
        _db_connection = DatabaseConnection()

    return _db_connection


def get_session() -> Generator[Session, None, None]:
    """
    A dependency function for getting a database session.

    This function is designed to be used with web frameworks like FastAPI that
    support dependency injection.

    Yields:
        A `sqlmodel.Session` object.
    """
    db = get_db()
    with db.get_session() as session:
        yield session


def init_database() -> None:
    """Initializes the database by creating all tables."""
    db = get_db()
    db.init_db()


def test_connection() -> bool:
    """Tests the database connection."""
    db = get_db()
    return db.test_connection()


def close_database() -> None:
    """Closes the database connection."""
    global _db_connection

    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None