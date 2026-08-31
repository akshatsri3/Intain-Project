# models package — import all ORM models so SQLAlchemy registers their tables.
#
# IMPORTANT: The app's ImportError model is aliased as "ImportErrorRecord"
# to avoid shadowing Python's built-in ImportError exception class.
# All internal code that references this model must use the alias.
from app.models.user import User
from app.models.dataset import Dataset
from app.models.raw_record import RawRecord
from app.models.loan import Loan
from app.models.import_error import ImportError as ImportErrorRecord  # alias avoids shadowing builtin
from app.models.validation_exception import ValidationException
from app.models.review_decision import ReviewDecision
from app.models.audit_event import AuditEvent
