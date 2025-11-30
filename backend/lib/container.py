"""
Service Container
Dependency injection container for managing singletons
"""

from typing import Dict, Type, TypeVar, Callable, Any


T = TypeVar('T')


class Container:
    """
    Service container for dependency injection
    Similar to Laravel's service container
    """
    
    _instance: 'Container' = None
    _bindings: Dict[str, Callable] = {}
    _singletons: Dict[str, Any] = {}
    
    def __new__(cls):
        """Ensure Container itself is a singleton"""
        if cls._instance is None:
            cls._instance = super(Container, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def bind(cls, abstract: str, concrete: Callable) -> None:
        """
        Bind a service to the container
        
        Args:
            abstract: Service identifier (class name or string key)
            concrete: Factory function or class to instantiate
        """
        cls._bindings[abstract] = concrete
    
    @classmethod
    def singleton(cls, abstract: str, concrete: Callable) -> None:
        """
        Register a singleton in the container
        
        Args:
            abstract: Service identifier (class name or string key)
            concrete: Factory function or class to instantiate
        """
        cls._bindings[abstract] = concrete
        # Mark as singleton by setting placeholder
        if abstract not in cls._singletons:
            cls._singletons[abstract] = None
    
    @classmethod
    def make(cls, abstract: str) -> Any:
        """
        Resolve a service from the container
        
        Args:
            abstract: Service identifier
            
        Returns:
            Resolved service instance
        """
        # Check if it's a singleton that's already been resolved
        if abstract in cls._singletons:
            if cls._singletons[abstract] is not None:
                return cls._singletons[abstract]
            
            # Resolve singleton for first time
            if abstract in cls._bindings:
                instance = cls._resolve(cls._bindings[abstract])
                cls._singletons[abstract] = instance
                return instance
        
        # Regular binding (non-singleton)
        if abstract in cls._bindings:
            return cls._resolve(cls._bindings[abstract])
        
        raise ValueError(f"Service '{abstract}' not found in container")
    
    @classmethod
    def _resolve(cls, concrete: Callable) -> Any:
        """
        Resolve a concrete implementation
        
        Args:
            concrete: Factory function or class
            
        Returns:
            Instance of the service
        """
        if callable(concrete):
            return concrete()
        return concrete
    
    @classmethod
    def flush(cls) -> None:
        """Clear all bindings and singletons (useful for testing)"""
        cls._bindings.clear()
        cls._singletons.clear()
    
    @classmethod
    def get_instance(cls, service_class: Type[T]) -> T:
        """
        Get singleton instance of a service by class
        
        Args:
            service_class: The service class
            
        Returns:
            Singleton instance
        """
        service_name = service_class.__name__
        return cls.make(service_name)


# Global container instance
container = Container()
