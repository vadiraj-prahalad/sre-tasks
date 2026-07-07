from fastapi import APIRouter

from manage import refresh_knowledge


router = APIRouter(prefix="/admin")


@router.post("/refresh")
def refresh_admin_knowledge():
    try:
        refresh_knowledge()

        return {
            "status": "success",
            "message": "Knowledge refresh completed successfully.",
        }
    except SystemExit:
        return {
            "status": "failed",
            "message": "Knowledge refresh completed with evaluation failures.",
        }
    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }
