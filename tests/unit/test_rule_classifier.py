from domain.enums import FailureCategory
from shared.ai.rule_classifier import classify_with_rules
from shared.ai.schemas import FailureContext


def test_rule_classifier_maps_timeout():
    output = classify_with_rules(
        FailureContext(
            test_name="test_payment_timeout",
            error_type="TimeoutError",
            error_message="Request timed out after 30s",
        )
    )
    assert output.category == FailureCategory.TIMEOUT
    assert output.insufficient_information is False


def test_rule_classifier_maps_assertion_to_product_defect():
    output = classify_with_rules(
        FailureContext(
            test_name="test_checkout_applies_discount",
            error_type="AssertionError",
            error_message="Expected total 90.0 but got 100.0",
        )
    )
    assert output.category == FailureCategory.PRODUCT_DEFECT
