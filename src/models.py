from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class ActivityParticipant(SQLModel, table=True):
    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id", primary_key=True)
    participant_id: Optional[int] = Field(default=None, foreign_key="participant.id", primary_key=True)


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    activities: List["Activity"] = Relationship(back_populates="participants", link_model=ActivityParticipant)


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None
    participants: List[Participant] = Relationship(back_populates="activities", link_model=ActivityParticipant)
