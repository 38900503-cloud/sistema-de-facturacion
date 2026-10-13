from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # se guarda el hash, no la clave
    rol = db.Column(db.String(20), nullable=False, default="vendedor")  # "admin" o "vendedor"

    def set_password(self, clave):
        self.password = generate_password_hash(clave)

    def verificar_password(self, clave):
        return check_password_hash(self.password, clave)

    def es_admin(self):
        return self.rol == "admin"

    def __repr__(self):
        return f"<Usuario {self.email}>"
