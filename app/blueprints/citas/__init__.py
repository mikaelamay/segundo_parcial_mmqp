"""Blueprint de Citas."""
from flask import Blueprint

bp_citas = Blueprint("bp_citas", __name__)

from app.blueprints.citas import routes  # noqa: E402,F401
