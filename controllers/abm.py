from flask import Blueprint, render_template, request, redirect, url_for, flash
from controllers.auth import solo_admin
from validaciones import validar


class ABMGenerico:
    """
    Controlador genérico de Alta, Baja, Modificación y Listado.

    Es la versión web de FormularioCRUD del TP de Vehículos y Propietarios:
    se instancia una vez por entidad (en app.py) variando solo los parámetros,
    y arma las mismas rutas y pantallas para Clientes y para Productos.
    No usa db.session: todo lo que es base de datos lo hace el repositorio.
    """

    def __init__(self, nombre, titulo, singular, icono, campos, reglas, repositorio,
                 campo_busqueda, relacion_que_impide_baja=None, mensaje_baja=""):
        self.nombre = nombre                  # se usa en la URL: /clientes, /productos
        self.titulo = titulo                  # "Clientes"
        self.singular = singular              # "cliente"
        self.icono = icono                    # ícono de Font Awesome para el menú
        self.campos = campos
        self.reglas = reglas
        self.repositorio = repositorio
        self.campo_busqueda = campo_busqueda
        self.relacion_que_impide_baja = relacion_que_impide_baja
        self.mensaje_baja = mensaje_baja

        self.bp = Blueprint(nombre, __name__, url_prefix=f"/{nombre}")
        self._registrar_rutas()

    # -------------------------------------------------------------- rutas
    def _registrar_rutas(self):
        self.bp.add_url_rule("/", "lista", solo_admin(self.lista))
        self.bp.add_url_rule("/nuevo", "nuevo", solo_admin(self.nuevo), methods=["GET", "POST"])
        self.bp.add_url_rule("/<int:id_registro>/editar", "editar", solo_admin(self.editar), methods=["GET", "POST"])
        self.bp.add_url_rule("/<int:id_registro>/eliminar", "eliminar", solo_admin(self.eliminar), methods=["GET", "POST"])

    def _contexto(self, **extra):
        """Datos que necesitan las plantillas genéricas abm/lista.html y abm/form.html."""
        return dict(abm=self, campos=self.campos, reglas=self.reglas, **extra)

    def _pk(self, registro):
        return getattr(registro, self.repositorio.pk.key)

    def _validar(self, excluir_id=None):
        """Valida el formulario con las reglas del diccionario y controla los campos 'unico'."""
        datos, errores = validar(request.form, self.campos, self.reglas)
        for campo in self.campos:
            regla = self.reglas.get(campo, {})
            if regla.get("unico") and campo not in errores and datos[campo]:
                if self.repositorio.existe(campo, datos[campo], excluir_id):
                    errores[campo] = f"{regla.get('etiqueta', campo)}: ya existe otro {self.singular} con ese valor."
        return datos, errores

    # ------------------------------------------------------------ Listado
    def lista(self):
        buscar = request.args.get("buscar", "").strip()
        registros = self.repositorio.listar(self.campo_busqueda, buscar, orden=self.campo_busqueda)
        return render_template("abm/lista.html", **self._contexto(registros=registros, buscar=buscar))

    # --------------------------------------------------------------- Alta
    def nuevo(self):
        valores, errores = {}, {}
        if request.method == "POST":
            valores, errores = self._validar()
            if not errores:
                registro = self.repositorio.crear(valores)
                flash(f"{self.singular.capitalize()} #{self._pk(registro)} creado correctamente.", "success")
                return redirect(url_for(f"{self.nombre}.lista"))
            valores = request.form  # se devuelve lo que escribió el usuario para que no lo pierda
        return render_template("abm/form.html", **self._contexto(
            valores=valores, errores=errores, accion="Nuevo"))

    # ------------------------------------------------------- Modificación
    def editar(self, id_registro):
        registro = self.repositorio.obtener(id_registro)
        if registro is None:
            flash(f"No existe el {self.singular} #{id_registro}.", "danger")
            return redirect(url_for(f"{self.nombre}.lista"))

        valores = {campo: getattr(registro, campo) for campo in self.campos}
        errores = {}
        if request.method == "POST":
            datos, errores = self._validar(excluir_id=id_registro)
            if not errores:
                self.repositorio.actualizar(registro, datos)
                flash(f"{self.singular.capitalize()} #{id_registro} modificado correctamente.", "success")
                return redirect(url_for(f"{self.nombre}.lista"))
            valores = request.form
        return render_template("abm/form.html", **self._contexto(
            valores=valores, errores=errores, accion="Editar", registro=registro, id_registro=id_registro))

    # --------------------------------------------------------------- Baja
    def eliminar(self, id_registro):
        registro = self.repositorio.obtener(id_registro)
        if registro is None:
            flash(f"No existe el {self.singular} #{id_registro}.", "danger")
            return redirect(url_for(f"{self.nombre}.lista"))

        # Regla de negocio: no se borra lo que ya está usado en facturas
        if self.relacion_que_impide_baja and getattr(registro, self.relacion_que_impide_baja):
            flash(self.mensaje_baja, "warning")
            return redirect(url_for(f"{self.nombre}.lista"))

        if request.method == "POST":
            if request.form.get("confirmar") == "si":
                self.repositorio.eliminar(registro)
                flash(f"{self.singular.capitalize()} #{id_registro} eliminado.", "success")
            else:
                flash("Eliminación cancelada. No se borró nada.", "info")
            return redirect(url_for(f"{self.nombre}.lista"))

        # GET: pantalla de confirmación "¿Seguro?" con botones Sí / No
        return render_template("abm/confirmar_baja.html", **self._contexto(
            registro=registro, id_registro=id_registro))
