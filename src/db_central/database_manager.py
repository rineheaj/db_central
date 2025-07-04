"""
DatabaseManager: A high-level API for database operations with error handling and retry mechanisms.
"""

import time
import logging
from typing import Type, List, Optional, Any, Dict
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.exc import OperationalError, DisconnectionError


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    pass


class ValidationError(DatabaseError):
    """Exception raised when input validation fails."""
    pass


class DatabaseManager:
    """
    High-level database manager that provides simple CRUD operations
    with error handling and retry mechanisms.
    """
    
    def __init__(self, database_url: str, echo: bool = False, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the DatabaseManager.
        
        Args:
            database_url: Database connection URL
            echo: Whether to log SQL statements
            max_retries: Maximum number of retry attempts for transient failures
            retry_delay: Delay between retry attempts in seconds
        """
        self.database_url = database_url
        self.echo = echo
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        
        try:
            self.engine = create_engine(database_url, echo=echo)
        except Exception as e:
            raise ConnectionError(f"Failed to create database engine: {str(e)}")
    
    def init_database(self) -> None:
        """
        Initialize the database by creating all tables.
        
        Raises:
            ConnectionError: If database initialization fails
        """
        try:
            SQLModel.metadata.create_all(self.engine)
            self.logger.info("Database initialized successfully")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize database: {str(e)}")
    
    @contextmanager
    def get_session(self):
        """
        Get a database session with proper error handling.
        
        Yields:
            Session: SQLModel session object
        
        Raises:
            ConnectionError: If session creation fails
        """
        session = None
        try:
            session = Session(self.engine)
            yield session
        except Exception as e:
            if session:
                session.rollback()
            raise ConnectionError(f"Database session error: {str(e)}")
        finally:
            if session:
                session.close()
    
    def _retry_operation(self, operation, *args, **kwargs):
        """
        Execute an operation with retry logic for transient failures.
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            DatabaseError: If operation fails after all retries
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except (OperationalError, DisconnectionError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Database operation failed (attempt {attempt + 1}), retrying in {self.retry_delay}s: {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Database operation failed after {self.max_retries} attempts: {str(e)}")
            except Exception as e:
                # Non-transient errors should not be retried
                raise DatabaseError(f"Database operation failed: {str(e)}")
        
        raise DatabaseError(f"Database operation failed after {self.max_retries} attempts: {str(last_exception)}")
    
    def create(self, model_instance: SQLModel) -> SQLModel:
        """
        Create a new record in the database.
        
        Args:
            model_instance: SQLModel instance to create
            
        Returns:
            Created model instance with populated ID
            
        Raises:
            ValidationError: If model validation fails
            DatabaseError: If creation fails
        """
        if not isinstance(model_instance, SQLModel):
            raise ValidationError("Instance must be a SQLModel object")
        
        def _create_operation():
            with self.get_session() as session:
                session.add(model_instance)
                session.commit()
                session.refresh(model_instance)
                return model_instance
        
        return self._retry_operation(_create_operation)
    
    def read(self, model_class: Type[SQLModel], model_id: int) -> Optional[SQLModel]:
        """
        Read a record by ID.
        
        Args:
            model_class: SQLModel class to query
            model_id: ID of the record to retrieve
            
        Returns:
            Model instance if found, None otherwise
            
        Raises:
            ValidationError: If parameters are invalid
            DatabaseError: If query fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        if not isinstance(model_id, int) or model_id <= 0:
            raise ValidationError("model_id must be a positive integer")
        
        def _read_operation():
            with self.get_session() as session:
                return session.get(model_class, model_id)
        
        return self._retry_operation(_read_operation)
    
    def read_all(self, model_class: Type[SQLModel], limit: Optional[int] = None) -> List[SQLModel]:
        """
        Read all records of a given model type.
        
        Args:
            model_class: SQLModel class to query
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
            
        Raises:
            ValidationError: If parameters are invalid
            DatabaseError: If query fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        if limit is not None and (not isinstance(limit, int) or limit <= 0):
            raise ValidationError("limit must be a positive integer")
        
        def _read_all_operation():
            with self.get_session() as session:
                query = select(model_class)
                if limit:
                    query = query.limit(limit)
                return session.exec(query).all()
        
        return self._retry_operation(_read_all_operation)
    
    def update(self, model_instance: SQLModel) -> SQLModel:
        """
        Update an existing record.
        
        Args:
            model_instance: SQLModel instance to update
            
        Returns:
            Updated model instance
            
        Raises:
            ValidationError: If model validation fails
            DatabaseError: If update fails
        """
        if not isinstance(model_instance, SQLModel):
            raise ValidationError("Instance must be a SQLModel object")
        
        if not hasattr(model_instance, 'id') or model_instance.id is None:
            raise ValidationError("Model instance must have an ID for updates")
        
        def _update_operation():
            with self.get_session() as session:
                session.add(model_instance)
                session.commit()
                session.refresh(model_instance)
                return model_instance
        
        return self._retry_operation(_update_operation)
    
    def delete(self, model_class: Type[SQLModel], model_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            model_class: SQLModel class
            model_id: ID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
            
        Raises:
            ValidationError: If parameters are invalid
            DatabaseError: If deletion fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        if not isinstance(model_id, int) or model_id <= 0:
            raise ValidationError("model_id must be a positive integer")
        
        def _delete_operation():
            with self.get_session() as session:
                instance = session.get(model_class, model_id)
                if instance is None:
                    return False
                session.delete(instance)
                session.commit()
                return True
        
        return self._retry_operation(_delete_operation)
    
    def query(self, model_class: Type[SQLModel], filters: Dict[str, Any] = None) -> List[SQLModel]:
        """
        Query records with optional filters.
        
        Args:
            model_class: SQLModel class to query
            filters: Dictionary of field names and values to filter by
            
        Returns:
            List of matching model instances
            
        Raises:
            ValidationError: If parameters are invalid
            DatabaseError: If query fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        def _query_operation():
            with self.get_session() as session:
                query = select(model_class)
                
                if filters:
                    for field_name, value in filters.items():
                        if not hasattr(model_class, field_name):
                            raise ValidationError(f"Field '{field_name}' does not exist on {model_class.__name__}")
                        field = getattr(model_class, field_name)
                        query = query.where(field == value)
                
                return session.exec(query).all()
        
        return self._retry_operation(_query_operation)
    
    def count(self, model_class: Type[SQLModel]) -> int:
        """
        Count the number of records for a given model type.
        
        Args:
            model_class: SQLModel class to count
            
        Returns:
            Number of records
            
        Raises:
            ValidationError: If model_class is invalid
            DatabaseError: If count fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        def _count_operation():
            with self.get_session() as session:
                return len(session.exec(select(model_class)).all())
        
        return self._retry_operation(_count_operation)