"""
Database Migration Facade
Laravel-style migration system for DocumentDB/MongoDB
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class Migration(ABC):
    """
    Abstract base class for database migrations
    Similar to Laravel's Migration class
    
    Usage:
        class CreateUsersTable(Migration):
            def up(self):
                self.create_collection('Users')
                self.create_index('Users', 'Email', unique=True)
                self.create_index('Users', 'Username', unique=True)
            
            def down(self):
                self.drop_collection('Users')
    """
    
    def __init__(self, db):
        """
        Initialize migration with database connection
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
    
    @abstractmethod
    def up(self):
        """
        Run the migration - create tables, indexes, etc.
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def down(self):
        """
        Reverse the migration - drop tables, indexes, etc.
        Must be implemented by subclasses
        """
        pass
    
    # Collection operations
    def create_collection(self, name: str, **options):
        """
        Create a new collection
        
        Args:
            name: Collection name
            **options: Additional options (e.g., capped, size, max)
        """
        try:
            self.db.create_collection(name, **options)
            print(f"✓ Created collection: {name}")
        except Exception as e:
            print(f"✗ Error creating collection {name}: {e}")
    
    def drop_collection(self, name: str):
        """
        Drop a collection
        
        Args:
            name: Collection name
        """
        try:
            self.db.drop_collection(name)
            print(f"✓ Dropped collection: {name}")
        except Exception as e:
            print(f"✗ Error dropping collection {name}: {e}")
    
    def collection_exists(self, name: str) -> bool:
        """
        Check if collection exists
        
        Args:
            name: Collection name
            
        Returns:
            True if exists, False otherwise
        """
        return name in self.db.list_collection_names()
    
    # Index operations
    def create_index(
        self,
        collection: str,
        field: str,
        unique: bool = False,
        sparse: bool = False,
        ttl: Optional[int] = None,
        **options
    ):
        """
        Create an index on a collection
        
        Args:
            collection: Collection name
            field: Field name to index
            unique: Whether index should be unique
            sparse: Whether index should be sparse (ignore null values)
            ttl: TTL in seconds for automatic document expiration
            **options: Additional index options
        """
        try:
            index_options = {**options}
            if unique:
                index_options['unique'] = True
            if sparse:
                index_options['sparse'] = True
            if ttl is not None:
                index_options['expireAfterSeconds'] = ttl
            
            self.db[collection].create_index(field, **index_options)
            index_type = "unique " if unique else ""
            ttl_info = f" (TTL: {ttl}s)" if ttl else ""
            print(f"✓ Created {index_type}index on {collection}.{field}{ttl_info}")
        except Exception as e:
            print(f"✗ Error creating index on {collection}.{field}: {e}")
    
    def create_compound_index(
        self,
        collection: str,
        fields: List[tuple],
        unique: bool = False,
        **options
    ):
        """
        Create a compound index on multiple fields
        
        Args:
            collection: Collection name
            fields: List of (field, direction) tuples, e.g., [('name', 1), ('age', -1)]
            unique: Whether index should be unique
            **options: Additional index options
        """
        try:
            index_options = {**options}
            if unique:
                index_options['unique'] = True
            
            self.db[collection].create_index(fields, **index_options)
            field_names = ', '.join([f[0] for f in fields])
            print(f"✓ Created compound index on {collection}.({field_names})")
        except Exception as e:
            print(f"✗ Error creating compound index on {collection}: {e}")
    
    def drop_index(self, collection: str, index_name: str):
        """
        Drop an index from a collection
        
        Args:
            collection: Collection name
            index_name: Name of the index to drop
        """
        try:
            self.db[collection].drop_index(index_name)
            print(f"✓ Dropped index {index_name} from {collection}")
        except Exception as e:
            print(f"✗ Error dropping index {index_name} from {collection}: {e}")
    
    # Document operations
    def insert_document(self, collection: str, document: Dict[str, Any]):
        """
        Insert a document into a collection
        
        Args:
            collection: Collection name
            document: Document to insert
        """
        try:
            self.db[collection].insert_one(document)
            print(f"✓ Inserted document into {collection}")
        except Exception as e:
            print(f"✗ Error inserting document into {collection}: {e}")
    
    def insert_documents(self, collection: str, documents: List[Dict[str, Any]]):
        """
        Insert multiple documents into a collection
        
        Args:
            collection: Collection name
            documents: List of documents to insert
        """
        try:
            self.db[collection].insert_many(documents)
            print(f"✓ Inserted {len(documents)} documents into {collection}")
        except Exception as e:
            print(f"✗ Error inserting documents into {collection}: {e}")


class MigrationRunner:
    """
    Migration runner to execute migrations
    Tracks migration history in a 'migrations' collection
    """
    
    def __init__(self, db):
        """
        Initialize migration runner
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.migrations_collection = 'migrations'
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Ensure migrations tracking collection exists"""
        if self.migrations_collection not in self.db.list_collection_names():
            self.db.create_collection(self.migrations_collection)
            self.db[self.migrations_collection].create_index('name', unique=True)
    
    def has_run(self, migration_name: str) -> bool:
        """
        Check if a migration has already been run
        
        Args:
            migration_name: Name of the migration
            
        Returns:
            True if migration has run, False otherwise
        """
        doc = self.db[self.migrations_collection].find_one({'name': migration_name})
        return doc is not None
    
    def mark_as_run(self, migration_name: str):
        """
        Mark a migration as run
        
        Args:
            migration_name: Name of the migration
        """
        import time
        self.db[self.migrations_collection].insert_one({
            'name': migration_name,
            'run_at': int(time.time())
        })
    
    def mark_as_reverted(self, migration_name: str):
        """
        Remove migration from history (after rollback)
        
        Args:
            migration_name: Name of the migration
        """
        self.db[self.migrations_collection].delete_one({'name': migration_name})
    
    def run(self, migration_class: type, migration_name: str):
        """
        Run a migration if it hasn't been run yet
        
        Args:
            migration_class: Migration class to instantiate and run
            migration_name: Unique name for this migration
        """
        if self.has_run(migration_name):
            print(f"⊘ Migration already run: {migration_name}")
            return
        
        print(f"→ Running migration: {migration_name}")
        migration = migration_class(self.db)
        migration.up()
        self.mark_as_run(migration_name)
        print(f"✓ Migration complete: {migration_name}")
    
    def rollback(self, migration_class: type, migration_name: str):
        """
        Rollback a migration if it has been run
        
        Args:
            migration_class: Migration class to instantiate and rollback
            migration_name: Unique name for this migration
        """
        if not self.has_run(migration_name):
            print(f"⊘ Migration not run, cannot rollback: {migration_name}")
            return
        
        print(f"→ Rolling back migration: {migration_name}")
        migration = migration_class(self.db)
        migration.down()
        self.mark_as_reverted(migration_name)
        print(f"✓ Rollback complete: {migration_name}")
    
    def get_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of all run migrations
        
        Returns:
            List of migration records
        """
        cursor = self.db[self.migrations_collection].find({}).sort('run_at', 1)
        migrations = []
        for doc in cursor:
            if '_id' in doc:
                del doc['_id']
            migrations.append(doc)
        return migrations


# Facade functions for easy access
def create_migration_runner(db) -> MigrationRunner:
    """
    Create a migration runner instance
    
    Args:
        db: MongoDB database instance
        
    Returns:
        MigrationRunner instance
    """
    return MigrationRunner(db)


def run_migration(db, migration_class: type, migration_name: str):
    """
    Run a single migration
    
    Args:
        db: MongoDB database instance
        migration_class: Migration class to run
        migration_name: Unique name for the migration
    """
    runner = MigrationRunner(db)
    runner.run(migration_class, migration_name)


def rollback_migration(db, migration_class: type, migration_name: str):
    """
    Rollback a single migration
    
    Args:
        db: MongoDB database instance
        migration_class: Migration class to rollback
        migration_name: Unique name for the migration
    """
    runner = MigrationRunner(db)
    runner.rollback(migration_class, migration_name)
