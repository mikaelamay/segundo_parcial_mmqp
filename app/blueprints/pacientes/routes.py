"""Rutas CRUD para el módulo de Pacientes."""
import re

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from app.blueprints.pacientes import bp_pacientes
from app.extensions import db
from app.models import Paciente

PATRON_TELEFONO = re.compile(r"^[0-9+\-()\s]{7,30}$")


def _validar_formulario():
    """Lee y valida los datos enviados desde el formulario."""
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    errores = []

    if not nombre:
        errores.append("El nombre del paciente es obligatorio.")
    elif len(nombre) > 120:
        errores.append("El nombre no puede superar los 120 caracteres.")

    if not telefono:
        errores.append("El teléfono es obligatorio.")
    elif not PATRON_TELEFONO.match(telefono):
        errores.append(
            "El teléfono solo admite números, espacios, paréntesis, guiones y el signo +."
        )

    return nombre, telefono, errores


@bp_pacientes.route("/")
def index():
    """Lista de pacientes con búsqueda por nombre o teléfono."""
    q = request.args.get("q", "").strip()
    consulta = Paciente.query
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(
            or_(Paciente.nombre.ilike(patron), Paciente.telefono.ilike(patron))
        )
    pacientes = consulta.order_by(Paciente.nombre.asc()).all()
    return render_template("pacientes/index.html", pacientes=pacientes, q=q)


@bp_pacientes.route("/nuevo", methods=["GET", "POST"])
def crear():
    """Registra un nuevo paciente."""
    if request.method == "POST":
        nombre, telefono, errores = _validar_formulario()
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("pacientes/form.html", paciente=None), 400

        paciente = Paciente(nombre=nombre, telefono=telefono)
        db.session.add(paciente)
        db.session.commit()
        flash(f"Paciente «{paciente.nombre}» registrado correctamente.", "success")
        return redirect(url_for("bp_pacientes.index"))

    return render_template("pacientes/form.html", paciente=None)


@bp_pacientes.route("/<int:paciente_id>/editar", methods=["GET", "POST"])
def editar(paciente_id):
    """Actualiza los datos de un paciente existente."""
    paciente = db.get_or_404(Paciente, paciente_id)

    if request.method == "POST":
        nombre, telefono, errores = _validar_formulario()
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("pacientes/form.html", paciente=paciente), 400

        paciente.nombre = nombre
        paciente.telefono = telefono
        db.session.commit()
        flash(f"Paciente «{paciente.nombre}» actualizado correctamente.", "success")
        return redirect(url_for("bp_pacientes.index"))

    return render_template("pacientes/form.html", paciente=paciente)


@bp_pacientes.post("/<int:paciente_id>/eliminar")
def eliminar(paciente_id):
    """Elimina un paciente siempre que no tenga citas asociadas."""
    paciente = db.get_or_404(Paciente, paciente_id)
    if paciente.citas:
        flash(
            "No se puede eliminar al paciente porque tiene citas registradas. "
            "Elimina primero sus citas.",
            "warning",
        )
        return redirect(url_for("bp_pacientes.index"))

    nombre = paciente.nombre
    db.session.delete(paciente)
    db.session.commit()
    flash(f"Paciente «{nombre}» eliminado correctamente.", "success")
    return redirect(url_for("bp_pacientes.index"))
