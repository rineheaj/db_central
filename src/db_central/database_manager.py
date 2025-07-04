"""
DatabaseManager - High-level database operations for db_central.

This module provides the DatabaseManager class which offers simple CRUD operations
with proper error handling and validation, abstracting away SQL complexities.
"""

from typing import List, Optional, Type
import logging
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import Engine

from .exceptions import DatabaseError, ConnectionError, ValidationError

# Set up logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    High-level database manager providing simple CRUD operations.
    
    This class abstracts away SQL complexities and provides intuitive methods
    for common database operations with proper error handling and validation.
    """
    
    def __init__(self, database_url: str = "sqlite:///orm.db", echo: bool = False):
        """
        Initialize the DatabaseManager.
        
        Args:
            database_url: Database connection URL (defaults to SQLite)
            echo: Enable SQL query logging
            
        Raises:
            ConnectionError: If unable to connect to database
        """
        self.database_url = database_url
        self.echo = echo
        self._engine: Optional[Engine] = None
        self._connect()
    
    def _connect(self, max_retries: int = 3) -> None:
        """
        Establish database connection with retry mechanism.
        
        Args:
            max_retries: Maximum number of connection attempts
            
        Raises:
            ConnectionError: If all connection attempts fail
        """
        for attempt in range(max_retries):
            try:
                self._engine = create_engine(self.database_url, echo=self.echo)
                # Test connection
                with Session(self._engine) as session:
                    session.exec(select(1))
                logger.info(f"Connected to database: {self.database_url}")
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise ConnectionError(f"Failed to connect to database after {max_retries} attempts: {e}")
    
    def initialize_tables(self) -> None:
        """
        Create all tables defined in the models.
        
        Raises:
            DatabaseError: If table creation fails
        """
        try:
            SQLModel.metadata.create_all(self._engine)
            logger.info("Database tables initialized successfully")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to initialize tables: {e}")
    
    @contextmanager
    def session(self):
        """
        Context manager for database sessions with automatic cleanup.
        
        Yields:
            Session: SQLModel session object
            
        Raises:
            DatabaseError: If session creation fails
        """
        if not self._engine:
            raise DatabaseError("Database not connected")
        
        session = Session(self._engine)
        try:
            yield session
            session.commit()
        except (ValidationError, ConnectionError, DatabaseError):
            session.rollback()
            raise  # Re-raise our custom exceptions as-is
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()
    
    def create(self, obj: SQLModel) -> SQLModel:
        """
        Create a new record in the database.
        
        Args:
            obj: SQLModel instance to create
            
        Returns:
            The created object with populated ID
            
        Raises:
            ValidationError: If object validation fails
            DatabaseError: If creation fails
        """
        if not isinstance(obj, SQLModel):
            raise ValidationError("Object must be a SQLModel instance")
        
        try:
            with self.session() as session:
                session.add(obj)
                session.commit()
                session.refresh(obj)
                # Detach the object from the session to prevent DetachedInstanceError
                session.expunge(obj)
                logger.debug(f"Created {type(obj).__name__} with ID: {obj.id}")
                return obj
        except IntegrityError as e:
            raise ValidationError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create record: {e}")
    
    def get_by_id(self, model_class: Type[SQLModel], obj_id: int) -> Optional[SQLModel]:
        """
        Retrieve a record by its ID.
        
        Args:
            model_class: The model class to query
            obj_id: The ID of the record to retrieve
            
        Returns:
            The record if found, None otherwise
            
        Raises:
            ValidationError: If invalid parameters provided
            DatabaseError: If query fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        if not isinstance(obj_id, int) or obj_id <= 0:
            raise ValidationError("obj_id must be a positive integer")
        
        try:
            with self.session() as session:
                result = session.get(model_class, obj_id)
                if result:
                    # Ensure all attributes are loaded before detaching
                    session.refresh(result)
                    session.expunge(result)
                logger.debug(f"Retrieved {model_class.__name__} with ID: {obj_id}")
                return result
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to retrieve record: {e}")
    
    def get_all(self, model_class: Type[SQLModel], limit: Optional[int] = None) -> List[SQLModel]:
        """
        Retrieve all records of a given model type.
        
        Args:
            model_class: The model class to query
            limit: Maximum number of records to return
            
        Returns:
            List of records
            
        Raises:
            ValidationError: If invalid parameters provided
            DatabaseError: If query fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        try:
            with self.session() as session:
                query = select(model_class)
                if limit:
                    query = query.limit(limit)
                results = session.exec(query).all()
                # Detach all objects from session to prevent DetachedInstanceError
                for result in results:
                    session.expunge(result)
                logger.debug(f"Retrieved {len(results)} {model_class.__name__} records")
                return results
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to retrieve records: {e}")
    
    def update(self, obj: SQLModel) -> SQLModel:
        """
        Update an existing record in the database.
        
        Args:
            obj: SQLModel instance to update (must have an ID)
            
        Returns:
            The updated object
            
        Raises:
            ValidationError: If object validation fails
            DatabaseError: If update fails
        """
        if not isinstance(obj, SQLModel):
            raise ValidationError("Object must be a SQLModel instance")
        
        if not hasattr(obj, 'id') or obj.id is None:
            raise ValidationError("Object must have an ID to update")
        
        try:
            with self.session() as session:
                session.add(obj)
                session.commit()
                session.refresh(obj)
                # Detach the object from the session to prevent DetachedInstanceError
                session.expunge(obj)
                logger.debug(f"Updated {type(obj).__name__} with ID: {obj.id}")
                return obj
        except IntegrityError as e:
            raise ValidationError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update record: {e}")
    
    def delete(self, model_class: Type[SQLModel], obj_id: int) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            model_class: The model class to delete from
            obj_id: The ID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
            
        Raises:
            ValidationError: If invalid parameters provided
            DatabaseError: If deletion fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        if not isinstance(obj_id, int) or obj_id <= 0:
            raise ValidationError("obj_id must be a positive integer")
        
        try:
            with self.session() as session:
                obj = session.get(model_class, obj_id)
                if obj:
                    session.delete(obj)
                    session.commit()
                    logger.debug(f"Deleted {model_class.__name__} with ID: {obj_id}")
                    return True
                return False
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to delete record: {e}")
    
    def find_by(self, model_class: Type[SQLModel], **kwargs) -> List[SQLModel]:
        """
        Find records by specific field values.
        
        Args:
            model_class: The model class to query
            **kwargs: Field-value pairs to filter by
            
        Returns:
            List of matching records
            
        Raises:
            ValidationError: If invalid parameters provided
            DatabaseError: If query fails
        """
        if not issubclass(model_class, SQLModel):
            raise ValidationError("model_class must be a SQLModel subclass")
        
        try:
            with self.session() as session:
                query = select(model_class)
                
                for field, value in kwargs.items():
                    if hasattr(model_class, field):
                        query = query.where(getattr(model_class, field) == value)
                    else:
                        raise ValidationError(f"Field '{field}' not found in {model_class.__name__}")
                
                results = session.exec(query).all()
                # Detach all objects from session to prevent DetachedInstanceError
                for result in results:
                    session.expunge(result)
                logger.debug(f"Found {len(results)} {model_class.__name__} records matching criteria")
                return results
        except ValidationError:
            raise  # Re-raise validation errors as-is
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to find records: {e}")


def create_database_manager(database_url: str = "sqlite:///orm.db", echo: bool = False) -> DatabaseManager:
    """
    Create and return a configured DatabaseManager instance.
    
    Args:
        database_url: Database connection URL
        echo: Enable SQL query logging
        
    Returns:
        Configured DatabaseManager instance
    """
    return DatabaseManager(database_url=database_url, echo=echo)