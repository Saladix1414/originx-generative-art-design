"""OriginX execution-governance boundary."""

from oxgad.execution.production_gate import (
    ProductionExecutionDenied,
    assert_current_execution_allowed,
    evaluate_execution_gate,
)

__all__ = (
    "ProductionExecutionDenied",
    "assert_current_execution_allowed",
    "evaluate_execution_gate",
)
