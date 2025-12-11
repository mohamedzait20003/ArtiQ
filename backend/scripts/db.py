#!/usr/bin/env python3
"""
Database Management Script
Fresh migrations, reset, and full database management

Usage:
    python scripts/db.py [command]

Commands:
    fresh   - Drop all collections, run migrations, run seeders
    reset   - Rollback all migrations, run migrations, run seeders
    wipe    - Drop all collections (destructive!)

Examples:
    python scripts/db.py fresh
    python scripts/db.py reset
    python scripts/db.py wipe
"""

import sys
import traceback
from pathlib import Path

# Add backend root to path FIRST
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# Load environment variables
from dotenv import load_dotenv  # noqa: E402
env_path = backend_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")

from lib import get_documentdb  # noqa: E402


def db_fresh():
    """Drop all collections, run migrations, run seeders"""

    try:
        print("→ Running db:fresh...")

        # Drop all collections
        print("→ Dropping all collections...")
        from lib import get_documentdb
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

        print("\n✓ Database fresh complete")
    except Exception as e:
        print(f"\n✗ Database fresh failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def db_reset():
    """Rollback all migrations, run migrations, run seeders"""
    backend_root = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_root))

    try:
        print("→ Running db:reset...")

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

        print("\n✓ Database reset complete")
    except Exception as e:
        print(f"\n✗ Database reset failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def db_wipe():
    """Drop all collections (destructive!)"""
    backend_root = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_root))

    try:
        # Confirmation
        confirm = input(
            "⚠ WARNING: This will delete ALL data!\n"
            "Type 'yes' to continue: "
        )
        if confirm.lower() != 'yes':
            print("Aborted.")
            return

        print("→ Wiping database...")
        db = get_documentdb()

        collections = db.list_collection_names()
        for collection in collections:
            db.drop_collection(collection)
            print(f"  ✓ Dropped: {collection}")

        print("\n✓ Database wiped")
    except Exception as e:
        print(f"\n✗ Database wipe failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/db.py [command]")
        print("\nCommands:")
        print("  fresh  - Drop all collections, run migrations, seeders")
        print("  reset  - Rollback migrations, run migrations, seeders")
        print("  wipe   - Drop all collections (destructive!)")
        print("\nExamples:")
        print("  python scripts/db.py fresh")
        print("  python scripts/db.py reset")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'fresh':
        db_fresh()
    elif command == 'reset':
        db_reset()
    elif command == 'wipe':
        db_wipe()
    else:
        print(f"✗ Unknown command: {command}")
        print("Available commands: fresh, reset, wipe")
        sys.exit(1)


if __name__ == "__main__":
    main()
