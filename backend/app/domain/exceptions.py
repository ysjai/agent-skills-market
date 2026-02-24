class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    message: str = "Domain error occurred"
    category: str = "BUSINESS"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    message = "Validation failed"
    category = "VALIDATION"


class ResourceNotFoundError(DomainError):
    code = "RESOURCE_NOT_FOUND"
    message = "Resource not found"
    category = "NOT_FOUND"


class ResourceConflictError(DomainError):
    code = "RESOURCE_CONFLICT"
    message = "Resource conflict"
    category = "CONFLICT"


class UnauthorizedError(DomainError):
    code = "UNAUTHORIZED"
    message = "Authentication required"
    category = "UNAUTHORIZED"


class ForbiddenError(DomainError):
    code = "FORBIDDEN"
    message = "Permission denied"
    category = "FORBIDDEN"
