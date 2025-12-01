"""
Database Migrations
Define and run all database migrations for lambda-service
"""

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")
else:
    print(f"⚠ Warning: .env file not found at {env_path}")

from lib import (  # noqa: E402
    MigrationRunner,
    get_documentdb
)

# Import migration classes
from .create_roles_table import CreateRolesTable  # noqa: E402
from .create_users_table import CreateUsersTable  # noqa: E402
from .create_sessions_table import CreateSessionsTable  # noqa: E402
from .create_artifacts_table import CreateArtifactsTable  # noqa: E402


# Migration registry (in order of execution)
MIGRATIONS = [
    ('2025_11_26_000001_create_roles_table', CreateRolesTable),
    ('2025_11_26_000002_create_users_table', CreateUsersTable),
    ('2025_11_26_000003_create_sessions_table', CreateSessionsTable),
    ('2025_11_26_000004_create_artifacts_table', CreateArtifactsTable),
]


# Export migration classes
__all__ = [
    'CreateRolesTable',
    'CreateUsersTable',
    'CreateSessionsTable',
    'CreateArtifactsTable',
    'MIGRATIONS',
    'run_all_migrations',
    'rollback_last_migration',
    'rollback_migration',
    'run_migration',
    'rollback_all_migrations',
    'get_migration_status',
]


def run_all_migrations():
    """Run all pending migrations"""
    db = get_documentdb()
    runner = MigrationRunner(db)

    print("=" * 60)
    print("Running Database Migrations")
    print("=" * 60)

    for migration_name, migration_class in MIGRATIONS:
        runner.run(migration_class, migration_name)

    print("=" * 60)
    print("✓ All migrations completed successfully")
    print("=" * 60)


def rollback_last_migration():
    """Rollback the last migration"""
    db = get_documentdb()
    runner = MigrationRunner(db)

    # Get all migrations
    run_migrations = runner.get_migrations()
    if not run_migrations:
        print("⊘ No migrations to rollback")
        return

    # Get last migration
    last_migration = run_migrations[-1]
    migration_name = last_migration['name']

    # Find migration class
    migration_class = None
    for name, cls in MIGRATIONS:
        if name == migration_name:
            migration_class = cls
            break

    if migration_class:
        runner.rollback(migration_class, migration_name)
    else:
        print(f"⚠ Migration class not found for: {migration_name}")


def rollback_migration(migration_name: str):
    """Rollback a specific migration by name"""
    db = get_documentdb()
    runner = MigrationRunner(db)

    # Find migration class
    migration_class = None
    for name, cls in MIGRATIONS:
        if name == migration_name:
            migration_class = cls
            break

    if migration_class:
        runner.rollback(migration_class, migration_name)
    else:
        print(f"✗ Unknown migration: {migration_name}")
        print("\nAvailable migrations:")
        for name, _ in MIGRATIONS:
            print(f"  - {name}")


def run_migration(migration_name: str):
    """Run a specific migration by name"""
    db = get_documentdb()
    runner = MigrationRunner(db)

    # Find migration class
    migration_class = None
    for name, cls in MIGRATIONS:
        if name == migration_name:
            migration_class = cls
            break

    if migration_class:
        runner.run(migration_class, migration_name)
    else:
        print(f"✗ Unknown migration: {migration_name}")
        print("\nAvailable migrations:")
        for name, _ in MIGRATIONS:
            print(f"  - {name}")


def rollback_all_migrations():
    """Rollback all migrations in reverse order"""
    db = get_documentdb()
    runner = MigrationRunner(db)

    print("=" * 60)
    print("Rolling Back All Migrations")
    print("=" * 60)

    # Rollback in reverse order
    for migration_name, migration_class in reversed(MIGRATIONS):
        if runner.has_run(migration_name):
            runner.rollback(migration_class, migration_name)
    
    print("=" * 60)
    print("✓ All migrations rolled back")
    print("=" * 60)


def get_migration_status():
    """Display migration status"""
    db = get_documentdb()
    runner = MigrationRunner(db)

    run_migrations = runner.get_migrations()
    run_names = {m['name'] for m in run_migrations}

    print("=" * 60)
    print("Migration Status")
    print("=" * 60)

    for migration_name, _ in MIGRATIONS:
        if migration_name in run_names:
            print(f"  ✓ {migration_name}")
        else:
            print(f"  ⊘ {migration_name} (pending)")

    print("=" * 60)
    print(f"Total: {len(MIGRATIONS)} migrations")
    print(f"Run: {len(run_migrations)}")
    print(f"Pending: {len(MIGRATIONS) - len(run_migrations)}")
    print("=" * 60)
