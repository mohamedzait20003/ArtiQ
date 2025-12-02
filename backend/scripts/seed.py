#!/usr/bin/env python3
"""
Global Seeding Script
Run database seeders globally

Usage:
    python scripts/seed.py [options]
    python scripts/seed.py --name [seeder_name]

Examples:
    python scripts/seed.py
    python scripts/seed.py --force
    python scripts/seed.py --name UserSeeder
"""

import sys
import traceback
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
backend_root = Path(__file__).parent.parent
load_dotenv(backend_root / '.env')


def run_seeders(
    force: bool = False,
    seeder_name: Optional[str] = None
):
    """Run seeders globally"""
    backend_root = Path(__file__).parent.parent

    # Add backend root to path
    sys.path.insert(0, str(backend_root))

    # Import global seeder functions
    try:
        if seeder_name:
            from database.seeders import run_seeder
            print(f"→ Running seeder '{seeder_name}'...")
            run_seeder(seeder_name, force=force)
            print(f"✓ Seeder '{seeder_name}' complete")
        else:
            from database.seeders import run_all_seeders
            print("→ Running all seeders...")
            run_all_seeders(force=force)
            print("✓ All seeders complete")
    except ImportError as e:
        print("✗ Error: Could not import seeders")
        print("  Make sure database/seeders/__init__.py exists")
        print(f"  Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Seeding failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python scripts/seed.py [options]")
        print("\nOptions:")
        print("  --force         Run seeders even if already run")
        print("  --name [name]   Run specific seeder by name")
        print("\nExamples:")
        print("  python scripts/seed.py")
        print("  python scripts/seed.py --force")
        print("  python scripts/seed.py --name UserSeeder")
        sys.exit(0)
    
    force = '--force' in sys.argv

    # Get seeder name if specified
    seeder_name = None
    if '--name' in sys.argv:
        name_index = sys.argv.index('--name')
        if name_index + 1 < len(sys.argv):
            seeder_name = sys.argv[name_index + 1]
        else:
            print("✗ Error: --name requires a seeder name")
            sys.exit(1)

    run_seeders(force, seeder_name)


if __name__ == "__main__":
    main()
