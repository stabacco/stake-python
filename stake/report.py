from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class ReportFormat(str, Enum):
    XLS = "XLS"
    HTML = "HTML"


class ReportName(str, Enum):  # TODO: there are more
    OrderTrans = "OrderTrans"


class ReportRequest(BaseModel):
    dateStart: datetime = Field(
        default_factory=lambda *_: date.today() - timedelta(days=365)
    )
    dateEnd: datetime = Field(default_factory=datetime.utcnow)
    reportFormat: ReportFormat = ReportFormat.XLS
    reportName: ReportName = ReportName.OrderTrans
