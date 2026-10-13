from datetime import date
from flask import Blueprint, render_template, redirect, url_for, g
from sqlalchemy import func
from controllers.auth import login_requerido
from models import db, Cliente, Producto, Factura

bp = Blueprint("inicio", __name__)


@bp.route("/")
def home():
    return redirect(url_for("inicio.dashboard" if g.usuario else "auth.login"))


@bp.route("/dashboard")
@login_requerido
def dashboard():
    inicio_mes = date.today().replace(day=1)
    ventas_mes = (db.session.query(func.coalesce(func.sum(Factura.total), 0))
                  .filter(Factura.fecha >= inicio_mes).scalar())
    return render_template(
        "dashboard.html",
        cant_clientes=Cliente.query.count(),
        cant_productos=Producto.query.count(),
        cant_facturas=Factura.query.count(),
        ventas_mes=ventas_mes,
        ultimas=Factura.query.order_by(Factura.id_factura.desc()).limit(5).all(),
        poco_stock=Producto.query.filter(Producto.stock <= 5).order_by(Producto.stock).all(),
    )
