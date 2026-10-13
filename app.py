from flask import Flask
from config import Config
from models import db, Cliente, Producto
from repositorio import RepositorioORM
from entidades import campos_cliente, reglas_cliente, campos_producto, reglas_producto
from controllers.abm import ABMGenerico
from controllers import auth, inicio, facturas, reportes

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


# ------------------------------------------------------ Filtros propios de Jinja2
@app.template_filter("moneda")
def moneda(valor):
    """1234.5 -> '$ 1.234,50' (formato argentino)."""
    texto = f"{float(valor or 0):,.2f}"
    return "$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("formato_fecha")
def formato_fecha(fecha):
    """date -> 'dd/mm/aaaa'."""
    return fecha.strftime("%d/%m/%Y") if fecha else ""


# ---------------------------------------- ABM: la misma clase para las 2 entidades
abm_clientes = ABMGenerico(
    nombre="clientes", titulo="Clientes", singular="cliente", icono="fa-users",
    campos=campos_cliente, reglas=reglas_cliente,
    repositorio=RepositorioORM(Cliente, "id_cliente"),
    campo_busqueda="nombre",
    relacion_que_impide_baja="facturas",
    mensaje_baja="No se puede eliminar: el cliente tiene facturas emitidas.",
)

abm_productos = ABMGenerico(
    nombre="productos", titulo="Productos", singular="producto", icono="fa-box",
    campos=campos_producto, reglas=reglas_producto,
    repositorio=RepositorioORM(Producto, "id_producto"),
    campo_busqueda="descripcion",
    relacion_que_impide_baja="detalles",
    mensaje_baja="No se puede eliminar: el producto figura en facturas emitidas.",
)

ABMS = [abm_clientes, abm_productos]


@app.context_processor
def datos_para_todas_las_plantillas():
    # base.html arma el menú lateral recorriendo esta lista
    return {"abms": ABMS}


# --------------------------------------------------------- Registro de rutas
app.register_blueprint(auth.bp)
app.register_blueprint(inicio.bp)
app.register_blueprint(facturas.bp)
app.register_blueprint(reportes.bp)
for abm in ABMS:
    app.register_blueprint(abm.bp)


if __name__ == "__main__":
    app.run(debug=True)
