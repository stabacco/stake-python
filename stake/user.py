from pydantic import BaseModel


class User(BaseModel):
    userID: str
    firstName: str
    lastName: str
    username: str
    email: str
    sessionKey: str
    macStatus: str
    accountType: str
    regionIdentifier: str
