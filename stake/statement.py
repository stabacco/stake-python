from datetime import date
from typing import List

import pydantic

from stake.common import BaseClient, camelcase

__all__ = ["StatementRequest"]


class Data(pydantic.BaseModel):
    data_code: str
    value: float
    model_config = pydantic.ConfigDict(alias_generator=camelcase, populate_by_name=True)


class StatementRequest(pydantic.BaseModel):
    """Request for retrieving the statements for the given symbol."""

    symbol: str
    start_date: date


class StatementData(pydantic.BaseModel):
    balance_sheet: List[Data]
    income_statement: List[Data]
    cash_flow: List[Data]
    overview: List[Data]
    model_config = pydantic.ConfigDict(alias_generator=camelcase, populate_by_name=True)


class Statement(pydantic.BaseModel):
    date: date
    quarter: int
    year: int
    statement_data: StatementData
    model_config = pydantic.ConfigDict(alias_generator=camelcase, populate_by_name=True)


class StatementClient(BaseClient):
    """This client is in charge listing the experts' statements for symbols."""

    async def list(self, request: StatementRequest) -> List[Statement]:
        """Lists all the statements for the symbols specified in the request.

        Returns:
            List[Statement]: The list of statements.
        """
        data = await self._client.get(
            self._client.exchange.statement.format(
                symbol=request.symbol,
                date=request.start_date,
            )
        )

        if data == {"message": "No data returned"}:
            return []
        return [Statement(**d) for d in data]
