#!/usr/bin/env python3
"""
Service Runner Script
Start development servers for services

Usage:
    python scripts/run.py [service_name] [options]

Options:
    --port [port]   Specify port
                    (default: 8000 for lambda, 8001 for fargate)
    --host [host]   Specify host (default: 0.0.0.0)
    --no-reload     Disable auto-reload

Examples:
    python scripts/run.py lambda-service
    python scripts/run.py lambda-service --port 8080
    python scripts/run.py fargate-service
    python scripts/run.py lambda-service --no-reload
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional


def get_service_path(service_name: str) -> Path:
    """Get the service directory path"""
    backend_root = Path(__file__).parent.parent
    service_path = backend_root / 'services' / service_name
    
    if not service_path.exists():
        raise ValueError(f"Service not found: {service_name}")
    
    return service_path


def run_service(
    service_name: str,
    port: Optional[int] = None,
    host: str = "0.0.0.0",
    reload: bool = True
):
    """Run a service in development mode"""
    service_path = get_service_path(service_name)

    # Determine default port and app module based on service
    if service_name == 'lambda-service':
        default_port = 8000
        app_module = 'app.main:app'
    elif service_name == 'fargate-service':
        default_port = 8001
        app_module = 'src.main:app'
    else:
        print(f"✗ Unknown service configuration: {service_name}")
        sys.exit(1)

    port = port or default_port

    # Build uvicorn command
    cmd = [
        'uvicorn',
        app_module,
        '--host', host,
        '--port', str(port)
    ]

    if reload:
        cmd.append('--reload')

    print(f"→ Starting {service_name} on {host}:{port}...")
    print(f"  Command: {' '.join(cmd)}")
    print(f"  Working directory: {service_path}")
    print()

    try:
        subprocess.run(cmd, cwd=service_path, check=True)
    except KeyboardInterrupt:
        print(f"\n✓ Stopped {service_name}")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Service failed: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run.py [service_name] [options]")
        print("\nAvailable services:")
        print("  - lambda-service   (default port: 8000)")
        print("  - fargate-service  (default port: 8001)")
        print("\nOptions:")
        print("  --port [port] Specify port")
        print("  --host [host] Specify host (default: 0.0.0.0)")
        print("  --no-reload   Disable auto-reload")
        print("\nExamples:")
        print("  python scripts/run.py lambda-service")
        print("  python scripts/run.py lambda-service --port 8080")
        print("  python scripts/run.py fargate-service")
        sys.exit(1)
    
    service_name = sys.argv[1]

    # Parse options
    port = None
    host = "0.0.0.0"
    reload = True

    if '--port' in sys.argv:
        port_index = sys.argv.index('--port')
        if port_index + 1 < len(sys.argv):
            port = int(sys.argv[port_index + 1])
        else:
            print("✗ Error: --port requires a port number")
            sys.exit(1)

    if '--host' in sys.argv:
        host_index = sys.argv.index('--host')
        if host_index + 1 < len(sys.argv):
            host = sys.argv[host_index + 1]
        else:
            print("✗ Error: --host requires a host address")
            sys.exit(1)

    if '--no-reload' in sys.argv:
        reload = False

    run_service(service_name, port, host, reload)


if __name__ == "__main__":
    main()
