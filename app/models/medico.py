"""Modelo Médico."""
from app.extensions import db


class Medico(db.Model):
    """Médico que atiende citas dentro de la clínica."""

    __tablename__ = "medicos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    especialidad = db.Column(db.String(120), nullable=False)

    # Relación 1 a N: un médico puede tener muchas citas.
    citas = db.relationship("Cita", back_populates="medico", lazy="select")

    def __repr__(self):
        return f"<Medico {self.nombre} - {self.especialidad}>"
