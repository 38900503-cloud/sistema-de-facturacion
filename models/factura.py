from datetime import date
from models import db


class Factura(db.Model):
    __tablename__ = "facturas"
    id_factura = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    total = db.Column(db.Float, nullable=False, default=0)

    # Una factura tiene muchos renglones de detalle; si se borra la factura, se borran sus renglones
    detalles = db.relationship("DetalleFactura", backref="factura", lazy=True,
                               cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Factura {self.id_factura}>"


class DetalleFactura(db.Model):
    __tablename__ = "detalle_factura"
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey("facturas.id_factura"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("productos.id_producto"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)  # precio al momento de facturar
    subtotal = db.Column(db.Float, nullable=False)
