"""
Pipeline Facade
Provides a fluent interface for executing sequential and parallel tasks
"""

import traceback
from typing import Callable, Any, List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, Future, as_completed


class PipelineException(Exception):
    """Exception raised when a pipeline task fails"""
    pass


class ParallelGroup:
    """
    Represents a group of tasks to be executed in parallel
    Created by the parallel() helper function
    """

    def __init__(self, *tasks: Callable, max_workers: Optional[int] = None):
        """
        Initialize parallel group

        Args:
            *tasks: Functions to execute in parallel
            max_workers: Maximum number of worker threads
        """
        self.tasks = tasks
        self.max_workers = max_workers

    def execute(self, data: Any = None) -> List[Any]:
        """
        Execute all tasks in parallel

        Args:
            data: Optional data to pass to all tasks as first argument

        Returns:
            List of results from all tasks

        Raises:
            PipelineException: If any task fails
        """
        results_dict = {}
        errors = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures: Dict[Future, int] = {}
            for idx, task in enumerate(self.tasks):
                if data is not None:
                    future = executor.submit(task, data)
                else:
                    future = executor.submit(task)
                futures[future] = idx

            # Collect results in order
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results_dict[idx] = result
                except Exception as e:
                    error_msg = (
                        f"Task {idx} failed: {str(e)}\n"
                        f"{traceback.format_exc()}"
                    )
                    errors.append(Exception(error_msg))

            # Check for errors
            if errors:
                error_messages = '\n'.join(str(e) for e in errors)
                raise PipelineException(
                    f"Parallel execution failed:\n{error_messages}"
                )

            # Return results in original task order
            return [results_dict[i] for i in sorted(results_dict.keys())]


