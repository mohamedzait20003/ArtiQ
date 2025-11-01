from abc import ABC, abstractmethod
from fastapi import APIRouter


class Controller(ABC):
    """
    Abstract base class for all controllers

    Controllers handle HTTP endpoints and business logic
    for specific domains (auth, users, etc.)
    """

    def __init__(self):
        """Initialize controller with its router"""
        self.router = APIRouter()
        self.register_routes()

    @abstractmethod
    def register_routes(self):
        """
        Register all routes for this controller

        This method must be implemented by all subclasses
        to define their specific endpoints
        """
        pass

    def get_router(self) -> APIRouter:
        """
        Get the FastAPI router for this controller

        Returns:
            APIRouter instance with registered routes
        """
        return self.router
