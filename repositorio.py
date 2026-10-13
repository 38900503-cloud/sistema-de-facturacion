from models import db


class RepositorioORM:
    """
    Repositorio genérico: sabe listar/crear/actualizar/borrar filas de UN
    modelo usando el ORM (db.session). No sabe nada de rutas ni de HTML.

    Es la versión con SQLAlchemy de RepositorioSQLite del TP anterior:
    se instancia pasándole el modelo y la clave primaria, y la misma clase
    sirve para Clientes y para Productos.
    """

    def __init__(self, modelo, clave_primaria):
        self.modelo = modelo
        self.pk = getattr(modelo, clave_primaria)

    def listar(self, campo_busqueda=None, texto=None, orden=None):
        consulta = self.modelo.query
        if campo_busqueda and texto:
            consulta = consulta.filter(getattr(self.modelo, campo_busqueda).ilike(f"%{texto}%"))
        if orden:
            consulta = consulta.order_by(getattr(self.modelo, orden))
        return consulta.all()

    def obtener(self, id_registro):
        return db.session.get(self.modelo, id_registro)

    def existe(self, campo, valor, excluir_id=None):
        """True si ya hay otro registro con ese valor (para la regla 'unico')."""
        consulta = self.modelo.query.filter(getattr(self.modelo, campo) == valor)
        if excluir_id is not None:
            consulta = consulta.filter(self.pk != excluir_id)
        return consulta.first() is not None

    def crear(self, datos):
        registro = self.modelo(**datos)
        db.session.add(registro)
        db.session.commit()
        return registro

    def actualizar(self, registro, datos):
        for campo, valor in datos.items():
            setattr(registro, campo, valor)
        db.session.commit()

    def eliminar(self, registro):
        db.session.delete(registro)
        db.session.commit()
