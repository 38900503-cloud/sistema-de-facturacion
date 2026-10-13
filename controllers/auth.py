from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, Usuario

bp = Blueprint("auth", __name__)


@bp.before_app_request
def cargar_usuario():
    """Antes de cada pedido, deja en g.usuario al usuario logueado (o None)."""
    id_usuario = session.get("id_usuario")
    g.usuario = db.session.get(Usuario, id_usuario) if id_usuario else None


def login_requerido(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if g.usuario is None:
            flash("Iniciá sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return funcion(*args, **kwargs)
    return envoltura


def solo_admin(funcion):
    """Los ABM de clientes y productos son solo para el Administrador (casos de uso CU-02 y CU-03)."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if g.usuario is None:
            flash("Iniciá sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if not g.usuario.es_admin():
            flash("Solo el Administrador puede acceder a esa sección.", "danger")
            return redirect(url_for("inicio.dashboard"))
        return funcion(*args, **kwargs)
    return envoltura


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("inicio.dashboard"))

    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Completá email y contraseña.", "danger")
        else:
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario and usuario.verificar_password(password):
                session.clear()
                session["id_usuario"] = usuario.id_usuario
                flash(f"¡Bienvenido/a, {usuario.nombre}!", "success")
                return redirect(url_for("inicio.dashboard"))
            # Mismo mensaje si falla el email o la clave: no se revela cuál de los dos está mal
            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html", email=email)


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
