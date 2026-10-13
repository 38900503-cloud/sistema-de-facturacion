from datetime import date
from flask import Blueprint, render_template, request, flash
from sqlalchemy import func
from controllers.auth import login_requerido
from controllers.facturas import leer_fecha
from models import db, Cliente, Factura

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


# ------------------------------------------- CU-06 Reporte facturas por cliente
@bp.route("/por-cliente")
@login_requerido
def por_cliente():
    total = func.coalesce(func.sum(Factura.total), 0)
    filas = (
        db.session.query(
            Cliente.id_cliente,
            Cliente.nombre,
            func.count(Factura.id_factura).label("cantidad"),
            total.label("total"),
        )
        .outerjoin(Factura, Factura.id_cliente == Cliente.id_cliente)   # incluye clientes sin facturas
        .group_by(Cliente.id_cliente, Cliente.nombre)
        .order_by(total.desc())
        .all()
    )
    total_general = sum(f.total for f in filas)
    return render_template("reportes/por_cliente.html", filas=filas, total_general=total_general)


# -------------------------------------------- CU-07 Reporte ventas por período
@bp.route("/por-periodo")
@login_requerido
def por_periodo():
    hoy = date.today()
    desde = leer_fecha(request.args.get("desde")) or hoy.replace(day=1)   # por defecto: el mes actual
    hasta = leer_fecha(request.args.get("hasta")) or hoy
    if desde > hasta:
        flash("La fecha 'Desde' no puede ser posterior a 'Hasta'. Se muestra el mes actual.", "warning")
        desde, hasta = hoy.replace(day=1), hoy

    filas = (
        db.session.query(
            Factura.fecha,
            func.count(Factura.id_factura).label("cantidad"),
            func.sum(Factura.total).label("total"),
        )
        .filter(Factura.fecha >= desde, Factura.fecha <= hasta)
        .group_by(Factura.fecha)
        .order_by(Factura.fecha)
        .all()
    )
    return render_template("reportes/por_periodo.html", filas=filas, desde=desde, hasta=hasta,
                           total_general=sum(f.total for f in filas),
                           cantidad_total=sum(f.cantidad for f in filas))
