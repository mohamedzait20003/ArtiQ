"""
Include module for lib initialization
Provides access to library components
"""

import sys
from pathlib import Path

# Add backend root to Python path to find lib module
backend_root = Path(__file__).parent.parent.parent.parent
lambda_service_root = Path(__file__).parent.parent

if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))
if str(lambda_service_root) not in sys.path:
    sys.path.insert(0, str(lambda_service_root))

from lib.route import Route  # noqa: E402
from lib.container import Container, container  # noqa: E402
from lib.eloquent import Eloquent  # noqa: E402
from lib.pipeline import (  # noqa: E402
    Pipeline,
    Parallel,
    ParallelGroup,
    PipelineException,
    pipeline,
    parallel
)
from lib.aws import (  # noqa: E402
    AWSServices,
    get_documentdb,
    get_collection,
    get_s3,
    get_lambda,
    get_sqs
)
from lib.encryption import (  # noqa: E402
    encrypt,
    decrypt,
    encrypt_artifact_id,
    decrypt_artifact_id,
    get_encryption_key,
    generate_encryption_key
)
from lib.relationships import (  # noqa: E402
    belongs_to,
    has_one,
    has_many,
    has_one_through,
    BelongsTo,
    HasOne,
    HasMany,
    HasOneThrough,
    active_session_filter
)
from lib.migration import (  # noqa: E402
    Migration,
    MigrationRunner,
    create_migration_runner,
    run_migration,
    rollback_migration
)
from lib.seeder import (  # noqa: E402
    Seeder,
    DatabaseSeeder,
    SeederRunner,
    create_seeder_runner,
    run_seeder,
    seed_database
)

__all__ = [
    'Route',
    'Container',
    'container',
    'Eloquent',
    'Pipeline',
    'Parallel',
    'ParallelGroup',
    'PipelineException',
    'pipeline',
    'parallel',
    'AWSServices',
    'get_documentdb',
    'get_collection',
    'get_s3',
    'get_lambda',
    'get_sqs',
    'encrypt',
    'decrypt',
    'encrypt_artifact_id',
    'decrypt_artifact_id',
    'get_encryption_key',
    'generate_encryption_key',
    'belongs_to',
    'has_one',
    'has_many',
    'has_one_through',
    'BelongsTo',
    'HasOne',
    'HasMany',
    'HasOneThrough',
    'active_session_filter',
    'Migration',
    'MigrationRunner',
    'create_migration_runner',
    'run_migration',
    'rollback_migration',
    'Seeder',
    'DatabaseSeeder',
    'SeederRunner',
    'create_seeder_runner',
    'run_seeder',
    'seed_database'
]
