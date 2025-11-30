#!/usr/bin/env python3
"""
Database Management Script
Fresh migrations, reset, and full database management

Usage:
    python scripts/db.py [service_name] [command]

Commands:
    fresh   - Drop all collections, run migrations, run seeders
    reset   - Rollback all migrations, run migrations, run seeders
    wipe    - Drop all collections (destructive!)

Examples:
    python scripts/db.py lambda-service fresh
    python scripts/db.py lambda-service reset
    python scripts/db.py lambda-service wipe
"""

import sys
import traceback
from pathlib import Path


def get_service_path(service_name: str) -> Path:
    """Get the service directory path"""
    backend_root = Path(__file__).parent.parent
    service_path = backend_root / 'services' / service_name
    
    if not service_path.exists():
        raise ValueError(f"Service not found: {service_name}")
    
    return service_path


def db_fresh(service_name: str):
    """Drop all collections, run migrations, run seeders"""
    service_path = get_service_path(service_name)
    sys.path.insert(0, str(service_path))

    try:
        print(f"→ Running db:fresh for {service_name}...")

        # Drop all collections
        print("→ Dropping all collections...")
        from app.include import get_documentdb
        db = get_documentdb()
        for collection in db.list_collection_names():
            if collection != 'migrations':
                db.drop_collection(collection)
                print(f"  ✓ Dropped: {collection}")

        # Run migrations
        print("\n→ Running migrations...")
        from database.migrations import run_all_migrations
        run_all_migrations()

        # Run seeders
        print("\n→ Running seeders...")
        from database.seeders import run_all_seeders
        run_all_seeders(force=True)

        print(f"\n✓ Database fresh complete for {service_name}")
    except Exception as e:
        print(f"\n✗ Database fresh failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def db_reset(service_name: str):
    """Rollback all migrations, run migrations, run seeders"""
    service_path = get_service_path(service_name)
    sys.path.insert(0, str(service_path))

    try:
        print(f"→ Running db:reset for {service_name}...")

        # Rollback all migrations
        print("→ Rolling back all migrations...")
        from database.migrations import rollback_all_migrations
        rollback_all_migrations()

        # Run migrations
        print("\n→ Running migrations...")
        from database.migrations import run_all_migrations
        run_all_migrations()

        # Run seeders
        print("\n→ Running seeders...")
        from database.seeders import run_all_seeders
        run_all_seeders(force=True)

        print(f"\n✓ Database reset complete for {service_name}")
    except Exception as e:
        print(f"\n✗ Database reset failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def db_wipe(service_name: str):
    """Drop all collections (destructive!)"""
    service_path = get_service_path(service_name)
    sys.path.insert(0, str(service_path))

    try:
        # Confirmation
        confirm = input(
            f"⚠ WARNING: This will delete ALL data from "
            f"{service_name}!\nType 'yes' to continue: "
        )
        if confirm.lower() != 'yes':
            print("Aborted.")
            return

        print(f"→ Wiping database for {service_name}...")

        from app.include import get_documentdb
        db = get_documentdb()

        collections = db.list_collection_names()
        for collection in collections:
            db.drop_collection(collection)
            print(f"  ✓ Dropped: {collection}")

        print(f"\n✓ Database wiped for {service_name}")
    except Exception as e:
        print(f"\n✗ Database wipe failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/db.py [service_name] [command]")
        print("\nAvailable services:")
        print("  - lambda-service")
        print("  - fargate-service")
        print("\nCommands:")
        print("  fresh  - Drop all collections, run migrations, seeders")
        print("  reset  - Rollback migrations, run migrations, seeders")
        print("  wipe   - Drop all collections (destructive!)")
        print("\nExamples:")
        print("  python scripts/db.py lambda-service fresh")
        print("  python scripts/db.py lambda-service reset")
        sys.exit(1)
    
    service_name = sys.argv[1]
    command = sys.argv[2]
    
    if command == 'fresh':
        db_fresh(service_name)
    elif command == 'reset':
        db_reset(service_name)
    elif command == 'wipe':
        db_wipe(service_name)
    else:
        print(f"✗ Unknown command: {command}")
        print("Available commands: fresh, reset, wipe")
        sys.exit(1)


if __name__ == "__main__":
    main()
