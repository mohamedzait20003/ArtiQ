"""
Jobs Module
Contains Lambda handler functions for various operations
"""

from .user_authenticate import lambda_handler as authenticate_job
from .user_logout import lambda_handler as logout_job
from .user_create import lambda_handler as create_user_job
from .user_register import lambda_handler as register_job
from .user_login import lambda_handler as login_job
from .user_list import lambda_handler as user_list_job
from .artifacts_list import lambda_handler as artifacts_list_job
from .artifact_create import lambda_handler as artifact_create_job
from .artifact_retrieve import lambda_handler as artifact_retrieve_job
from .artifact_update import lambda_handler as artifact_update_job
from .artifact_delete import lambda_handler as artifact_delete_job
from .artifact_by_regex import lambda_handler as artifact_by_regex_job
from .artifact_by_name import lambda_handler as artifact_by_name_job
from .artifact_by_type_and_name import (
    lambda_handler as artifact_by_type_and_name_job
)
from .artifact_first_ten_by_type import (
    lambda_handler as artifact_first_ten_by_type_job
)
from .registry_reset import lambda_handler as registry_reset_job
from .model_artifact_rate import lambda_handler as model_artifact_rate_job
from .artifact_cost import lambda_handler as artifact_cost_job
from .artifact_license_check import (
    lambda_handler as artifact_license_check_job
)
from .artifact_lineage_get import (
    lambda_handler as artifact_lineage_get_job
)

__all__ = [
    'authenticate_job',
    'logout_job',
    'create_user_job',
    'register_job',
    'login_job',
    'user_list_job',
    'artifacts_list_job',
    'artifact_create_job',
    'artifact_retrieve_job',
    'artifact_update_job',
    'artifact_delete_job',
    'artifact_by_regex_job',
    'artifact_by_name_job',
    'artifact_by_type_and_name_job',
    'artifact_first_ten_by_type_job',
    'registry_reset_job',
    'model_artifact_rate_job',
    'artifact_cost_job',
    'artifact_license_check_job',
    'artifact_lineage_get_job',
]
