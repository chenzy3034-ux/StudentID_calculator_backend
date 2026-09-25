from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.responses import error_response
from app.database import HistoryRepository, get_history_repository
from app.schemas import (
    DeleteHistoryData,
    DeleteHistorySuccessResponse,
    ErrorResponse,
    HistoryListSuccessResponse,
)
from app.services.history import HistoryNotFoundError, delete_history, list_history


router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryListSuccessResponse)
def get_history(
    repository: Annotated[HistoryRepository, Depends(get_history_repository)],
) -> HistoryListSuccessResponse:
    return HistoryListSuccessResponse(data=list_history(repository))


@router.delete(
    "/{history_id}",
    response_model=DeleteHistorySuccessResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
def remove_history(
    history_id: int,
    repository: Annotated[HistoryRepository, Depends(get_history_repository)],
) -> DeleteHistorySuccessResponse | JSONResponse:
    try:
        delete_history(history_id, repository)
    except HistoryNotFoundError:
        return error_response(
            status.HTTP_404_NOT_FOUND,
            "HISTORY_NOT_FOUND",
            "The calculation history record was not found",
        )

    return DeleteHistorySuccessResponse(data=DeleteHistoryData(id=history_id))
