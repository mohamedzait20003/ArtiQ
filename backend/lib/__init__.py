"""
Library Module
Core utilities and routing infrastructure
"""

# Lazy import Route to avoid FastAPI dependency in non-web contexts
try:
    from .route import Route
except ImportError:
    Route = None

from .container import Container, container
from .eloquent import Eloquent
from .cache import Cache, CacheManager, cache  # noqa: F401
from .pipeline import (
    Pipeline,
    Parallel,
    ParallelGroup,
    PipelineException,
    pipeline,
    parallel
)
from .aws import (
    AWSServices,
    get_documentdb,
    get_collection,
    get_s3,
    get_lambda,
    get_ecs
)
from .relationships import (  # noqa: F401
    belong_to_one,
    has_one,
    has_many,
    has_one_through,
    BelongToOne,
    HasOne,
    HasMany,
    HasOneThrough,
    active_session_filter
)
try:
    from .migration import (
        Migration,
        MigrationRunner,
        create_migration_runner,
        run_migration,
        rollback_migration
    )
except ImportError:
    Migration = None
    MigrationRunner = None
    create_migration_runner = None
    run_migration = None
    rollback_migration = None

try:
    from .seeder import (
        Seeder,
        DatabaseSeeder,
        SeederRunner,
        create_seeder_runner,
        run_seeder,
        seed_database
    )
except ImportError:
    Seeder = None
    DatabaseSeeder = None
    SeederRunner = None
    create_seeder_runner = None
    run_seeder = None
    seed_database = None
from .encryption import (
    get_encryption_key,
    generate_encryption_key,
    encrypt,
    decrypt,
    encrypt_artifact_id,
    decrypt_artifact_id
)

__all__ = [
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
    'get_ecs',
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
    'active_session_filter'
]

# Conditionally add Route export if available
if Route is not None:
    __all__.insert(0, 'Route')

# Conditionally add migration exports if available
if Migration is not None:
    __all__.extend([
        'Migration',
        'MigrationRunner',
        'create_migration_runner',
        'run_migration',
        'rollback_migration'
    ])

# Conditionally add seeder exports if available
if Seeder is not None:
    __all__.extend([
        'Seeder',
        'DatabaseSeeder',
        'SeederRunner',
        'create_seeder_runner',
        'run_seeder',
        'seed_database'
    ])
