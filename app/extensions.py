"""Extensiones compartidas por la aplicación (patrón Application Factory)."""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
