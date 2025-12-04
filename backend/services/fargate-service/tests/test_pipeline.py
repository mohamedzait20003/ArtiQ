"""
Test for Pipeline functionality in fargate service
"""
import sys
from pathlib import Path

# Add backend lib to sys.path to import pipeline module directly
backend_lib = Path(__file__).parent.parent.parent.parent / 'lib'
if str(backend_lib) not in sys.path:
    sys.path.insert(0, str(backend_lib))

# Import pipeline module directly (avoiding lib/__init__.py imports)
import pipeline  # noqa: E402

Pipeline = pipeline.Pipeline


def step_add_one(x):
    """Add 1 to input"""
    return x + 1


def step_double(x):
    """Double the input"""
    return x * 2


def step_square(x):
    """Square the input"""
    return x * x


def test_simple_pipeline():
    """Test basic pipeline with two steps"""
    pipe = Pipeline()
    result = pipe.pipe(step_add_one).pipe(step_double).run(3)
    # (3 + 1) * 2 = 8
    assert result == 8


def test_pipeline_single_step():
    """Test pipeline with single step"""
    pipe = Pipeline()
    result = pipe.pipe(step_add_one).run(5)
    assert result == 6


def test_pipeline_empty_input():
    """Test pipeline with zero as input"""
    pipe = Pipeline()
    result = pipe.pipe(step_add_one).pipe(step_double).run(0)
    # (0 + 1) * 2 = 2
    assert result == 2


def test_pipeline_three_steps():
    """Test pipeline with three steps"""
    pipe = Pipeline()
    result = (pipe
              .pipe(step_add_one)
              .pipe(step_double)
              .pipe(step_square)
              .run(2))
    # ((2 + 1) * 2) ^ 2 = 6 ^ 2 = 36
    assert result == 36


def test_pipeline_send_method():
    """Test pipeline using send() method"""
    pipe = Pipeline()
    result = (pipe
              .send(10)
              .pipe(step_add_one)
              .pipe(step_double)
              .execute())
    # (10 + 1) * 2 = 22
    assert result == 22


def test_pipeline_then_alias():
    """Test pipeline using then() alias"""
    pipe = Pipeline()
    result = (pipe
              .then(step_add_one)
              .then(step_double)
              .run(4))
    # (4 + 1) * 2 = 10
    assert result == 10


# To run these tests:
#   cd services/fargate-service
#   pytest tests/test_pipeline.py -v
