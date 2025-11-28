"""
Database Seeder Facade
Laravel-style seeding system for DocumentDB/MongoDB
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import uuid
import hashlib


class Seeder(ABC):
    """
    Abstract base class for database seeders
    Similar to Laravel's Seeder class

    Usage:
        class UserSeeder(Seeder):
            def run(self):
                self.create('Users', {
                    'ID': str(uuid.uuid4()),
                    'Username': 'admin',
                    'Email': 'admin@example.com',
                    'Password': self.hash_password('admin123'),
                    'Name': 'Administrator',
                    'RoleID': 'admin-role-id'
                })
    """

    def __init__(self, db):
        """
        Initialize seeder with database connection

        Args:
            db: MongoDB database instance
        """
        self.db = db

    @abstractmethod
    def run(self):
        """
        Run the seeder - insert data into collections
        Must be implemented by subclasses
        """
        pass

    # Helper methods for creating records
    def create(self, collection: str, document: Dict[str, Any]) -> bool:
        """
        Create a single document in a collection

        Args:
            collection: Collection name
            document: Document to insert

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db[collection].insert_one(document)
            print(f"✓ Created document in {collection}")
            return True
        except Exception as e:
            print(f"✗ Error creating document in {collection}: {e}")
            return False

    def create_many(self, collection: str, documents: List[Dict[str, Any]]) -> bool:
        """
        Create multiple documents in a collection

        Args:
            collection: Collection name
            documents: List of documents to insert

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db[collection].insert_many(documents)
            print(f"✓ Created {len(documents)} documents in {collection}")
            return True
        except Exception as e:
            print(f"✗ Error creating documents in {collection}: {e}")
            return False

    def update_or_create(
        self,
        collection: str,
        filter_query: Dict[str, Any],
        document: Dict[str, Any]
    ) -> bool:
        """
        Update existing document or create if not exists

        Args:
            collection: Collection name
            filter_query: Query to find existing document
            document: Document data

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db[collection].replace_one(
                filter_query,
                document,
                upsert=True
            )
            print(f"✓ Updated or created document in {collection}")
            return True
        except Exception as e:
            print(f"✗ Error upserting document in {collection}: {e}")
            return False
    
    def truncate(self, collection: str) -> bool:
        """
        Delete all documents from a collection
        
        Args:
            collection: Collection name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.db[collection].delete_many({})
            print(f"✓ Truncated {collection} ({result.deleted_count} documents)")
            return True
        except Exception as e:
            print(f"✗ Error truncating {collection}: {e}")
            return False
    
    def call(self, seeder_class: type):
        """
        Call another seeder from within this seeder
        Similar to Laravel's $this->call()
        
        Args:
            seeder_class: Seeder class to instantiate and run
        """
        print(f"→ Calling seeder: {seeder_class.__name__}")
        seeder = seeder_class(self.db)
        seeder.run()
    
    # Utility methods
    @staticmethod
    def generate_id() -> str:
        """
        Generate a unique ID
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def faker(self):
        """
        Get faker instance for generating fake data
        Note: Requires faker package to be installed
        
        Returns:
            Faker instance or None if not available
        """
        try:
            from faker import Faker
            return Faker()
        except ImportError:
            print("⚠ Warning: faker package not installed")
            return None


class DatabaseSeeder(Seeder):
    """
    Main database seeder - calls all other seeders
    Similar to Laravel's DatabaseSeeder
    
    Usage:
        class DatabaseSeeder(DatabaseSeeder):
            def run(self):
                self.call(RoleSeeder)
                self.call(UserSeeder)
                self.call(ArtifactSeeder)
    """
    
    def run(self):
        """
        Override this method to call all your seeders
        """
        pass


class SeederRunner:
    """
    Seeder runner to execute seeders
    Tracks seeding history in a 'seeds' collection
    """
    
    def __init__(self, db, track_history: bool = False):
        """
        Initialize seeder runner
        
        Args:
            db: MongoDB database instance
            track_history: Whether to track seeding history
        """
        self.db = db
        self.track_history = track_history
        self.seeds_collection = 'seeds'
        
        if self.track_history:
            self._ensure_seeds_table()
    
    def _ensure_seeds_table(self):
        """Ensure seeds tracking collection exists"""
        if self.seeds_collection not in self.db.list_collection_names():
            self.db.create_collection(self.seeds_collection)
            self.db[self.seeds_collection].create_index('name', unique=True)
    
    def has_run(self, seeder_name: str) -> bool:
        """
        Check if a seeder has already been run
        
        Args:
            seeder_name: Name of the seeder
            
        Returns:
            True if seeder has run, False otherwise
        """
        if not self.track_history:
            return False
        
        doc = self.db[self.seeds_collection].find_one({'name': seeder_name})
        return doc is not None
    
    def mark_as_run(self, seeder_name: str):
        """
        Mark a seeder as run
        
        Args:
            seeder_name: Name of the seeder
        """
        if not self.track_history:
            return
        
        import time
        try:
            self.db[self.seeds_collection].insert_one({
                'name': seeder_name,
                'run_at': int(time.time())
            })
        except Exception:
            # Ignore duplicate key errors
            pass
    
    def run(self, seeder_class: type, seeder_name: Optional[str] = None, force: bool = False):
        """
        Run a seeder
        
        Args:
            seeder_class: Seeder class to instantiate and run
            seeder_name: Optional custom name (defaults to class name)
            force: Run even if already run before
        """
        name = seeder_name or seeder_class.__name__
        
        if not force and self.has_run(name):
            print(f"⊘ Seeder already run: {name}")
            return
        
        print(f"→ Running seeder: {name}")
        seeder = seeder_class(self.db)
        seeder.run()
        self.mark_as_run(name)
        print(f"✓ Seeder complete: {name}")
    
    def get_seeds(self) -> List[Dict[str, Any]]:
        """
        Get list of all run seeders
        
        Returns:
            List of seeder records
        """
        if not self.track_history:
            return []
        
        cursor = self.db[self.seeds_collection].find({}).sort('run_at', 1)
        seeds = []
        for doc in cursor:
            if '_id' in doc:
                del doc['_id']
            seeds.append(doc)
        return seeds


# Facade functions for easy access
def create_seeder_runner(db, track_history: bool = False) -> SeederRunner:
    """
    Create a seeder runner instance
    
    Args:
        db: MongoDB database instance
        track_history: Whether to track seeding history
        
    Returns:
        SeederRunner instance
    """
    return SeederRunner(db, track_history)


def run_seeder(db, seeder_class: type, force: bool = False):
    """
    Run a single seeder
    
    Args:
        db: MongoDB database instance
        seeder_class: Seeder class to run
        force: Run even if already run before
    """
    runner = SeederRunner(db, track_history=False)
    runner.run(seeder_class, force=force)


def seed_database(db, seeder_classes: List[type], track_history: bool = False):
    """
    Run multiple seeders in sequence
    
    Args:
        db: MongoDB database instance
        seeder_classes: List of seeder classes to run
        track_history: Whether to track seeding history
    """
    runner = SeederRunner(db, track_history)
    for seeder_class in seeder_classes:
        runner.run(seeder_class)
