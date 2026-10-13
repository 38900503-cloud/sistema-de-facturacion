"""
Carga datos de prueba. OJO: borra y vuelve a crear todas las tablas.
Uso:  python seed.py
"""
from datetime import date, timedelta
from app import app
from models import db, Usuario, Cliente, Producto, Factura, DetalleFactura

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = Usuario(nombre="Administrador", email="admin@facturacion.com", rol="admin")
    admin.set_password("admin123")
    vendedor = Usuario(nombre="Vendedor", email="vendedor@facturacion.com", rol="vendedor")
    vendedor.set_password("vendedor123")
    db.session.add_all([admin, vendedor])

    juan = Cliente(nombre="Juan Pérez", direccion="Av. Rivadavia 1234, CABA",
                   telefono="1145678901", email="juan.perez@mail.com")
    maria = Cliente(nombre="María Gómez", direccion="Calle 50 N° 456, La Plata",
                    telefono="2214567890", email="maria.gomez@mail.com")
    comercial = Cliente(nombre="Comercial Sur S.A.", direccion="Av. Mitre 800, Avellaneda",
                        telefono="1142223333", email="compras@comercialsur.com")
    db.session.add_all([juan, maria, comercial])

    mouse = Producto(descripcion="Mouse inalámbrico", precio=8500, stock=40)
    teclado = Producto(descripcion="Teclado USB", precio=12000, stock=25)
    monitor = Producto(descripcion="Monitor 24 pulgadas", precio=185000, stock=8)
    auriculares = Producto(descripcion="Auriculares", precio=15500, stock=4)
    pendrive = Producto(descripcion="Pendrive 64GB", precio=9900, stock=60)
    db.session.add_all([mouse, teclado, monitor, auriculares, pendrive])

    def emitir(cliente, items, dias_atras):
        factura = Factura(cliente=cliente, fecha=date.today() - timedelta(days=dias_atras))
        total = 0
        for producto, cantidad in items:
            subtotal = producto.precio * cantidad
            factura.detalles.append(DetalleFactura(producto=producto, cantidad=cantidad,
                                                   precio_unitario=producto.precio, subtotal=subtotal))
            producto.stock -= cantidad
            total += subtotal
        factura.total = total
        db.session.add(factura)

    emitir(juan, [(mouse, 2), (teclado, 1)], 10)
    emitir(maria, [(monitor, 1)], 5)
    emitir(comercial, [(pendrive, 10), (mouse, 5)], 2)
    emitir(juan, [(auriculares, 1)], 0)
    db.session.commit()

print("Base de datos inicializada.")
print("  admin@facturacion.com    / admin123     (Administrador)")
print("  vendedor@facturacion.com / vendedor123  (Vendedor)")
