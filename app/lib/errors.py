from typing import Any, Optional


class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def api_success(data: Any) -> dict[str, Any]:
    return {"success": True, "data": data}


def api_error(
    code: str,
    message: str,
    field_errors: Optional[dict[str, str]] = None,
    form_errors: Optional[list[str]] = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if field_errors:
        error["field_errors"] = field_errors
    if form_errors:
        error["form_errors"] = form_errors
    return {"success": False, "error": error}
