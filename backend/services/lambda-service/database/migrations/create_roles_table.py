"""
Create Roles Table Migration
Creates the Roles collection with indexes
"""

from lib import Migration


class CreateRolesTable(Migration):
    """Create Roles collection with indexes"""
    
    def up(self):
        # Create Roles collection
        self.create_collection('Roles')
        
        # Create indexes
        self.create_index('Roles', 'RoleID', unique=True)
        self.create_index('Roles', 'Name', unique=True)
        
        print("  ✓ Created Roles collection with indexes")
    
    def down(self):
        self.drop_collection('Roles')
