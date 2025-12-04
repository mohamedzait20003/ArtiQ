"""
Test for lib.pipeline.Pipeline usage in fargate service
"""
import sys
from pathlib import Path

backend_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_root))


from lib.pipeline import Pipeline # noqa: E402


def step_add_one(x):
    return x + 1


def step_double(x):
    return x * 2

def test_simple_pipeline():
    pipeline = Pipeline([
        step_add_one,
        step_double
    ])
    result = pipeline.run(3)
    assert result == 8

# To run this test, use:
#   pytest tests/test_pipeline.py -v
