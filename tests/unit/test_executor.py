import pytest

from server.application.services.executor import universal_response
from server.exceptions import ValidationError


@pytest.mark.asyncio
async def test_universal_response_success():
    @universal_response
    def handler(x: int):
        return {"result": x * 2}

    response = await handler(x=10)
    assert response["status"] == 200
    assert response["data"] == {"result": 20}
    assert response["metrics"]["approx_output_tokens"] > 0

@pytest.mark.asyncio
async def test_universal_response_async_success():
    @universal_response
    async def handler(x: int):
        return {"result": x * 2}

    response = await handler(x=10)
    assert response["status"] == 200
    assert response["data"] == {"result": 20}

@pytest.mark.asyncio
async def test_universal_response_validation_error():
    @universal_response
    def handler():
        raise ValidationError("Invalid")

    response = await handler()
    assert response["status"] == 400
    assert response["error"]["error_code"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_universal_response_unexpected_error():
    @universal_response
    def handler():
        raise ValueError("Boom")

    response = await handler()
    assert response["status"] == 500
    assert response["error"]["error_code"] == "UNEXPECTED_ERROR"
