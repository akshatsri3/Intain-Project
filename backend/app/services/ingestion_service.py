import io
import math
import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import Dataset, DatasetStatus
from app.models.raw_record import RawRecord
from app.models.loan import Loan
from app.models.import_error import ImportError as ImportErrorModel
from app.utils.normalization import normalize_row, NormalizationCounters


def _safe_value(val) -> any:
    if val is None:
        return None
    try:
        if isinstance(val, float) and math.isnan(val):
            return None
    except TypeError:
        pass
    return val


def process_csv(
    db: Session,
    dataset: Dataset,
    file_content: bytes,
) -> NormalizationCounters:
    counters = NormalizationCounters()
    successfully_imported = 0
    failed_rows = 0

    dataset.status = DatasetStatus.PROCESSING
    db.commit()

    try:
        df = pd.read_csv(io.BytesIO(file_content), dtype=str, keep_default_na=False)
    except Exception as e:
        dataset.status = DatasetStatus.FAILED
        dataset.total_rows = 0
        db.commit()
        raise ValueError(f"Could not parse CSV file: {e}")

    total_rows = len(df)
    dataset.total_rows = total_rows
    db.commit()

    for idx, row in df.iterrows():
        row_number = idx + 1
        raw_dict = {col: (_safe_value(val) if val != "" else None) for col, val in row.items()}

        raw_record = RawRecord(
            dataset_id=dataset.id,
            row_number=row_number,
            raw_data_json=raw_dict,
        )
        db.add(raw_record)

        try:
            normalized = normalize_row(raw_dict, counters)
            non_null_values = [v for v in normalized.values() if v is not None]
            if len(non_null_values) == 0:
                raise ValueError("Row produced no normalized fields — empty or malformed")

            loan = Loan(
                dataset_id=dataset.id,
                source_row_number=row_number,
                **normalized,
            )
            db.add(loan)
            successfully_imported += 1

        except Exception as e:
            import_error = ImportErrorModel(
                dataset_id=dataset.id,
                row_number=row_number,
                error_type="NORMALIZATION_ERROR",
                error_message=str(e),
                raw_data_json=raw_dict,
            )
            db.add(import_error)
            failed_rows += 1

        if row_number % 100 == 0:
            db.commit()

    db.commit()

    dataset.successfully_imported_rows = successfully_imported
    dataset.failed_rows = failed_rows
    dataset.status = DatasetStatus.COMPLETED
    db.commit()

    from app.services.audit_service import log_event
    log_event(db, "dataset", dataset.id, "UPLOADED",
              details={"file_name": dataset.file_name, "file_size": dataset.file_size})
    for loan_record in db.query(Loan).filter(Loan.dataset_id == dataset.id).all():
        log_event(db, "loan", loan_record.id, "IMPORTED",
                  details={"dataset_id": dataset.id, "row_number": loan_record.source_row_number})
    db.commit()

    from app.services.validation_service import validate_dataset
    try:
        validate_dataset(db, dataset.id)
    except Exception:
        pass

    return counters