class Parallel:
    """
    Parallel task executor within a pipeline
    Executes multiple tasks concurrently using multi-threading
    """

    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel executor

        Args:
            max_workers: Maximum number of worker threads
                        (default: None uses ThreadPoolExecutor default)
        """
        self.tasks: List[Dict[str, Any]] = []
        self.max_workers = max_workers
        self.results: List[Any] = []
        self.errors: List[Exception] = []

    def add(self, task: Callable, *args, **kwargs) -> 'Parallel':
        """
        Add a task to be executed in parallel

        Args:
            task: Callable function to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task

        Returns:
            Self for method chaining
        """
        self.tasks.append({
            'task': task,
            'args': args,
            'kwargs': kwargs
        })
        return self

    def execute(self, data: Any = None) -> List[Any]:
        """
        Execute all tasks in parallel

        Args:
            data: Optional data to pass to all tasks as first argument

        Returns:
            List of results from all tasks

        Raises:
            PipelineException: If any task fails
        """
        self.results = []
        self.errors = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures: Dict[Future, int] = {}
            for idx, task_info in enumerate(self.tasks):
                task = task_info['task']
                args = task_info['args']
                kwargs = task_info['kwargs']

                # Prepend data if provided
                if data is not None:
                    args = (data,) + args

                future = executor.submit(task, *args, **kwargs)
                futures[future] = idx

            # Collect results in order
            results_dict = {}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results_dict[idx] = result
                except Exception as e:
                    error_msg = (
                        f"Task {idx} failed: {str(e)}\n"
                        f"{traceback.format_exc()}"
                    )
                    self.errors.append(Exception(error_msg))

            # Check for errors
            if self.errors:
                error_messages = '\n'.join(str(e) for e in self.errors)
                raise PipelineException(
                    f"Parallel execution failed:\n{error_messages}"
                )

            # Return results in original task order
            self.results = [
                results_dict[i] for i in sorted(results_dict.keys())
            ]
            return self.results

    def get_results(self) -> List[Any]:
        """Get the results from the last execution"""
        return self.results

    def get_errors(self) -> List[Exception]:
        """Get any errors from the last execution"""
        return self.errors


class Pipeline:
    """
    Pipeline Facade
    Provides a fluent interface for building and executing
    sequential and parallel task workflows
    """

    def __init__(self):
        """Initialize an empty pipeline"""
        self.stages: List[Dict[str, Any]] = []
        self.data: Any = None
        self.results: List[Any] = []
        self._stop_on_error: bool = True

    def pipe(self, task: Callable, *args, **kwargs) -> 'Pipeline':
        """
        Add a sequential task to the pipeline

        Args:
            task: Callable function to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task

        Returns:
            Self for method chaining
        """
        self.stages.append({
            'type': 'sequential',
            'task': task,
            'args': args,
            'kwargs': kwargs
        })
        return self

    def parallel(
        self,
        tasks: List[Callable] = None,
        max_workers: Optional[int] = None
    ) -> 'Parallel':
        """
        Add parallel tasks to the pipeline

        Args:
            tasks: Optional list of callables to execute in parallel
            max_workers: Maximum number of worker threads

        Returns:
            Parallel object for adding tasks

        Example:
            pipeline.parallel()\\
                .add(task1, arg1)\\
                .add(task2, arg2)\\
                .add(task3, arg3)
        """
        parallel = Parallel(max_workers=max_workers)

        if tasks:
            for task in tasks:
                parallel.add(task)

        self.stages.append({
            'type': 'parallel',
            'executor': parallel
        })

        return parallel

    def then(self, task: Callable, *args, **kwargs) -> 'Pipeline':
        """
        Alias for pipe() - adds a sequential task

        Args:
            task: Callable function to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task

        Returns:
            Self for method chaining
        """
        return self.pipe(task, *args, **kwargs)

    def stop_on_error(self, stop: bool = True) -> 'Pipeline':
        """
        Configure whether to stop pipeline execution on error

        Args:
            stop: If True, stops on first error. If False, continues

        Returns:
            Self for method chaining
        """
        self._stop_on_error = stop
        return self

    def send(self, data: Any) -> 'Pipeline':
        """
        Set initial data to send through the pipeline

        Args:
            data: Initial data to pass to the first task

        Returns:
            Self for method chaining
        """
        self.data = data
        return self

    def execute(self, initial_data: Any = None) -> Any:
        """
        Execute the entire pipeline

        Args:
            initial_data: Optional initial data (overrides send())

        Returns:
            Final result from the pipeline

        Raises:
            PipelineException: If any stage fails and stop_on_error is True
        """
        if initial_data is not None:
            self.data = initial_data

        current_data = self.data
        self.results = []

        for idx, stage in enumerate(self.stages):
            try:
                if stage['type'] == 'sequential':
                    task = stage['task']
                    args = stage['args']
                    kwargs = stage['kwargs']

                    # Pass current data as first argument
                    if current_data is not None:
                        args = (current_data,) + args

                    result = task(*args, **kwargs)
                    current_data = result
                    self.results.append(result)

                elif stage['type'] == 'parallel':
                    executor = stage['executor']
                    results = executor.execute(current_data)
                    current_data = results
                    self.results.append(results)

            except Exception as e:
                error_msg = (
                    f"Stage {idx} ({stage['type']}) failed: {str(e)}\n"
                    f"{traceback.format_exc()}"
                )
                if self._stop_on_error:
                    raise PipelineException(error_msg)
                else:
                    print(f"Warning: {error_msg}")
                    continue

        return current_data

    def run(self, initial_data: Any = None) -> Any:
        """
        Alias for execute()

        Args:
            initial_data: Optional initial data

        Returns:
            Final result from the pipeline
        """
        return self.execute(initial_data)

    def get_results(self) -> List[Any]:
        """
        Get all intermediate results from pipeline execution

        Returns:
            List of results from each stage
        """
        return self.results

    def clear(self) -> 'Pipeline':
        """
        Clear all stages and reset the pipeline

        Returns:
            Self for method chaining
        """
        self.stages = []
        self.data = None
        self.results = []
        return self


def parallel(*tasks: Callable, max_workers: Optional[int] = None):
    """
    Create a parallel group of tasks

    Args:
        *tasks: Functions to execute in parallel
        max_workers: Maximum number of worker threads

    Returns:
        ParallelGroup object

    Example:
        result = pipeline(
            func1,
            func2,
            parallel(func3_1, func3_2, func3_3),
            func4
        )(initial_data)
    """
    return ParallelGroup(*tasks, max_workers=max_workers)


def pipeline(*stages) -> Callable:
    """
    Create a pipeline from a sequence of functions and parallel groups

    Args:
        *stages: Sequential functions or ParallelGroup objects

    Returns:
        A function that executes the pipeline when called with data

    Example:
        # Simple sequential
        result = pipeline(func1, func2, func3)(data)

        # With parallel execution
        result = pipeline(
            func1,
            parallel(func2_1, func2_2),
            func3
        )(data)

        # Multiple parallel stages
        result = pipeline(
            validate,
            parallel(enrich_a, enrich_b, enrich_c),
            transform,
            parallel(save_db, save_cache, send_event),
            finalize
        )(data)
    """

    def execute(initial_data: Any = None) -> Any:
        """
        Execute the pipeline with the given data

        Args:
            initial_data: Data to pass through the pipeline

        Returns:
            Final result from the pipeline

        Raises:
            PipelineException: If any stage fails
        """
        current_data = initial_data

        for idx, stage in enumerate(stages):
            try:
                if isinstance(stage, ParallelGroup):
                    # Execute parallel group
                    results = stage.execute(current_data)
                    current_data = results
                elif callable(stage):
                    # Execute sequential function
                    if current_data is not None:
                        result = stage(current_data)
                    else:
                        result = stage()
                    current_data = result
                else:
                    raise ValueError(
                        f"Stage {idx} is not callable or ParallelGroup"
                    )

            except PipelineException:
                # Re-raise pipeline exceptions
                raise
            except Exception as e:
                error_msg = (
                    f"Pipeline stage {idx} failed: {str(e)}\n"
                    f"{traceback.format_exc()}"
                )
                raise PipelineException(error_msg)

        return current_data

    return execute


__all__ = [
    'Pipeline',
    'Parallel',
    'ParallelGroup',
    'PipelineException',
    'pipeline',
    'parallel'
]
