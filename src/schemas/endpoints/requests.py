from pydantic import BaseModel, Field


class EventBridgeEventDetailS3Bucket(BaseModel):
    name: str


class EventBridgeEventDetailS3Object(BaseModel):
    key: str


class EventBridgeEvent(BaseModel):
    id: str
    detail_type: str = Field(..., alias="detail-type")


class EventBridgeS3EventDetail(BaseModel):
    bucket: EventBridgeEventDetailS3Bucket
    object: EventBridgeEventDetailS3Object


class EventBridgeS3Event(EventBridgeEvent):
    detail: EventBridgeS3EventDetail
