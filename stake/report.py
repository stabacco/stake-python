from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum


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
