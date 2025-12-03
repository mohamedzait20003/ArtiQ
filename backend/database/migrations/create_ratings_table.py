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
        self.create_index('Ratings', 'artifact_id', unique=True)
        self.create_index('Ratings', 'name')
        self.create_index('Ratings', 'category')

        # Compound index for efficient filtering
        self.create_compound_index(
            'Ratings',
            [('category', 1), ('net_score.value', -1)]
        )

        print("  ✓ Created Ratings collection with indexes")

    def down(self):
        self.drop_collection('Ratings')
