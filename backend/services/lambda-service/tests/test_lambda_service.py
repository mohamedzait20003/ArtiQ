import pytest

# This file was split into focused test modules; keep the original around for
# history but skip running it to avoid duplicate tests. See the new files in the
# same directory (test_simple_endpoints.py, test_artifacts_list.py,
# test_registry_reset.py, test_artifact_create.py, and test_artifact_* for CRUD).
pytest.skip("Original combined test file skipped — use split modules instead", allow_module_level=True)