from pydantic import BaseModel, Field, field_validator

from domain.enums import FailureCategory


class FailureContext(BaseModel):
    test_name: str
    suite_name: str = ""
    error_type: str = ""
    error_message: str = ""
    stack_trace: str = ""
    log_excerpt: str = ""
    retry_number: int = 0
    repository_full_name: str = ""
    workflow_name: str = ""
    branch: str = ""


class ClassificationOutput(BaseModel):
    category: FailureCategory
    subcategory: str = ""
    suspected_component: str = ""
    summary: str = Field(min_length=1)
    likely_cause: str = ""
    suggested_action: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)
    insufficient_information: bool = False

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower().replace("-", "_").replace(" ", "_")
        return value


class RawLLMResponse(BaseModel):
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0


class ClassificationResult(BaseModel):
    output: ClassificationOutput
    provider: str
    model: str
    prompt_version: str
    input_hash: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    trace_id: str
