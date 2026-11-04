"""Rutas CRUD para el módulo de Citas."""
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from app.blueprints.citas import bp_citas
from app.extensions import db
from app.models import Cita, Medico, Paciente


def _validar_formulario(cita_actual=None):
    """Valida fecha, hora, médico y paciente, incluyendo choques de horario."""
    fecha_txt = request.form.get("fecha", "").strip()
    hora_txt = request.form.get("hora", "").strip()
    medico_id = request.form.get("medico_id", type=int)
    paciente_id = request.form.get("paciente_id", type=int)
    errores = []
    fecha = hora = medico = paciente = None

    try:
        fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
    except ValueError:
        errores.append("Selecciona una fecha válida.")

    try:
        hora = datetime.strptime(hora_txt, "%H:%M").time()
    except ValueError:
        errores.append("Selecciona una hora válida.")

    if medico_id:
        medico = db.session.get(Medico, medico_id)
    if medico is None:
        errores.append("Debes seleccionar un médico válido.")

    if paciente_id:
        paciente = db.session.get(Paciente, paciente_id)
    if paciente is None:
        errores.append("Debes seleccionar un paciente válido.")

    if medico and fecha and hora:
        consulta = Cita.query.filter_by(
            medico_id=medico.id, fecha=fecha, hora=hora
        )
        if cita_actual is not None:
            consulta = consulta.filter(Cita.id != cita_actual.id)
        if consulta.first():
            errores.append(
                "El médico ya tiene una cita agendada en esa fecha y hora. "
                "Elige otro horario."
            )

    return fecha, hora, medico, paciente, errores


@bp_citas.route("/")
def index():
    """Lista de citas con filtros por fecha y médico."""
    fecha_txt = request.args.get("fecha", "").strip()
    medico_id = request.args.get("medico_id", type=int)

    consulta = Cita.query
    if fecha_txt:
        try:
            fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
            consulta = consulta.filter(Cita.fecha == fecha)
        except ValueError:
            flash("La fecha del filtro no es válida.", "warning")

    if medico_id:
        consulta = consulta.filter(Cita.medico_id == medico_id)

    citas = consulta.order_by(
        Cita.fecha.desc(), Cita.hora.desc(), Cita.id.desc()
    ).all()
    medicos = Medico.query.order_by(Medico.nombre.asc()).all()

    return render_template(
        "citas/index.html",
        citas=citas,
        medicos=medicos,
        fecha_filtro=fecha_txt,
        medico_filtro=medico_id,
    )


@bp_citas.route("/nueva", methods=["GET", "POST"])
def crear():
    """Agenda una nueva cita médica."""
    medicos = Medico.query.order_by(Medico.nombre.asc()).all()
    pacientes = Paciente.query.order_by(Paciente.nombre.asc()).all()

    if request.method == "POST":
        fecha, hora, medico, paciente, errores = _validar_formulario()
        if errores:
            for error in errores:
                flash(error, "danger")
            return (
                render_template(
                    "citas/form.html",
                    cita=None,
                    medicos=medicos,
                    pacientes=pacientes,
                ),
                400,
            )

        cita = Cita(
            fecha=fecha, hora=hora, medico=medico, paciente=paciente
        )
        db.session.add(cita)
        db.session.commit()
        flash("Cita agendada correctamente.", "success")
        return redirect(url_for("bp_citas.index"))

    return render_template(
        "citas/form.html", cita=None, medicos=medicos, pacientes=pacientes
    )


@bp_citas.route("/<int:cita_id>/editar", methods=["GET", "POST"])
def editar(cita_id):
    """Actualiza una cita existente."""
    cita = db.get_or_404(Cita, cita_id)
    medicos = Medico.query.order_by(Medico.nombre.asc()).all()
    pacientes = Paciente.query.order_by(Paciente.nombre.asc()).all()

    if request.method == "POST":
        fecha, hora, medico, paciente, errores = _validar_formulario(cita)
        if errores:
            for error in errores:
                flash(error, "danger")
            return (
                render_template(
                    "citas/form.html",
                    cita=cita,
                    medicos=medicos,
                    pacientes=pacientes,
                ),
                400,
            )

        cita.fecha = fecha
        cita.hora = hora
        cita.medico = medico
        cita.paciente = paciente
        db.session.commit()
        flash("Cita actualizada correctamente.", "success")
        return redirect(url_for("bp_citas.index"))

    return render_template(
        "citas/form.html", cita=cita, medicos=medicos, pacientes=pacientes
    )


@bp_citas.post("/<int:cita_id>/eliminar")
def eliminar(cita_id):
    """Elimina una cita médica."""
    cita = db.get_or_404(Cita, cita_id)
    db.session.delete(cita)
    db.session.commit()
    flash("Cita eliminada correctamente.", "success")
    return redirect(url_for("bp_citas.index"))
