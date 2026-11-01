"""Base errors shared by service application layers."""


class ReAugmenAIError(Exception):
    """Base class for expected platform errors."""


class ContractError(ReAugmenAIError):
    """Raised when a boundary contract cannot be satisfied."""
