#!/usr/bin/env python3
"""
Global Seeding Script
Run database seeders for any service

Usage:
    python scripts/seed.py [service_name] [options]
    python scripts/seed.py [service_name] --name [seeder_name]

Examples:
    python scripts/seed.py lambda-service
    python scripts/seed.py lambda-service --force
    python scripts/seed.py lambda-service --name UserSeeder
    python scripts/seed.py fargate-service
"""

import sys
import traceback
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
backend_root = Path(__file__).parent.parent
load_dotenv(backend_root / '.env')


def get_service_path(service_name: str) -> Path:
    """Get the service directory path"""
    backend_root = Path(__file__).parent.parent
    service_path = backend_root / 'services' / service_name

    if not service_path.exists():
        raise ValueError(f"Service not found: {service_name}")

    return service_path


def run_seeders(
    service_name: str,
    force: bool = False,
    seeder_name: Optional[str] = None
):
    """Run seeders for a specific service"""
    backend_root = Path(__file__).parent.parent
    service_path = get_service_path(service_name)

    # Add backend root and service to path
    sys.path.insert(0, str(backend_root))
    sys.path.insert(0, str(service_path))

    # Import service-specific seeder functions
    try:
        if seeder_name:
            from database.seeders import run_seeder
            msg = (
                f"→ Running seeder '{seeder_name}' "
                f"for {service_name}..."
            )
            print(msg)
            run_seeder(seeder_name, force=force)
            msg = (
                f"✓ Seeder '{seeder_name}' complete "
                f"for {service_name}"
            )
            print(msg)
        else:
            from database.seeders import run_all_seeders
            print(f"→ Running all seeders for {service_name}...")
            run_all_seeders(force=force)
            print(f"✓ All seeders complete for {service_name}")
    except ImportError as e:
        print(f"✗ Error: Could not import seeders for {service_name}")
        print("  Make sure database/seeders/__init__.py exists")
        print(f"  Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Seeding failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed.py [service_name] [options]")
        print("\nAvailable services:")
        print("  - lambda-service")
        print("  - fargate-service")
        print("\nOptions:")
        print("  --force         Run seeders even if already run")
        print("  --name [name]   Run specific seeder by name")
        print("\nExamples:")
        print("  python scripts/seed.py lambda-service")
        print("  python scripts/seed.py lambda-service --force")
        print("  python scripts/seed.py lambda-service --name UserSeeder")
        sys.exit(1)
    
    service_name = sys.argv[1]
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

    run_seeders(service_name, force, seeder_name)


if __name__ == "__main__":
    main()
