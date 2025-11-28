#!/usr/bin/env python3
"""
Global Migration Script
Run database migrations for any service

Usage:
    python scripts/migrate.py [service_name] [options]
    python scripts/migrate.py [service_name] --name [migration_name]

Examples:
    python scripts/migrate.py lambda-service
    python scripts/migrate.py lambda-service --rollback
    python scripts/migrate.py lambda-service --status
    python scripts/migrate.py lambda-service --name create_users_table
    python scripts/migrate.py lambda-service --rollback --name
        create_users_table
"""

import sys
import traceback
from pathlib import Path
from typing import Optional


def get_service_path(service_name: str) -> Path:
    """Get the service directory path"""
    backend_root = Path(__file__).parent.parent
    service_path = backend_root / 'services' / service_name

    if not service_path.exists():
        raise ValueError(f"Service not found: {service_name}")

    return service_path


def run_migrations(
    service_name: str,
    rollback: bool = False,
    status: bool = False,
    migration_name: Optional[str] = None
):
    """Run migrations for a specific service"""
    backend_root = Path(__file__).parent.parent
    service_path = get_service_path(service_name)

    # Add backend root and service to path
    sys.path.insert(0, str(backend_root))
    sys.path.insert(0, str(service_path))

    # Import service-specific migration functions
    try:
        if status:
            from database.migrations import get_migration_status
            print(f"→ Getting migration status for {service_name}...")
            get_migration_status()
        elif rollback:
            if migration_name:
                from database.migrations import rollback_migration
                msg = (
                    f"→ Rolling back migration '{migration_name}' "
                    f"for {service_name}..."
                )
                print(msg)
                rollback_migration(migration_name)
                print(f"✓ Rollback complete for {service_name}")
            else:
                from database.migrations import (
                    rollback_last_migration
                )
                msg = f"→ Rolling back last migration for {service_name}..."
                print(msg)
                rollback_last_migration()
                print(f"✓ Rollback complete for {service_name}")
        else:
            if migration_name:
                from database.migrations import run_migration
                msg = (
                    f"→ Running migration '{migration_name}' "
                    f"for {service_name}..."
                )
                print(msg)
                run_migration(migration_name)
                msg = (
                    f"✓ Migration '{migration_name}' complete "
                    f"for {service_name}"
                )
                print(msg)
            else:
                from database.migrations import run_all_migrations
                print(f"→ Running all migrations for {service_name}...")
                run_all_migrations()
                print(f"✓ All migrations complete for {service_name}")
    except ImportError as e:
        print(f"✗ Error: Could not import migrations for {service_name}")
        print("  Make sure database/migrations/__init__.py exists")
        print(f"  Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/migrate.py [service_name] [options]")
        print("\nAvailable services:")
        print("  - lambda-service")
        print("  - fargate-service")
        print("\nOptions:")
        print("  --rollback    Rollback last or specific migration")
        print("  --status      Show migration status")
        print("  --name [name] Run/rollback specific migration by name")
        print("\nExamples:")
        print("  python scripts/migrate.py lambda-service")
        print("  python scripts/migrate.py lambda-service --rollback")
        print("  python scripts/migrate.py lambda-service --status")
        msg = (
            "  python scripts/migrate.py lambda-service "
            "--name create_users_table"
        )
        print(msg)
        sys.exit(1)
    
    service_name = sys.argv[1]
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

    run_migrations(service_name, rollback, status, migration_name)


if __name__ == "__main__":
    main()
