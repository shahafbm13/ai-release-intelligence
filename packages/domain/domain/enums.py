from enum import StrEnum


class UserRole(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    FAILED_PERMANENT = "failed_permanent"


class IngestStatus(StrEnum):
    ACCEPTED = "accepted"
    IGNORED = "ignored"
    DUPLICATE = "duplicate"


class FailureCategory(StrEnum):
    PRODUCT_DEFECT = "product_defect"
    TEST_DEFECT = "test_defect"
    ENVIRONMENT_ISSUE = "environment_issue"
    INFRASTRUCTURE_ISSUE = "infrastructure_issue"
    AUTHENTICATION_ISSUE = "authentication_issue"
    DATA_ISSUE = "data_issue"
    TIMEOUT = "timeout"
    NETWORK_ISSUE = "network_issue"
    FLAKY_INTERMITTENT = "flaky_intermittent"
    UNKNOWN = "unknown"


class ClassificationProvider(StrEnum):
    GROQ = "groq"
    GEMINI = "gemini"
    RULES = "rules"


class SimilarMatchMethod(StrEnum):
    FINGERPRINT = "fingerprint"
    TEST_NAME_ERROR_TYPE = "test_name_error_type"
    TEST_NAME = "test_name"
    ERROR_MESSAGE = "error_message"
    ERROR_TYPE = "error_type"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReleaseRecommendation(StrEnum):
    PROCEED = "proceed"
    CAUTION = "caution"
    HOLD = "hold"


class FeedbackAction(StrEnum):
    ACCEPT = "accept"
    CORRECT = "correct"
