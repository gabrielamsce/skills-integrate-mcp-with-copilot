"""Seed the SQLite database with example activities and participants.

Run: python -m scripts.seed_db
"""
from sqlmodel import Session, select
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.models import Activity, Participant
from src.app import engine, create_db_and_tables


def seed():
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(Activity)).first()
        if existing:
            print("DB already seeded (activities exist). Skipping.")
            return

        activities = [
            Activity(name="Chess Club", description="Learn strategies and compete in chess tournaments", schedule="Fridays, 3:30 PM - 5:00 PM", max_participants=12),
            Activity(name="Programming Class", description="Learn programming fundamentals and build software projects", schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM", max_participants=20),
            Activity(name="Gym Class", description="Physical education and sports activities", schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", max_participants=30),
        ]

        for a in activities:
            session.add(a)

        session.commit()
        print("Seeded activities.")


if __name__ == "__main__":
    seed()
