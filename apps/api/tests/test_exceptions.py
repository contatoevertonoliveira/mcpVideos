from app.core.exceptions import ApplicationError, NotFoundError
from app.main import app  # noqa: F401  (ensures the exception handler is registered)


def test_application_error_defaults() -> None:
    err = ApplicationError()

    assert err.code == "APPLICATION_ERROR"
    assert err.message == "Something went wrong."


def test_not_found_error_response_shape(client) -> None:
    @app.get("/__test_not_found__")
    def _raise_not_found():
        raise NotFoundError("Project not found", code="PROJECT_NOT_FOUND")

    response = client.get("/__test_not_found__")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "PROJECT_NOT_FOUND", "message": "Project not found"}
    }
