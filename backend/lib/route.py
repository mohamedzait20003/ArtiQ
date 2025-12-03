"""
Route Registration System
Laravel-style routing for FastAPI
"""

from typing import Callable, List, Optional, Dict, Any
from fastapi import APIRouter, Depends
from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods supported by routes"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


class Route:
    """
    Laravel-style route manager for FastAPI

    Usage:
        Route.get('/users', controller.index)
        Route.post('/users', controller.store)
        Route.put('/users/{id}', controller.update)
        Route.delete('/users/{id}', controller.destroy)
    """

    _router: Optional[APIRouter] = None
    _routes: List[Dict[str, Any]] = []

    @classmethod
    def set_router(cls, router: APIRouter):
        """Set the FastAPI router instance"""
        cls._router = router

    @classmethod
    def get_router(cls) -> Optional[APIRouter]:
        """Get the current router instance"""
        return cls._router

    @classmethod
    def get(
        cls,
        path: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
        **kwargs
    ):
        """Register a GET route"""
        return cls._register_route(
            HTTPMethod.GET,
            path,
            handler,
            name=name,
            tags=tags,
            response_model=response_model,
            status_code=status_code,
            dependencies=dependencies,
            **kwargs
        )

    @classmethod
    def post(
        cls,
        path: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        response_model: Any = None,
        status_code: int = 201,
        dependencies: Optional[List[Depends]] = None,
        **kwargs
    ):
        """Register a POST route"""
        return cls._register_route(
            HTTPMethod.POST,
            path,
            handler,
            name=name,
            tags=tags,
            response_model=response_model,
            status_code=status_code,
            dependencies=dependencies,
            **kwargs
        )

    @classmethod
    def put(
        cls,
        path: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
        **kwargs
    ):
        """Register a PUT route"""
        return cls._register_route(
            HTTPMethod.PUT,
            path,
            handler,
            name=name,
            tags=tags,
            response_model=response_model,
            status_code=status_code,
            dependencies=dependencies,
            **kwargs
        )

    @classmethod
    def delete(
        cls,
        path: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
        **kwargs
    ):
        """Register a DELETE route"""
        return cls._register_route(
            HTTPMethod.DELETE,
            path,
            handler,
            name=name,
            tags=tags,
            response_model=response_model,
            status_code=status_code,
            dependencies=dependencies,
            **kwargs
        )

    @classmethod
    def patch(
        cls,
        path: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
        **kwargs
    ):
        """Register a PATCH route"""
        return cls._register_route(
            HTTPMethod.PATCH,
            path,
            handler,
            name=name,
            tags=tags,
            response_model=response_model,
            status_code=status_code,
            dependencies=dependencies,
            **kwargs
        )

    @classmethod
    def group(
        cls,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[Depends]] = None
    ):
        """
        Create a route group with shared prefix, tags, and dependencies

        Usage:
            with Route.group(prefix="/api/v1", tags=["v1"]):
                Route.get("/users", handler)
        """
        return RouteGroup(prefix=prefix, tags=tags, dependencies=dependencies)

    @classmethod
    def _register_route(
        cls,
        method: HTTPMethod,
        path: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
        **kwargs
    ):
        """Internal method to register a route"""
        if cls._router is None:
            raise RuntimeError(
                "Router not initialized. Call Route.set_router(router) first"
            )

        # Build route config
        route_config = {
            'path': path,
            'status_code': status_code,
            **kwargs
        }

        if name:
            route_config['name'] = name
        if tags:
            route_config['tags'] = tags
        if response_model:
            route_config['response_model'] = response_model
        if dependencies:
            route_config['dependencies'] = dependencies

        # Register with FastAPI router based on method
        if method == HTTPMethod.GET:
            cls._router.get(**route_config)(handler)
        elif method == HTTPMethod.POST:
            cls._router.post(**route_config)(handler)
        elif method == HTTPMethod.PUT:
            cls._router.put(**route_config)(handler)
        elif method == HTTPMethod.DELETE:
            cls._router.delete(**route_config)(handler)
        elif method == HTTPMethod.PATCH:
            cls._router.patch(**route_config)(handler)

        # Store route metadata
        cls._routes.append({
            'method': method,
            'path': path,
            'handler': handler.__name__,
            'name': name,
            'tags': tags
        })

        return handler

    @classmethod
    def list_routes(cls) -> List[Dict[str, Any]]:
        """Get list of all registered routes"""
        return cls._routes


class RouteGroup:
    """Context manager for route grouping"""

    def __init__(
        self,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[Depends]] = None
    ):
        self.prefix = prefix
        self.tags = tags or []
        self.dependencies = dependencies or []
        self._original_register = None

    def __enter__(self):
        """Enter the route group context"""
        # Store original register method
        self._original_register = Route._register_route

        # Create wrapped register method that adds group config
        def wrapped_register(method, path, handler, **kwargs):
            # Prepend prefix to path
            full_path = f"{self.prefix}{path}"

            # Merge tags
            route_tags = kwargs.get('tags', [])
            kwargs['tags'] = self.tags + route_tags

            # Merge dependencies
            route_deps = kwargs.get('dependencies', [])
            kwargs['dependencies'] = self.dependencies + route_deps

            return self._original_register(
                method, full_path, handler, **kwargs
            )

        # Replace register method
        Route._register_route = wrapped_register
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the route group context"""
        # Restore original register method
        if self._original_register:
            Route._register_route = self._original_register
