from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import DateTime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    is_active = db.Column(db.Boolean, default=True)
    last_login_at = db.Column(DateTime, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    statuses = db.relationship("TaskStatus", back_populates="user", cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), default="medium")
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    assignee = db.relationship("User", foreign_keys=[assignee_id])
    statuses = db.relationship("TaskStatus", back_populates="task", cascade="all, delete-orphan")


class TaskStatus(db.Model):
    __tablename__ = "task_status"
    __table_args__ = (db.UniqueConstraint("task_id", "user_id", name="uq_task_status_task_user"),)

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="not_started")
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    task = db.relationship("Task", back_populates="statuses")
    user = db.relationship("User", back_populates="statuses")
