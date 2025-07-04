from sqlmodel import SQLModel, create_engine, Session, select
from typing import Type, TypeVar, List, Dict, Any, Optional, Union
import time
import logging
from functools import wraps
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables for generic operations
T = TypeVar('T', bound=SQLModel)

# Default configuration
DB_URL = "sqlite:///orm.db"
ENGINE = create_engine(DB_URL, echo=True)

def init_db():
    """Initialize database tables using the default engine.
    
    This function maintains backward compatibility with existing code.
    """
    SQLModel.metadata.create_all(ENGINE)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry database operations on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
            raise last_exception
        return wrapper
    return decorator


class DatabaseManager:
    """A high-level database manager that abstracts SQL complexities.
    
    This class provides easy-to-use methods for database operations without
    requiring extensive SQL knowledge.
    """
    
    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        """Initialize the database manager.
        
        Args:
            database_url: Database connection URL. If None, uses in-memory SQLite.
            echo: Whether to echo SQL statements to stdout
            
        Examples:
            # In-memory database for testing
            db = DatabaseManager()
            
            # File-based database
            db = DatabaseManager("sqlite:///myapp.db")
            
            # PostgreSQL database
            db = DatabaseManager("postgresql://user:pass@localhost/dbname")
        """
        if database_url is None:
            database_url = "sqlite:///:memory:"
            logger.info("Using in-memory SQLite database")
        else:
            logger.info(f"Using database: {database_url}")
            
        self.engine = create_engine(database_url, echo=echo)
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure all defined tables exist in the database."""
        try:
            SQLModel.metadata.create_all(self.engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def create(self, model_instance: T) -> T:
        """Create a new record in the database.
        
        Args:
            model_instance: An instance of a SQLModel table class
            
        Returns:
            The created instance with populated ID and other defaults
            
        Raises:
            ValueError: If the model instance is invalid
            
        Example:
            from models import Author
            author = Author(name="John Doe", email="john@example.com")
            created_author = db.create(author)
        """
        if not isinstance(model_instance, SQLModel):
            raise ValueError("model_instance must be a SQLModel instance")
            
        try:
            with Session(self.engine) as session:
                session.add(model_instance)
                session.commit()
                session.refresh(model_instance)
                logger.info(f"Created {type(model_instance).__name__} with ID: {getattr(model_instance, 'id', 'N/A')}")
                return model_instance
        except Exception as e:
            logger.error(f"Failed to create {type(model_instance).__name__}: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def get_by_id(self, model_class: Type[T], record_id: int) -> Optional[T]:
        """Retrieve a record by its ID.
        
        Args:
            model_class: The SQLModel table class
            record_id: The ID of the record to retrieve
            
        Returns:
            The record if found, None otherwise
            
        Example:
            from models import Author
            author = db.get_by_id(Author, 1)
        """
        try:
            with Session(self.engine) as session:
                record = session.get(model_class, record_id)
                if record:
                    logger.info(f"Retrieved {model_class.__name__} with ID: {record_id}")
                else:
                    logger.info(f"No {model_class.__name__} found with ID: {record_id}")
                return record
        except Exception as e:
            logger.error(f"Failed to retrieve {model_class.__name__} with ID {record_id}: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def get_all(self, model_class: Type[T], limit: Optional[int] = None) -> List[T]:
        """Retrieve all records of a given type.
        
        Args:
            model_class: The SQLModel table class
            limit: Optional limit on number of records to return
            
        Returns:
            List of all records
            
        Example:
            from models import Author
            all_authors = db.get_all(Author, limit=10)
        """
        try:
            with Session(self.engine) as session:
                statement = select(model_class)
                if limit:
                    statement = statement.limit(limit)
                results = session.exec(statement).all()
                logger.info(f"Retrieved {len(results)} {model_class.__name__} records")
                return results
        except Exception as e:
            logger.error(f"Failed to retrieve {model_class.__name__} records: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def find_by_attributes(self, model_class: Type[T], **filters) -> List[T]:
        """Find records by attribute values.
        
        Args:
            model_class: The SQLModel table class
            **filters: Keyword arguments representing attribute=value filters
            
        Returns:
            List of matching records
            
        Example:
            from models import Author
            authors = db.find_by_attributes(Author, name="John Doe")
            books = db.find_by_attributes(Book, author_id=1, title="Some Title")
        """
        try:
            with Session(self.engine) as session:
                statement = select(model_class)
                
                # Apply filters
                for attr_name, value in filters.items():
                    if hasattr(model_class, attr_name):
                        attr = getattr(model_class, attr_name)
                        statement = statement.where(attr == value)
                    else:
                        raise ValueError(f"{model_class.__name__} has no attribute '{attr_name}'")
                
                results = session.exec(statement).all()
                logger.info(f"Found {len(results)} {model_class.__name__} records matching filters: {filters}")
                return results
        except Exception as e:
            logger.error(f"Failed to find {model_class.__name__} records with filters {filters}: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def update(self, model_instance: T, **updates) -> T:
        """Update a record with new values.
        
        Args:
            model_instance: The instance to update (must have an ID)
            **updates: Keyword arguments representing attribute=value updates
            
        Returns:
            The updated instance
            
        Example:
            author = db.get_by_id(Author, 1)
            updated_author = db.update(author, name="Jane Doe", email="jane@example.com")
        """
        if not hasattr(model_instance, 'id') or model_instance.id is None:
            raise ValueError("model_instance must have a valid ID for updates")
            
        try:
            with Session(self.engine) as session:
                # Get fresh instance from database
                fresh_instance = session.get(type(model_instance), model_instance.id)
                if not fresh_instance:
                    raise ValueError(f"No {type(model_instance).__name__} found with ID: {model_instance.id}")
                
                # Apply updates
                for attr_name, value in updates.items():
                    if hasattr(fresh_instance, attr_name):
                        setattr(fresh_instance, attr_name, value)
                    else:
                        raise ValueError(f"{type(model_instance).__name__} has no attribute '{attr_name}'")
                
                session.add(fresh_instance)
                session.commit()
                session.refresh(fresh_instance)
                logger.info(f"Updated {type(model_instance).__name__} with ID: {model_instance.id}")
                return fresh_instance
        except Exception as e:
            logger.error(f"Failed to update {type(model_instance).__name__} with ID {model_instance.id}: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def delete(self, model_instance: T) -> bool:
        """Delete a record from the database.
        
        Args:
            model_instance: The instance to delete (must have an ID)
            
        Returns:
            True if deletion was successful
            
        Example:
            author = db.get_by_id(Author, 1)
            success = db.delete(author)
        """
        if not hasattr(model_instance, 'id') or model_instance.id is None:
            raise ValueError("model_instance must have a valid ID for deletion")
            
        try:
            with Session(self.engine) as session:
                # Get fresh instance from database
                fresh_instance = session.get(type(model_instance), model_instance.id)
                if not fresh_instance:
                    raise ValueError(f"No {type(model_instance).__name__} found with ID: {model_instance.id}")
                
                session.delete(fresh_instance)
                session.commit()
                logger.info(f"Deleted {type(model_instance).__name__} with ID: {model_instance.id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete {type(model_instance).__name__} with ID {model_instance.id}: {e}")
            raise
    
    @retry_on_failure(max_retries=3)
    def bulk_create(self, model_instances: List[T]) -> List[T]:
        """Create multiple records in a single transaction.
        
        Args:
            model_instances: List of SQLModel instances to create
            
        Returns:
            List of created instances with populated IDs
            
        Example:
            authors = [
                Author(name="John Doe", email="john@example.com"),
                Author(name="Jane Smith", email="jane@example.com")
            ]
            created_authors = db.bulk_create(authors)
        """
        if not model_instances:
            return []
            
        if not all(isinstance(instance, SQLModel) for instance in model_instances):
            raise ValueError("All instances must be SQLModel instances")
            
        try:
            with Session(self.engine) as session:
                session.add_all(model_instances)
                session.commit()
                for instance in model_instances:
                    session.refresh(instance)
                logger.info(f"Bulk created {len(model_instances)} records")
                return model_instances
        except Exception as e:
            logger.error(f"Failed to bulk create records: {e}")
            raise
    
    def count(self, model_class: Type[T], **filters) -> int:
        """Count records in a table, optionally with filters.
        
        Args:
            model_class: The SQLModel table class
            **filters: Optional attribute=value filters
            
        Returns:
            Number of matching records
            
        Example:
            total_authors = db.count(Author)
            published_books = db.count(Book, published=True)
        """
        try:
            with Session(self.engine) as session:
                statement = select(model_class)
                
                # Apply filters
                for attr_name, value in filters.items():
                    if hasattr(model_class, attr_name):
                        attr = getattr(model_class, attr_name)
                        statement = statement.where(attr == value)
                    else:
                        raise ValueError(f"{model_class.__name__} has no attribute '{attr_name}'")
                
                count = len(session.exec(statement).all())
                logger.info(f"Counted {count} {model_class.__name__} records")
                return count
        except Exception as e:
            logger.error(f"Failed to count {model_class.__name__} records: {e}")
            raise


# Convenience functions for common operations
def create_database_manager(database_url: Optional[str] = None, echo: bool = False) -> DatabaseManager:
    """Create a new DatabaseManager instance.
    
    Args:
        database_url: Database connection URL. If None, uses in-memory SQLite.
        echo: Whether to echo SQL statements to stdout
        
    Returns:
        Configured DatabaseManager instance
        
    Examples:
        # Quick in-memory database for testing
        db = create_database_manager()
        
        # Production database
        db = create_database_manager("sqlite:///production.db")
    """
    return DatabaseManager(database_url=database_url, echo=echo)


def create_memory_database(echo: bool = False) -> DatabaseManager:
    """Create an in-memory database for quick testing.
    
    Args:
        echo: Whether to echo SQL statements to stdout
        
    Returns:
        DatabaseManager configured with in-memory SQLite
        
    Example:
        db = create_memory_database()
        # Perfect for unit tests and quick prototyping
    """
    return DatabaseManager(database_url="sqlite:///:memory:", echo=echo)


def create_file_database(file_path: Union[str, Path], echo: bool = False) -> DatabaseManager:
    """Create a file-based SQLite database.
    
    Args:
        file_path: Path to the SQLite database file
        echo: Whether to echo SQL statements to stdout
        
    Returns:
        DatabaseManager configured with file-based SQLite
        
    Example:
        db = create_file_database("myapp.db")
        # Data persists between application runs
    """
    if isinstance(file_path, Path):
        file_path = str(file_path)
    return DatabaseManager(database_url=f"sqlite:///{file_path}", echo=echo)

