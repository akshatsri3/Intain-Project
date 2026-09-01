import io
import math
import logging
import traceback
import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import Dataset, DatasetStatus
from app.models.raw_record import RawRecord
from app.models.loan import Loan
from app.models.import_error import ImportError as ImportErrorModel
from app.utils.normalization import normalize_row, NormalizationCounters

logger = logging.getLogger(__name__)


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
        logger.error("process_csv: could not parse CSV for dataset %s: %s", dataset.id, repr(e))
        traceback.print_exc()
        dataset.status = DatasetStatus.FAILED
        dataset.total_rows = 0
        db.commit()
        raise ValueError(f"Could not parse CSV file: {e}")

    total_rows = len(df)
    dataset.total_rows = total_rows
    logger.info("process_csv: dataset_id=%s total_rows=%d", dataset.id, total_rows)
    db.commit()

    imported_loan_ids = []  # track IDs for audit logging

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
            db.flush()  # flush so loan.id is available
            imported_loan_ids.append((loan.id, row_number))
            successfully_imported += 1

        except Exception as e:
            logger.warning(
                "process_csv: normalization error at row %d dataset %s: %s",
                row_number, dataset.id, str(e),
            )
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

    logger.info(
        "process_csv: dataset_id=%s imported=%d failed=%d",
        dataset.id, successfully_imported, failed_rows,
    )

    # Audit logging — log dataset upload event and each imported loan
    from app.services.audit_service import log_event
    log_event(db, "dataset", dataset.id, "UPLOADED",
              details={"file_name": dataset.file_name, "file_size": dataset.file_size})

    # Log each imported loan using in-memory IDs (avoid N+1 query)
    for loan_id, row_number in imported_loan_ids:
        log_event(db, "loan", loan_id, "IMPORTED",
                  details={"dataset_id": dataset.id, "row_number": row_number})
    db.commit()

    from app.services.validation_service import validate_dataset
    try:
        validate_dataset(db, dataset.id)
    except Exception as exc:
        logger.error(
            "process_csv: validation failed for dataset %s: %s", dataset.id, repr(exc)
        )
        traceback.print_exc()
        # Validation failure is non-fatal — dataset is still imported

    return counters
