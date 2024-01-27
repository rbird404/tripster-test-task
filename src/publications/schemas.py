import datetime
from enum import Enum

from pydantic import ConfigDict

from src.common.schemas import BaseSchema, DefaultResponse
from src.users.schemas import UserRead


class PublicationBase(BaseSchema):
    content: str


class PublicationCreate(PublicationBase):
    pass


class PublicationRead(PublicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PublicationReadDetail(PublicationRead):
    rating: float | None = 0
    vote_count: int = 0
    creator: UserRead
    created_at: datetime.datetime


class VoteBase(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    grade: bool


class OrderBy(str, Enum):
    rating = "rating"
    created_at = "created_at"


class ItemQueryParams(BaseSchema):
    order_by: OrderBy = OrderBy.rating
    desc: bool = False
    limit: int = 10


class PublicationListResponse(DefaultResponse):
    status: bool = True
    details: list[PublicationReadDetail]


class PublicationResponse(DefaultResponse):
    status: bool = True
    details: PublicationRead


class VoteResponse(DefaultResponse):
    status: bool = True
    details: VoteBase
