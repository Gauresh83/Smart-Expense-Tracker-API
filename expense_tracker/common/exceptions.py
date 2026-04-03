import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to produce a consistent
    error envelope:

        {
            "error": {
                "code":    "validation_error",
                "message": "Human-readable summary.",
                "detail":  { ... }   # original DRF detail
            }
        }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "error": {
                "code": _get_error_code(response.status_code),
                "message": _get_message(response.data),
                "detail": response.data,
            }
        }
        response.data = error_payload
    else:
        # Unhandled exception — return 500 and log it
        logger.exception("Unhandled exception in view %s", context.get("view"))
        response = Response(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "detail": None,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_error_code(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        429: "too_many_requests",
        500: "internal_server_error",
    }
    return mapping.get(status_code, "error")


def _get_message(data) -> str:
    if isinstance(data, dict):
        first_key = next(iter(data), None)
        if first_key:
            val = data[first_key]
            if isinstance(val, list) and val:
                return str(val[0])
            return str(val)
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)
