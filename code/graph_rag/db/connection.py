"""
Database connection utilities for the Agentic Graph RAG system.

Provides:
- Snowflake connectivity with SQLModel
- Session management and connection pooling
- Transaction handling
- Error handling and retries
- Database initialization
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
    """Database configuration from environment variables."""
    
    def __init__(self):
        """Initialize database configuration from environment."""
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
        """Validate that required configuration is present."""
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
        """Build Snowflake connection string."""
        self.validate()
        
        # Snowflake SQLAlchemy connection string format
        # snowflake://<user>:<password>@<account>/<database>/<schema>?warehouse=<warehouse>&role=<role>
        
        conn_str = (
            f"snowflake://{self.user}:{self.password}@{self.account}/"
            f"{self.database}/{self.schema}"
            f"?warehouse={self.warehouse}"
        )
        
        if self.role:
            conn_str += f"&role={self.role}"
        
        return conn_str


class DatabaseConnection:
    """
    Manages database connections and sessions.
    
    Provides:
    - Connection pooling
    - Session management
    - Transaction handling
    - Retry logic
    - Database initialization
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database connection manager.
        
        Args:
            config: Database configuration (defaults to env vars)
        """
        self.config = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self._initialized = False
    
    def create_engine(self) -> Engine:
        """
        Create SQLAlchemy engine with connection pooling.
        
        Returns:
            Configured SQLAlchemy engine
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
            }
        )
        
        # Set up event listeners
        self._setup_event_listeners()
        
        return self.engine
    
    def _setup_event_listeners(self) -> None:
        """Set up SQLAlchemy event listeners for connection handling."""
        if self.engine is None:
            return
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Handle new connections."""
            # Set session parameters if needed
            pass
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Handle connection checkout from pool."""
            # Verify connection is alive
            pass
    
    def init_db(self) -> None:
        """
        Initialize database by creating all tables.
        
        Creates tables for:
        - Projects
        - Schemas
        - Nodes
        - Edges
        """
        if self._initialized:
            return
        
        engine = self.create_engine()
        
        # Import all models to ensure they're registered
        from ..models.project import Project
        from ..models.schema import Schema
        from ..models.node import Node
        from ..models.edge import Edge
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        
        self._initialized = True
        print("✓ Database initialized successfully")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.
        
        Usage:
            with db.get_session() as session:
                # Use session
                session.add(obj)
                session.commit()
        
        Yields:
            SQLModel Session
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
        Execute a database function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func
            
        Raises:
            Last exception if all retries fail
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
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
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
        """Close database engine and all connections."""
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
            self._initialized = False
            print("✓ Database connections closed")


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """
    Get or create global database connection instance.
    
    Returns:
        DatabaseConnection instance
    """
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    
    return _db_connection


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI/similar frameworks.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.query(Item).all()
            return items
    
    Yields:
        SQLModel Session
    """
    db = get_db()
    with db.get_session() as session:
        yield session


def init_database() -> None:
    """Initialize database (create tables)."""
    db = get_db()
    db.init_db()


def test_connection() -> bool:
    """Test database connection."""
    db = get_db()
    return db.test_connection()


def close_database() -> None:
    """Close database connections."""
    global _db_connection
    
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None
