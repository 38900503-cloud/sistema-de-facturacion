from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from controllers.auth import login_requerido
from models import db, Cliente, Producto, Factura, DetalleFactura

bp = Blueprint("facturas", __name__, url_prefix="/facturas")


def leer_fecha(texto):
    """'AAAA-MM-DD' -> date. Devuelve None si viene vacío o mal escrito."""
    try:
        return date.fromisoformat(texto) if texto else None
    except ValueError:
        return None


# ---------------------------------------------------- CU-05 Consultar factura
@bp.route("/")
@login_requerido
def lista():
    id_cliente = request.args.get("cliente", type=int)
    desde = leer_fecha(request.args.get("desde"))
    hasta = leer_fecha(request.args.get("hasta"))

    if desde and hasta and desde > hasta:
        flash("La fecha 'Desde' no puede ser posterior a 'Hasta'.", "warning")
        desde = hasta = None

    consulta = Factura.query
    if id_cliente:
        consulta = consulta.filter_by(id_cliente=id_cliente)
    if desde:
        consulta = consulta.filter(Factura.fecha >= desde)
    if hasta:
        consulta = consulta.filter(Factura.fecha <= hasta)
    facturas = consulta.order_by(Factura.fecha.desc(), Factura.id_factura.desc()).all()

    clientes = Cliente.query.order_by(Cliente.nombre).all()
    return render_template("facturas/lista.html", facturas=facturas, clientes=clientes,
                           id_cliente=id_cliente, desde=desde, hasta=hasta)


@bp.route("/<int:id_factura>")
@login_requerido
def detalle(id_factura):
    factura = db.session.get(Factura, id_factura)
    if factura is None:
        flash(f"No existe la factura #{id_factura}.", "danger")
        return redirect(url_for("facturas.lista"))
    return render_template("facturas/detalle.html", factura=factura)


# ------------------------------------------------------ CU-04 Emitir factura
@bp.route("/nueva", methods=["GET", "POST"])
@login_requerido
def nueva():
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    productos = Producto.query.filter(Producto.stock > 0).order_by(Producto.descripcion).all()
    id_cliente = None
    renglones = []   # lo que cargó el usuario, para volver a mostrarlo si hay errores

    if request.method == "POST":
        id_cliente = request.form.get("id_cliente", type=int)
        ids_producto = request.form.getlist("id_producto")
        cantidades = request.form.getlist("cantidad")
        renglones = [{"id_producto": p, "cantidad": c} for p, c in zip(ids_producto, cantidades)]

        errores = []
        cliente = db.session.get(Cliente, id_cliente) if id_cliente else None
        if cliente is None:
            errores.append("Cliente: es obligatorio seleccionar uno.")

        # Se agrupan los renglones: si eligió el mismo producto dos veces, se suman las cantidades
        pedido = {}
        for numero, renglon in enumerate(renglones, start=1):
            if not renglon["id_producto"]:
                errores.append(f"Renglón {numero}: falta elegir el producto.")
            elif not renglon["cantidad"].isdigit() or int(renglon["cantidad"]) < 1:
                errores.append(f"Renglón {numero}: la cantidad debe ser un número entero mayor a 0.")
            else:
                id_p = int(renglon["id_producto"])
                pedido[id_p] = pedido.get(id_p, 0) + int(renglon["cantidad"])

        if not renglones:
            errores.append("Productos: agregá al menos un renglón.")

        # Control de stock (el precio y el stock se leen de la base, no del formulario)
        items = []
        for id_p, cantidad in pedido.items():
            producto = db.session.get(Producto, id_p)
            if producto is None:
                errores.append("Hay un producto que ya no existe.")
            elif cantidad > producto.stock:
                errores.append(f"Stock insuficiente para «{producto.descripcion}»: "
                               f"pediste {cantidad} y hay {producto.stock}.")
            else:
                items.append((producto, cantidad))

        if errores:
            for e in errores:
                flash(e, "danger")
        else:
            factura = Factura(cliente=cliente, fecha=date.today())
            total = 0
            for producto, cantidad in items:
                subtotal = round(producto.precio * cantidad, 2)
                factura.detalles.append(DetalleFactura(
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal,
                ))
                producto.stock -= cantidad
                total += subtotal
            factura.total = round(total, 2)

            db.session.add(factura)
            db.session.commit()   # factura + detalle + descuento de stock en una sola transacción
            flash(f"Factura #{factura.id_factura} emitida correctamente.", "success")
            return redirect(url_for("facturas.detalle", id_factura=factura.id_factura))

    return render_template("facturas/nueva.html", clientes=clientes, productos=productos,
                           id_cliente=id_cliente, renglones=renglones)
