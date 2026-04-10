"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities and stores student, contact, and activity
records in a persistent SQLite database.
"""

import os
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, select

from src.models import Activity, Student, engine

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)

activities: Dict[str, Dict] = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "category": "Club",
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "category": "Class",
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "category": "Class",
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "category": "Team",
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "category": "Team",
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "category": "Club",
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "category": "Club",
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "category": "Club",
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "category": "Club",
    },
}


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


def get_signup_emails(activity_name: str):
    with get_session() as session:
        statement = select(Activity).where(Activity.activity_name == activity_name)
        results = session.exec(statement).all()
        return [activity.student_email for activity in results]


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    response = {}
    for name, details in activities.items():
        participants = get_signup_emails(name)
        response[name] = {
            **details,
            "participants": participants,
            "availability": details["max_participants"] - len(participants),
        }
    return response


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    with get_session() as session:
        existing = session.exec(
            select(Activity).where(
                Activity.activity_name == activity_name,
                Activity.student_email == email,
            )
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        student = session.get(Student, email)
        if not student:
            student = Student(email=email)
            session.add(student)
            session.commit()
            session.refresh(student)

        signup = Activity(
            student_email=email,
            activity_name=activity_name,
            category=activities[activity_name]["category"],
        )
        session.add(signup)
        session.commit()

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    with get_session() as session:
        statement = select(Activity).where(
            Activity.activity_name == activity_name,
            Activity.student_email == email,
        )
        existing = session.exec(statement).first()

        if not existing:
            raise HTTPException(
                status_code=400,
                detail="Student is not signed up for this activity",
            )

        session.delete(existing)
        session.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}


@app.get("/students")
def get_students():
    with get_session() as session:
        students = session.exec(select(Student)).all()
        return [student.dict() for student in students]
