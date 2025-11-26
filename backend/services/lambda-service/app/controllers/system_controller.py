import os
from fastapi import HTTPException, Header
from app.jobs import registry_reset_job


class SystemController:
    """
    System Controller
    Handles system-level operations like health checks, reset, and tracks
    """

    def __init__(self):
        pass

    async def health_check(self):
        """Health check endpoint"""
        print("GET /health called")
        result = {"status": "ok"}
        print(f"HEALTH RETURNING: {result}")
        return result

    async def reset_registry(
        self,
        x_authorization: str = Header(
            default=None, alias="X-Authorization")
    ):
        """
        Reset the registry to a system default state
        """
        print("DELETE /reset called")
        try:
            # Prepare event for handler function
            event = {
                'X-Authorization': x_authorization or 'dummy-token',
                'ARTIFACTS_BUCKET': os.environ.get(
                    'ARTIFACTS_BUCKET', 'artifacts-bucket')
            }

            # Call the handler function directly
            result = registry_reset_job(event, None)

            if result.get('statusCode') == 200:
                result_msg = {"message": "Registry is reset."}
                print(f"RESET RETURNING: 200: {result_msg}")
                return result_msg
            elif result.get('statusCode') == 403:
                print("RESET RETURNING: 403 - auth failed")
                raise HTTPException(
                    status_code=403,
                    detail="Authentication failed due to invalid "
                    "or missing AuthenticationToken")
            elif result.get('statusCode') == 401:
                print("RESET RETURNING: 401 - permission denied")
                raise HTTPException(
                    status_code=401,
                    detail="You do not have permission to reset "
                    "the registry")
            else:
                print(f"RESET RETURNING: 500 - error: {result}")
                raise HTTPException(
                    status_code=500, detail="Internal server error")

        except HTTPException as he:
            print(f"RESET HTTPException: {he.status_code} - {he.detail}")
            raise
        except Exception as e:
            print(f"RESET Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}")

    async def get_tracks(self):
        """
        Get the list of tracks team 25 has planned to implement
        """
        print("GET /tracks called")
        result = {
            "plannedTracks": [
                "Access control track"
            ]
        }
        print(f"TRACKS RETURNING: {result}")
        return result
