"""
Create Users Table Migration
Creates the Users collection with indexes
"""

from lib import Migration


class CreateUsersTable(Migration):
    """Create Users collection with indexes"""
    
    def up(self):
        # Create Users collection
        self.create_collection('Users')
        
        # Create indexes
        self.create_index('Users', 'Email', unique=True)
        self.create_index('Users', 'Username', unique=True)
        self.create_index('Users', 'RoleID')
        
        print("  ✓ Created Users collection with indexes")
    
    def down(self):
        self.drop_collection('Users')
