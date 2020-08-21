import pytest

from stake import FxConversionRequest
@pytest.mark.asyncio
async def test_fx_conversion(test_client_fixture_generator):
    request = FxConversionRequest(from_currency="USD", to_currency="AUD", from_amount=1000.0)
    conversion_result = await test_client_fixture_generator.fx.convert(request)
    print(conversion_result)
