"""Datos de prueba para MediControl.

Uso:
    ./venv/bin/python seed.py            # inserta datos si la base está vacía
    ./venv/bin/python seed.py --reset    # borra todo y vuelve a insertar
"""
import sys
from datetime import date, time, timedelta

from app import create_app
from app.extensions import db
from app.models import Cita, Medico, Paciente

MEDICOS = [
    ("Dra. Ana Torres", "Cardiología"),
    ("Dr. Luis Mamani", "Pediatría"),
    ("Dra. Carla Quispe", "Dermatología"),
    ("Dr. Jorge Apaza", "Traumatología"),
    ("Dra. Silvia Choque", "Ginecología"),
    ("Dr. Marco Condori", "Medicina General"),
]

PACIENTES = [
    ("Juan Pérez Mamani", "71234567"),
    ("María López Quispe", "76543210"),
    ("José Huanca Flores", "72345678"),
    ("Rosa Ticona Nina", "78901234"),
    ("Carlos Ramos Villca", "70123456"),
    ("Lucía Fernández Cruz", "74567890"),
]

# (días respecto a hoy, hora, índice de médico, índice de paciente)
CITAS = [
    (-3, "09:00", 0, 0),
    (-2, "10:30", 1, 1),
    (-1, "15:00", 2, 2),
    (0, "08:30", 5, 3),
    (0, "11:00", 0, 4),
    (0, "16:00", 3, 5),
    (1, "09:30", 1, 0),
    (2, "14:00", 4, 3),
    (4, "10:00", 2, 1),
    (7, "11:30", 5, 4),
]


def cargar_datos(reset=False):
    app = create_app()
    with app.app_context():
        if reset:
            Cita.query.delete()
            Medico.query.delete()
            Paciente.query.delete()
            db.session.commit()
            print("Base de datos reiniciada.")
        elif Medico.query.count() or Paciente.query.count() or Cita.query.count():
            print(
                "La base de datos ya contiene información. "
                "Usa --reset si deseas volver a cargar los datos de prueba."
            )
            return

        medicos = [Medico(nombre=n, especialidad=e) for n, e in MEDICOS]
        pacientes = [Paciente(nombre=n, telefono=t) for n, t in PACIENTES]
        db.session.add_all(medicos + pacientes)
        db.session.commit()

        hoy = date.today()
        for dias, hora_txt, i_medico, i_paciente in CITAS:
            h, m = map(int, hora_txt.split(":"))
            db.session.add(
                Cita(
                    fecha=hoy + timedelta(days=dias),
                    hora=time(h, m),
                    medico_id=medicos[i_medico].id,
                    paciente_id=pacientes[i_paciente].id,
                )
            )
        db.session.commit()

        print(f"Datos cargados: {len(medicos)} médicos, "
              f"{len(pacientes)} pacientes y {len(CITAS)} citas.")


if __name__ == "__main__":
    cargar_datos(reset="--reset" in sys.argv)
