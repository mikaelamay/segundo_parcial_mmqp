"""Configuración central de la aplicación MediControl."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Configuración base usada por la Application Factory."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "medicontrol-clave-de-desarrollo-2026")

    # El examen solicita SQLite como motor de base de datos.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'medicontrol.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
