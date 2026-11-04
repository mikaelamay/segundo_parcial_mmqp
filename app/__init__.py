"""Application Factory de MediControl.

Crea la aplicación Flask, inicializa las extensiones, registra los
Blueprints con sus prefijos y expone el panel principal.
"""
import os
from datetime import date

from flask import Flask, render_template

from app.extensions import db, migrate
from config import Config


def create_app(config_class=Config):
    """Construye y configura una instancia de la aplicación Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Aseguramos que exista la carpeta instance/ donde vive la base SQLite.
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicialización de extensiones.
    db.init_app(app)
    migrate.init_app(app, db)

    # Importamos los modelos para que SQLAlchemy y Flask-Migrate los detecten.
    from app import models  # noqa: F401

    # Registro de Blueprints con los prefijos solicitados por el examen.
    from app.blueprints.citas import bp_citas
    from app.blueprints.medicos import bp_medicos
    from app.blueprints.pacientes import bp_pacientes

    app.register_blueprint(bp_medicos, url_prefix="/medicos")
    app.register_blueprint(bp_pacientes, url_prefix="/pacientes")
    app.register_blueprint(bp_citas, url_prefix="/citas")

    @app.route("/")
    def index():
        """Panel principal con indicadores y próximas citas."""
        from app.models import Cita, Medico, Paciente

        hoy = date.today()
        proximas = (
            Cita.query.filter(Cita.fecha >= hoy)
            .order_by(Cita.fecha.asc(), Cita.hora.asc())
            .limit(6)
            .all()
        )
        return render_template(
            "index.html",
            total_medicos=Medico.query.count(),
            total_pacientes=Paciente.query.count(),
            total_citas=Cita.query.count(),
            citas_hoy=Cita.query.filter_by(fecha=hoy).count(),
            proximas=proximas,
        )

    @app.errorhandler(404)
    def pagina_no_encontrada(error):  # pragma: no cover - vista de error
        return render_template("404.html"), 404

    @app.context_processor
    def inyectar_fecha_actual():
        """Deja disponible la fecha de hoy en todas las plantillas."""
        return {"hoy": date.today()}

    return app
