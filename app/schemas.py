from typing import Literal

from pydantic import BaseModel, ConfigDict


class CalculateRequest(BaseModel):
    expression: str


class CalculationData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    expression: str
    result: str
    created_at: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class CalculateSuccessResponse(BaseModel):
    success: Literal[True] = True
    data: CalculationData
    error: None = None


class HistoryListSuccessResponse(BaseModel):
    success: Literal[True] = True
    data: list[CalculationData]
    error: None = None


class DeleteHistoryData(BaseModel):
    id: int


class DeleteHistorySuccessResponse(BaseModel):
    success: Literal[True] = True
    data: DeleteHistoryData
    error: None = None


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    data: None = None
    error: ErrorDetail
