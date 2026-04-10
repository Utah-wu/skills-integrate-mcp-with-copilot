from pathlib import Path
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship, create_engine

DB_FILE = Path(__file__).resolve().parents[1] / "school.db"
DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


class Student(SQLModel, table=True):
    email: str = Field(primary_key=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None
    contacts: List["Contact"] = Relationship(back_populates="student")
    activities: List["Activity"] = Relationship(back_populates="student")


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_email: str = Field(foreign_key="student.email", index=True)
    mobile: Optional[str] = None
    student: Optional[Student] = Relationship(back_populates="contacts")


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_email: str = Field(foreign_key="student.email", index=True)
    activity_name: str
    category: Optional[str] = None
    student: Optional[Student] = Relationship(back_populates="activities")
