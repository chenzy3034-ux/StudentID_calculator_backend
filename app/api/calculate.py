from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.responses import error_response
from app.calculator import DivisionByZeroExpressionError, InvalidExpressionError
from app.database import HistoryRepository, get_history_repository
from app.schemas import CalculateRequest, CalculateSuccessResponse, ErrorResponse
from app.services.calculation import calculate_and_store


router = APIRouter(prefix="/api", tags=["calculator"])


@router.post(
    "/calculate",
    response_model=CalculateSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def calculate(
    request: CalculateRequest,
    repository: Annotated[HistoryRepository, Depends(get_history_repository)],
) -> CalculateSuccessResponse | JSONResponse:
    try:
        history = calculate_and_store(request.expression, repository)
    except InvalidExpressionError:
        return error_response(
            status.HTTP_400_BAD_REQUEST,
            "INVALID_EXPRESSION",
            "The expression is invalid",
        )
    except DivisionByZeroExpressionError:
        return error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "DIVISION_BY_ZERO",
            "Division by zero is not allowed",
        )

    return CalculateSuccessResponse(data=history)
