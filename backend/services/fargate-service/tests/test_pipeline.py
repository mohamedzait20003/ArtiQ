import pytest
from include import Pipeline, parallel


# =============================================================================
# Pipeline-specific Test Fixtures
# =============================================================================
@pytest.fixture
def sample_context():
    """Sample pipeline context dictionary"""
    return {
        'initial': 10,
        'results': [11, 22],
        'last': 22
    }


@pytest.fixture
def step_functions():
    """Common step functions for pipeline testing"""
    def step_add_one(context):
        """Add 1 to the last result or initial value"""
        value = context.get('last') or context.get('initial', 0)
        return value + 1

    def step_double(context):
        """Double the last result"""
        value = context.get('last') or context.get('initial', 0)
        return value * 2

    def step_square(context):
        """Square the last result"""
        value = context.get('last') or context.get('initial', 0)
        return value * value

    def step_subtract_five(context):
        """Subtract 5 from the last result"""
        value = context.get('last') or context.get('initial', 0)
        return value - 5

    return {
        'add_one': step_add_one,
        'double': step_double,
        'square': step_square,
        'subtract_five': step_subtract_five
    }


# =============================================================================
# Pipeline Tests
# =============================================================================

def test_simple_pipeline(step_functions):
    """Test basic pipeline with two steps"""
    result = Pipeline(
        step_functions['add_one'],
        step_functions['double']
    ).start(3)
    # (3 + 1) * 2 = 8
    assert result == 8


def test_pipeline_single_step(step_functions):
    """Test pipeline with single step"""
    result = Pipeline(step_functions['add_one']).start(5)
    assert result == 6


def test_pipeline_empty_input(step_functions):
    """Test pipeline with zero as input"""
    result = Pipeline(
        step_functions['add_one'],
        step_functions['double']
    ).start(0)
    # (0 + 1) * 2 = 2
    assert result == 2


def test_pipeline_three_steps(step_functions):
    """Test pipeline with three steps"""
    result = Pipeline(
        step_functions['add_one'],
        step_functions['double'],
        step_functions['square']
    ).start(2)
    # ((2 + 1) * 2) ^ 2 = 6 ^ 2 = 36
    assert result == 36


def test_pipeline_send_method(step_functions):
    """Test pipeline using send() method (backward compatibility)"""
    pipe = Pipeline(
        step_functions['add_one'],
        step_functions['double']
    )
    result = pipe.send(10).execute()
    # (10 + 1) * 2 = 22
    assert result == 22


def test_pipeline_then_alias(step_functions):
    """Test pipeline using then() for adding steps dynamically"""
    pipe = Pipeline()
    result = (pipe
              .then(step_functions['add_one'])
              .then(step_functions['double'])
              .run(4))
    # (4 + 1) * 2 = 10
    assert result == 10


def test_pipeline_with_parallel(step_functions):
    """Test pipeline with parallel execution"""
    def sum_parallel_results(context):
        """Sum results from parallel execution"""
        last = context.get('last', [])
        if isinstance(last, list):
            return sum(last)
        return last
    
    result = Pipeline(
        step_functions['add_one'],
        parallel(
            step_functions['double'],
            step_functions['square'],
            step_functions['subtract_five']
        ),
        sum_parallel_results
    ).start(3)
    # Initial: 3
    # Step 1: 3 + 1 = 4
    # Parallel: [4*2=8, 4*4=16, 4-5=-1]
    # Final: sum([8, 16, -1]) = 23
    assert result == 23


def test_pipeline_access_all_results(step_functions):
    """Test that functions can access all previous results"""
    def sum_all(context):
        """Sum all previous results"""
        results = context.get('results', [])
        return sum(results) if results else 0
    
    result = Pipeline(
        step_functions['add_one'],   # 3 + 1 = 4
        step_functions['double'],    # 4 * 2 = 8
        step_functions['square'],    # 8 * 8 = 64
        sum_all                      # 4 + 8 + 64 = 76
    ).start(3)
    assert result == 76


def test_pipeline_access_initial_value(step_functions):
    """Test that functions can access the initial value"""
    def return_initial(context):
        """Return the initial value"""
        return context.get('initial')
    
    result = Pipeline(
        step_functions['add_one'],
        step_functions['double'],
        return_initial
    ).start(10)
    assert result == 10


def test_context_structure(sample_context):
    """Test that context has the correct structure"""
    def check_context(context):
        """Verify context has all required keys"""
        assert 'initial' in context
        assert 'results' in context
        assert 'last' in context
        assert isinstance(context['results'], list)
        return context['initial']
    
    result = Pipeline(check_context).start(42)
    assert result == 42


def test_parallel_functions_receive_context():
    """Test that parallel functions receive proper context"""
    def parallel_func1(context):
        """Return initial value"""
        return context.get('initial', 0) * 2
    
    def parallel_func2(context):
        """Return last value or initial"""
        value = context.get('last') or context.get('initial', 0)
        return value + 10
    
    result = Pipeline(
        parallel(parallel_func1, parallel_func2)
    ).start(5)
    # parallel_func1: 5 * 2 = 10
    # parallel_func2: 5 + 10 = 15
    # Result: [10, 15]
    assert result == [10, 15]


def test_complex_pipeline_with_multiple_parallel():
    """Test complex pipeline with multiple parallel stages"""
    def add_ten(context):
        value = context.get('last') or context.get('initial', 0)
        return value + 10
    
    def multiply_two(context):
        value = context.get('last') or context.get('initial', 0)
        if isinstance(value, list):
            return sum(value) * 2
        return value * 2
    
    def subtract_three(context):
        value = context.get('last') or context.get('initial', 0)
        return value - 3
    
    def get_first_result(context):
        results = context.get('results', [])
        return results[0] if results else 0
    
    result = Pipeline(
        add_ten,                                    # 5 + 10 = 15
        parallel(multiply_two, subtract_three),     # [15*2=30, 15-3=12]
        get_first_result                            # returns 15
    ).start(5)
    assert result == 15


# To run these tests:
#   cd services/fargate-service
#   pytest tests/test_pipeline.py -v
