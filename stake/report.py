from datetime import date
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class ReportFormat(str, Enum):
    XLS = "XLS"
    HTML = "HTML"


class ReportName(str, Enum):  # TODO: there are more
    OrderTrans = "OrderTrans"


class ReportRequest(BaseModel):
    dateStart: datetime = Field(default_factory=datetime.utcnow)
    dateEnd: datetime
    reportFormat: ReportFormat = ReportFormat.XLS
    reportName: ReportName = ReportName.OrderTrans
