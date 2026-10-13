import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave_secreta_cambiar")
    # SQLite para desarrollo local (ver presentación "Conexión a BD con Flask-SQLAlchemy").
    # Para otro motor alcanza con cambiar la URI, sin tocar los modelos.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "facturacion.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
