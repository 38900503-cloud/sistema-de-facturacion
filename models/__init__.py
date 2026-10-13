from flask_sqlalchemy import SQLAlchemy

# Un único objeto db compartido por todos los modelos (ver clase "Flask ORM Modelos")
db = SQLAlchemy()

from models.usuario import Usuario
from models.cliente import Cliente
from models.producto import Producto
from models.factura import Factura, DetalleFactura
