"""Rutas CRUD para el módulo de Médicos."""
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from app.blueprints.medicos import bp_medicos
from app.extensions import db
from app.models import Medico


def _validar_formulario():
    """Lee y valida los datos enviados desde el formulario."""
    nombre = request.form.get("nombre", "").strip()
    especialidad = request.form.get("especialidad", "").strip()
    errores = []

    if not nombre:
        errores.append("El nombre del médico es obligatorio.")
    elif len(nombre) > 120:
        errores.append("El nombre no puede superar los 120 caracteres.")

    if not especialidad:
        errores.append("La especialidad es obligatoria.")
    elif len(especialidad) > 120:
        errores.append("La especialidad no puede superar los 120 caracteres.")

    return nombre, especialidad, errores


@bp_medicos.route("/")
def index():
    """Lista de médicos con búsqueda por nombre o especialidad."""
    q = request.args.get("q", "").strip()
    consulta = Medico.query
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(
            or_(Medico.nombre.ilike(patron), Medico.especialidad.ilike(patron))
        )
    medicos = consulta.order_by(Medico.nombre.asc()).all()
    return render_template("medicos/index.html", medicos=medicos, q=q)


@bp_medicos.route("/nuevo", methods=["GET", "POST"])
def crear():
    """Registra un nuevo médico."""
    if request.method == "POST":
        nombre, especialidad, errores = _validar_formulario()
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("medicos/form.html", medico=None), 400

        medico = Medico(nombre=nombre, especialidad=especialidad)
        db.session.add(medico)
        db.session.commit()
        flash(f"Médico «{medico.nombre}» registrado correctamente.", "success")
        return redirect(url_for("bp_medicos.index"))

    return render_template("medicos/form.html", medico=None)


@bp_medicos.route("/<int:medico_id>/editar", methods=["GET", "POST"])
def editar(medico_id):
    """Actualiza los datos de un médico existente."""
    medico = db.get_or_404(Medico, medico_id)

    if request.method == "POST":
        nombre, especialidad, errores = _validar_formulario()
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("medicos/form.html", medico=medico), 400

        medico.nombre = nombre
        medico.especialidad = especialidad
        db.session.commit()
        flash(f"Médico «{medico.nombre}» actualizado correctamente.", "success")
        return redirect(url_for("bp_medicos.index"))

    return render_template("medicos/form.html", medico=medico)


@bp_medicos.post("/<int:medico_id>/eliminar")
def eliminar(medico_id):
    """Elimina un médico siempre que no tenga citas asociadas."""
    medico = db.get_or_404(Medico, medico_id)
    if medico.citas:
        flash(
            "No se puede eliminar al médico porque tiene citas registradas. "
            "Elimina primero sus citas.",
            "warning",
        )
        return redirect(url_for("bp_medicos.index"))

    nombre = medico.nombre
    db.session.delete(medico)
    db.session.commit()
    flash(f"Médico «{nombre}» eliminado correctamente.", "success")
    return redirect(url_for("bp_medicos.index"))
