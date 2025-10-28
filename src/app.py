from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from sqlmodel import Session, select, create_engine, SQLModel
from typing import List
import os

from .models import Activity, Participant, ActivityParticipant


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./activities.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent, "static")), name="static")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(session: Session = Depends(get_session)):
    activities = session.exec(select(Activity)).all()
    result: List[dict] = []
    for a in activities:
        participants = [p.email for p in (a.participants or [])]
        result.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "schedule": a.schedule,
            "max_participants": a.max_participants,
            "participants": participants,
        })
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    # Find activity
    activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Load current participants
    participants = activity.participants or []

    if any(p.email == email for p in participants):
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if activity.max_participants and len(participants) >= activity.max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Get or create participant
    participant = session.exec(select(Participant).where(Participant.email == email)).first()
    if not participant:
        participant = Participant(email=email)
        session.add(participant)
        session.commit()
        session.refresh(participant)

    # Link
    link = ActivityParticipant(activity_id=activity.id, participant_id=participant.id)
    session.add(link)
    session.commit()
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    participant = session.exec(select(Participant).where(Participant.email == email)).first()
    if not participant:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    link = session.exec(select(ActivityParticipant).where(
        (ActivityParticipant.activity_id == activity.id) & (ActivityParticipant.participant_id == participant.id)
    )).first()
    if not link:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    session.delete(link)
    session.commit()
    return {"message": f"Unregistered {email} from {activity_name}"}
