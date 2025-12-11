"""
Create Ratings Table Migration
Creates the Ratings collection with indexes
"""

from lib import Migration


class CreateRatingsTable(Migration):
    """Create Ratings collection with indexes"""

    def up(self):
        # Create Ratings collection
        self.create_collection('Ratings')

        # Create indexes
        # Primary key index on 'id' (format: rating_{artifact_id})
        self.create_index('Ratings', 'id', unique=True)
        
        # Foreign key index on 'artifact_id' for relationship queries
        self.create_index('Ratings', 'artifact_id', unique=False)

        # Compound indexes for efficient filtering by score
        self.create_compound_index(
            'Ratings',
            [('artifact_id', 1), ('net_score.value', -1)]
        )

        print("  ✓ Created Ratings collection with indexes")

    def down(self):
        self.drop_collection('Ratings')
