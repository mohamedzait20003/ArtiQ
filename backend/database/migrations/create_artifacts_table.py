"""
Create Artifacts Table Migration
Creates the Artifacts collection with indexes
"""

from lib import Migration


class CreateArtifactsTable(Migration):
    """Create Artifacts collection with indexes"""

    def up(self):
        # Create Artifacts collection
        self.create_collection('Artifacts')

        # Create indexes
        self.create_index('Artifacts', 'id', unique=True)
        self.create_index('Artifacts', 'name')
        self.create_index('Artifacts', 'artifact_type')

        # Compound index for efficient filtering
        self.create_compound_index(
            'Artifacts',
            [('artifact_type', 1), ('name', 1)]
        )

        print("  ✓ Created Artifacts collection with indexes")

    def down(self):
        self.drop_collection('Artifacts')
