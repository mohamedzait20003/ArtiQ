"""
Database Seeders
Register and run seeders globally
"""

from lib import AWSServices  # noqa: E402
from database.seeders.roles_seeder import RolesSeeder  # noqa: E402
from database.seeders.admin_seeder import (  # noqa: E402
    DefaultAdminSeeder
)


# Register all seeders here (order matters - run in sequence)
SEEDERS = {
    'RolesSeeder': RolesSeeder,
    'DefaultAdminSeeder': DefaultAdminSeeder,
}


def run_seeder(seeder_name: str, force: bool = False):
    """
    Run a specific seeder

    Args:
        seeder_name: Name of the seeder class
        force: Whether to force run even if already run
    """
    if seeder_name not in SEEDERS:
        available = ', '.join(SEEDERS.keys())
        raise ValueError(
            f"Seeder '{seeder_name}' not found. "
            f"Available seeders: {available}"
        )

    # Get database connection
    aws = AWSServices()
    db = aws.get_documentdb()

    # Create and run seeder
    seeder_class = SEEDERS[seeder_name]
    seeder = seeder_class(db)

    print(f"→ Running {seeder_name}...")
    seeder.run()
    print(f"✓ {seeder_name} completed")


def run_all_seeders(force: bool = False):
    """
    Run all registered seeders

    Args:
        force: Whether to force run even if already run
    """
    print(f"→ Running {len(SEEDERS)} seeder(s)...")

    for seeder_name in SEEDERS.keys():
        run_seeder(seeder_name, force=force)

    print("✓ All seeders completed")


if __name__ == "__main__":
    # Allow running seeders directly
    run_all_seeders()
