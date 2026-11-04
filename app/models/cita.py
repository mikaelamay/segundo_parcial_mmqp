"""Modelo Cita."""
from datetime import date

from app.extensions import db


class Cita(db.Model):
    """Cita médica que relaciona un médico con un paciente."""

    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    medico_id = db.Column(
        db.Integer, db.ForeignKey("medicos.id"), nullable=False, index=True
    )
    paciente_id = db.Column(
        db.Integer, db.ForeignKey("pacientes.id"), nullable=False, index=True
    )

    # Cada cita pertenece a un médico y a un paciente.
    medico = db.relationship("Medico", back_populates="citas")
    paciente = db.relationship("Paciente", back_populates="citas")

    @property
    def estado(self):
        """Estado calculado de la cita para mostrarlo en las plantillas."""
        if self.fecha < date.today():
            return "Atendida"
        if self.fecha == date.today():
            return "Hoy"
        return "Programada"

    def __repr__(self):
        return f"<Cita {self.fecha} {self.hora} - {self.medico_id}/{self.paciente_id}>"
