"""
API Routes Definition
Laravel-style route registration with Node.js-style middleware
"""

from fastapi import APIRouter, Depends
from lib.route import Route
from app.controllers.auth_controller import AuthController
from app.controllers.artifact_controller import ArtifactController
from app.controllers.system_controller import SystemController
from app.controllers.admin_controller import AdminController
from app.middlewares.auth_middleware import (
    auth_optional,
    auth_required,
    auth_admin
)


def register_api_routes(app) -> None:
    """
    Register all API routes
    Similar to Laravel's routes/api.php
    """
    # Create main API router
    router = APIRouter()

    # Initialize Route with router
    Route.set_router(router)

    # Initialize controllers
    auth = AuthController()
    artifacts = ArtifactController()
    system = SystemController()
    admin = AdminController()

    # ==========================================
    # System Routes
    # ==========================================
    Route.get(
        '/health',
        system.health_check,
        tags=['system'],
        status_code=200
    )

    Route.delete(
        '/reset',
        system.reset_registry,
        tags=['system'],
        status_code=200
    )

    Route.get(
        '/tracks',
        system.get_tracks,
        tags=['system'],
        status_code=200
    )

    # ==========================================
    # Authentication Routes
    # ==========================================
    Route.put(
        '/authenticate',
        auth.authenticate,
        tags=['auth'],
        response_model=str,
        status_code=200,
        responses={
            200: {"description": "Return an AuthenticationToken"},
            400: {
                "description": "Missing field(s) in the "
                "AuthenticationRequest or it is formed improperly"
            },
            401: {"description": "The user or password is invalid"},
            501: {
                "description": "This system does not support authentication"
            }
        }
    )

    Route.delete(
        '/logout',
        auth.logout,
        tags=['auth'],
        status_code=200,
        dependencies=[Depends(auth_required)]  # Apply auth middleware
    )

    # ==========================================
    # Admin Routes
    # ==========================================
    Route.post(
        '/admin/users',
        admin.create_user,
        tags=['admin'],
        status_code=201,
        responses={
            201: {"description": "User created successfully"},
            400: {"description": "Missing required fields"},
            409: {"description": "User with this email already exists"},
            500: {"description": "Internal server error"}
        }
    )

    # ==========================================
    # Artifact Routes
    # ==========================================

    # List artifacts (with optional auth)
    Route.post(
        '/artifacts',
        artifacts.artifacts_list,
        tags=['artifacts'],
        status_code=200,
        dependencies=[Depends(auth_optional)]  # Apply optional auth
    )

    # Create artifact
    Route.post(
        '/artifact/{artifact_type}',
        artifacts.artifact_create,
        tags=['artifacts'],
        status_code=201
    )

    # Retrieve artifact
    Route.get(
        '/artifacts/{artifact_type}/{id}',
        artifacts.artifact_retrieve,
        tags=['artifacts'],
        status_code=200
    )

    # Update artifact
    Route.put(
        '/artifacts/{artifact_type}/{id}',
        artifacts.artifact_update,
        tags=['artifacts'],
        status_code=200
    )

    # Delete artifact
    Route.delete(
        '/artifacts/{artifact_type}/{id}',
        artifacts.artifact_delete,
        tags=['artifacts'],
        status_code=200
    )

    # ==========================================
    # Additional Artifact Routes (Not Implemented)
    # ==========================================

    # Model artifact rating
    Route.get(
        '/artifact/model/{id}/rate',
        artifacts.model_artifact_rate,
        tags=['artifacts'],
        status_code=200
    )

    # Artifact cost
    Route.get(
        '/artifact/{artifact_type}/{id}/cost',
        artifacts.artifact_cost,
        tags=['artifacts'],
        status_code=200
    )

    # Artifact by name
    Route.get(
        '/artifact/byName/{name}',
        artifacts.artifact_by_name_get,
        tags=['artifacts'],
        status_code=200
    )

    # Artifact audit
    Route.get(
        '/artifact/{artifact_type}/{id}/audit',
        artifacts.artifact_audit_get,
        tags=['artifacts'],
        status_code=200
    )

    # Artifact lineage
    Route.get(
        '/artifact/model/{id}/lineage',
        artifacts.artifact_lineage_get,
        tags=['artifacts'],
        status_code=200
    )

    # License check
    Route.post(
        '/artifact/model/{id}/license-check',
        artifacts.artifact_license_check,
        tags=['artifacts'],
        status_code=200
    )

    # Artifact by regex
    Route.post(
        '/artifact/byRegEx',
        artifacts.artifact_by_regex_get,
        tags=['artifacts'],
        status_code=200
    )

    # Include the router in the app
    app.include_router(router)
