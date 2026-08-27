from fastapi import APIRouter

from backend.api.errors import ApiError


router = APIRouter()


def not_implemented(module: str) -> None:
    raise ApiError(
        "MODULE_NOT_IMPLEMENTED",
        f"The {module} module is not yet available",
        501,
    )


@router.get("/analytics/density")
def density() -> None:
    not_implemented("analytics")


@router.get("/analytics/congestion")
def congestion() -> None:
    not_implemented("analytics")


@router.get("/analytics/od")
def origin_destination() -> None:
    not_implemented("analytics")


@router.get("/alerts")
def alerts() -> None:
    not_implemented("alerts")