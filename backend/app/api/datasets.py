from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User, UserRole
from app.models.dataset import Dataset, SourceType, DatasetStatus
from app.models.loan import Loan
from app.models.import_error import ImportError as ImportErrorModel
from app.schemas.dataset import DatasetResponse, ImportSummaryResponse, NormalizationSummary, ImportErrorResponse
from app.schemas.loan import LoanResponse
from app.services.ingestion_service import process_csv
from app.utils.security import get_current_user

router = APIRouter(prefix="/datasets", tags=["datasets"])


def require_operator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.DATA_OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only DATA_OPERATOR users can perform this action",
        )
    return current_user


@router.post("/upload", response_model=ImportSummaryResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    source_type: str = Form(default="OTHER"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    try:
        source_type_enum = SourceType(source_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source_type. Must be one of: {[e.value for e in SourceType]}",
        )

    file_content = await file.read()
    file_size = len(file_content)

    dataset = Dataset(
        file_name=file.filename,
        source_type=source_type_enum,
        file_size=file_size,
        uploaded_by=current_user.id,
        status=DatasetStatus.UPLOADED,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    try:
        counters = process_csv(db, dataset, file_content)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    db.refresh(dataset)

    return ImportSummaryResponse(
        dataset=DatasetResponse.model_validate(dataset),
        normalization_summary=NormalizationSummary(**counters.to_dict()),
    )


@router.get("", response_model=List[DatasetResponse])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Dataset)
        .filter(Dataset.uploaded_by == current_user.id)
        .order_by(Dataset.uploaded_at.desc())
        .all()
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return dataset


@router.get("/{dataset_id}/summary", response_model=ImportSummaryResponse)
def get_dataset_summary(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ImportSummaryResponse(
        dataset=DatasetResponse.model_validate(dataset),
        normalization_summary=NormalizationSummary(),
    )


@router.get("/{dataset_id}/errors", response_model=List[ImportErrorResponse])
def get_dataset_errors(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    errors = (
        db.query(ImportErrorModel)
        .filter(ImportErrorModel.dataset_id == dataset_id)
        .order_by(ImportErrorModel.row_number)
        .all()
    )
    return errors


@router.get("/{dataset_id}/records", response_model=List[LoanResponse])
def get_dataset_records(
    dataset_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    loans = (
        db.query(Loan)
        .filter(Loan.dataset_id == dataset_id)
        .order_by(Loan.source_row_number)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return loans
