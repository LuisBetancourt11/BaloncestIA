from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base
import json

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    fecha_inicio = Column(String)
    semanas = Column(Integer)
    nivel = Column(String)
    dias_por_semana = Column(Integer)
    duracion_sesion_min = Column(Integer)
    objetivos_json = Column(Text)
    equipamiento_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship('Session', back_populates='plan', cascade='all, delete-orphan')

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey('plans.id'))
    week_idx = Column(Integer)
    day_name = Column(String)
    intensidad = Column(String)
    duracion_min = Column(Integer)
    rpe = Column(Integer)
    carga = Column(Integer)

    plan = relationship('Plan', back_populates='sessions')
    blocks = relationship('Block', back_populates='session', cascade='all, delete-orphan')

class Block(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    tipo = Column(String)
    min = Column(Integer)
    descripcion = Column(Text)

    session = relationship('Session', back_populates='blocks')

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey('plans.id'))
    week_idx = Column(Integer)
    cumplimiento_pct = Column(Integer)
    rpe_promedio = Column(Integer)
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
