"""
Create Sessions Table Migration
Creates the Sessions collection with indexes and TTL
"""

from lib import Migration


class CreateSessionsTable(Migration):
    """Create Sessions collection with indexes and TTL"""

    def up(self):
        # Create Sessions collection
        self.create_collection('Sessions')

        # Create indexes
        self.create_index('Sessions', 'UserID')
        self.create_index('Sessions', 'Token')

        # TTL index for automatic session expiration
        self.create_index(
            'Sessions',
            'TTL',
            ttl=0,  # Expire documents when TTL timestamp is reached
            name='ttl_index'
        )

        print("  ✓ Created Sessions collection with TTL index")

    def down(self):
        self.drop_collection('Sessions')
