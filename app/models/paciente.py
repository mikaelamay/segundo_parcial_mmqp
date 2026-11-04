"""Modelo Paciente."""
from app.extensions import db


class Paciente(db.Model):
    """Paciente registrado en la clínica."""

    __tablename__ = "pacientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)

    # Relación 1 a N: un paciente puede tener muchas citas.
    citas = db.relationship("Cita", back_populates="paciente", lazy="select")

    def __repr__(self):
        return f"<Paciente {self.nombre}>"
