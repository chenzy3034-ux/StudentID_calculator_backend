from fastapi.responses import JSONResponse

from app.schemas import ErrorDetail, ErrorResponse


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    response = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status_code, content=response.model_dump())
