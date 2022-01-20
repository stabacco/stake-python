import pytest

from stake import FxConversionRequest


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_fx_conversion(tracing_client):
    request = FxConversionRequest(
        from_currency="USD", to_currency="AUD", from_amount=1000.0
    )
    conversion_result = await tracing_client.fx.convert(request)
    assert conversion_result.rate > 1.0
