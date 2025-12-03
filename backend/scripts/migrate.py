#!/usr/bin/env python3
"""
Global Migration Script
Run database migrations globally

Usage:
    python scripts/migrate.py [options]
    python scripts/migrate.py --name [migration_name]

Examples:
    python scripts/migrate.py
    python scripts/migrate.py --rollback
    python scripts/migrate.py --status
    python scripts/migrate.py --name create_users_table
    python scripts/migrate.py --rollback --name create_users_table
"""

import sys
import traceback
from pathlib import Path
from typing import Optional

# Add backend root to path FIRST
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# Load environment variables
from dotenv import load_dotenv  # noqa: E402
env_path = backend_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")


def run_migrations(
    rollback: bool = False,
    status: bool = False,
    migration_name: Optional[str] = None
):
    """Run migrations globally"""

    # Add backend root to path
    sys.path.insert(0, str(backend_root))

    # Import global migration functions
    try:
        if status:
            from database.migrations import get_migration_status
            print("→ Getting migration status...")
            get_migration_status()
        elif rollback:
            if migration_name:
                from database.migrations import rollback_migration
                print(f"→ Rolling back migration '{migration_name}'...")
                rollback_migration(migration_name)
                print("✓ Rollback complete")
            else:
                from database.migrations import (
                    rollback_last_migration
                )
                print("→ Rolling back last migration...")
                rollback_last_migration()
                print("✓ Rollback complete")
        else:
            if migration_name:
                from database.migrations import run_migration
                print(f"→ Running migration '{migration_name}'...")
                run_migration(migration_name)
                print(f"✓ Migration '{migration_name}' complete")
            else:
                from database.migrations import run_all_migrations
                print("→ Running all migrations...")
                run_all_migrations()
                print("✓ All migrations complete")
    except ImportError as e:
        print("✗ Error: Could not import migrations")
        print("  Make sure database/migrations/__init__.py exists")
        print(f"  Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python scripts/migrate.py [options]")
        print("\nOptions:")
        print("  --rollback    Rollback last or specific migration")
        print("  --status      Show migration status")
        print("  --name [name] Run/rollback specific migration by name")
        print("\nExamples:")
        print("  python scripts/migrate.py")
        print("  python scripts/migrate.py --rollback")
        print("  python scripts/migrate.py --status")
        print("  python scripts/migrate.py --name create_users_table")
        sys.exit(0)

    rollback = '--rollback' in sys.argv
    status = '--status' in sys.argv

    # Get migration name if specified
    migration_name = None
    if '--name' in sys.argv:
        name_index = sys.argv.index('--name')
        if name_index + 1 < len(sys.argv):
            migration_name = sys.argv[name_index + 1]
        else:
            print("✗ Error: --name requires a migration name")
            sys.exit(1)

    run_migrations(rollback, status, migration_name)


if __name__ == "__main__":
    main()
