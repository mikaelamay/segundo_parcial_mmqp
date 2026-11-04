"""Blueprint de Médicos."""
from flask import Blueprint

bp_medicos = Blueprint("bp_medicos", __name__)

from app.blueprints.medicos import routes  # noqa: E402,F401
