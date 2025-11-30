"""
Application Bootstrap
Registers all services as singletons in the container
"""

from include import Container, AWSServices
from app.controllers.auth_controller import AuthController
from app.controllers.artifact_controller import ArtifactController
from app.controllers.system_controller import SystemController


def bootstrap_services() -> None:
    """
    Bootstrap application services
    Registers all controllers and jobs as singletons
    """
    # Register AWS services as singleton
    Container.singleton('AWSServices', lambda: AWSServices())
    
    # Register controllers as singletons
    Container.singleton('AuthController', lambda: AuthController())
    Container.singleton('ArtifactController', lambda: ArtifactController())
    Container.singleton('SystemController', lambda: SystemController())


def get_auth_controller() -> AuthController:
    """Get AuthController singleton instance"""
    return Container.make('AuthController')


def get_artifact_controller() -> ArtifactController:
    """Get ArtifactController singleton instance"""
    return Container.make('ArtifactController')


def get_system_controller() -> SystemController:
    """Get SystemController singleton instance"""
    return Container.make('SystemController')


def get_aws_services() -> AWSServices:
    """Get AWSServices singleton instance"""
    return Container.make('AWSServices')
