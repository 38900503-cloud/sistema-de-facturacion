from models import db


class Producto(db.Model):
    __tablename__ = "productos"
    id_producto = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), unique=True, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)

    # Un producto puede aparecer en muchos renglones de factura
    detalles = db.relationship("DetalleFactura", backref="producto", lazy=True)

    def __repr__(self):
        return f"<Producto {self.descripcion}>"
