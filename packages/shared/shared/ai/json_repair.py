import json
import re

from pydantic import ValidationError

from shared.ai.schemas import ClassificationOutput


def extract_json_object(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def repair_json_text(text: str) -> str:
    candidate = extract_json_object(text) or text
    candidate = candidate.strip()
    candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
    return candidate


def parse_classification_output(text: str, *, allow_repair: bool = True) -> ClassificationOutput:
    try:
        data = json.loads(text)
        return ClassificationOutput.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        if not allow_repair:
            raise
        repaired = repair_json_text(text)
        data = json.loads(repaired)
        return ClassificationOutput.model_validate(data)
