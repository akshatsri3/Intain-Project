from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.dataset import DatasetStatus, SourceType


class DatasetResponse(BaseModel):
    id: int
    file_name: str
    source_type: SourceType
    file_size: Optional[int]
    uploaded_by: int
    uploaded_at: datetime
    total_rows: int
    successfully_imported_rows: int
    failed_rows: int
    status: DatasetStatus

    model_config = {"from_attributes": True}


class NormalizationSummary(BaseModel):
    dates_normalized: int = 0
    currency_values_normalized: int = 0
    interest_rates_normalized: int = 0
    missing_values_converted_to_null: int = 0


class ImportSummaryResponse(BaseModel):
    dataset: DatasetResponse
    normalization_summary: NormalizationSummary


class ImportErrorResponse(BaseModel):
    id: int
    dataset_id: int
    row_number: int
    error_type: str
    error_message: str
    raw_data_json: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}
