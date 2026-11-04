"""Blueprint de Pacientes."""
from flask import Blueprint

bp_pacientes = Blueprint("bp_pacientes", __name__)

from app.blueprints.pacientes import routes  # noqa: E402,F401
