# Sistema de Facturación Básico (Flask + AdminLTE)

Repositorio: https://github.com/38900503-cloud/sistema-de-facturacion

Sistema web en **Python + Flask** con patrón **MVC**, **ORM Flask-SQLAlchemy** y plantillas
**Jinja2** sobre **AdminLTE 3**. Gestiona clientes, productos y facturas, con reportes básicos y
login de usuarios, según el *Análisis Funcional — Sistema de Facturación Básico*.

## Autora

- Karen Maliandi

**Materia:** Programación — Prof. Cepeda Leandro

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python seed.py     # crea facturacion.db con datos de prueba (OJO: borra lo que haya)
python app.py      # abrir http://127.0.0.1:5000
```

| Usuario | Contraseña | Rol |
|---|---|---|
| admin@facturacion.com | admin123 | Administrador: todo el sistema |
| vendedor@facturacion.com | vendedor123 | Usuario autorizado: emitir/consultar facturas y reportes |

## Estructura del proyecto (MVC)

```
facturacion/
├── app.py              # Punto de entrada: crea la app, filtros Jinja, instancia los ABM y registra las rutas
├── config.py           # SECRET_KEY y SQLALCHEMY_DATABASE_URI
├── models/             # MODELO: clases db.Model
│   ├── __init__.py     #   db = SQLAlchemy()
│   ├── usuario.py
│   ├── cliente.py      #   Cliente 1 ── * Factura
│   ├── producto.py     #   Producto 1 ── * DetalleFactura
│   └── factura.py      #   Factura 1 ── * DetalleFactura
├── controllers/        # CONTROLADOR: rutas de Flask
│   ├── auth.py         #   CU-01 login / logout + decoradores login_requerido y solo_admin
│   ├── abm.py          #   CU-02 y CU-03: clase genérica ABMGenerico
│   ├── facturas.py     #   CU-04 emitir y CU-05 consultar
│   ├── reportes.py     #   CU-06 por cliente y CU-07 por período
│   └── inicio.py       #   Dashboard
├── templates/          # VISTA: Jinja2 + AdminLTE
│   ├── base.html       #   layout (herencia de plantillas)
│   ├── macros.html     #   macros reutilizables
│   ├── mensajes.html   #   subplantilla de flash() ({% include %})
│   ├── abm/            #   lista / form / confirmar_baja: genéricas para cualquier entidad
│   ├── facturas/
│   └── reportes/
├── static/css/
├── entidades.py        # Campos y reglas de validación por entidad (diccionario clave-valor)
├── validaciones.py     # Interpreta las reglas de entidades.py
├── repositorio.py      # RepositorioORM: único lugar que usa db.session para el ABM
├── seed.py             # Datos de prueba
├── capturas/           # Capturas del plan de pruebas
├── Plan_de_Pruebas_Facturacion.docx   # Casos de uso + plan de pruebas con capturas
└── PLAN_DE_PRUEBAS.md
```

## Casos de uso cubiertos

| Caso de uso | Actor | Ruta |
|---|---|---|
| CU-01 Iniciar / cerrar sesión | Todos | `/login`, `/logout` |
| CU-02 ABM Cliente | Administrador | `/clientes/` |
| CU-03 ABM Producto | Administrador | `/productos/` |
| CU-04 Emitir factura | Usuario autorizado | `/facturas/nueva` |
| CU-05 Consultar factura (por cliente o fecha → detalle) | Usuario autorizado | `/facturas/` |
| CU-06 Reporte facturas por cliente | Usuario autorizado | `/reportes/por-cliente` |
| CU-07 Reporte ventas por período | Usuario autorizado | `/reportes/por-periodo` |

## Requisitos aplicados (mismo enfoque que el TP de Vehículos y Propietarios)

| Requisito | Cómo se resuelve |
|---|---|
| Una clase genérica para el CRUD de 2+ entidades | `ABMGenerico` (en `controllers/abm.py`) recibe nombre, campos, reglas y un repositorio; en `app.py` se instancia igual para Clientes y Productos |
| Formularios generados dinámicamente | `templates/abm/form.html` arma los campos con `{% for campo in campos %}` usando la macro `campo_formulario` |
| Validaciones con diccionario clave-valor | Reglas en `entidades.py`, interpretadas por `validaciones.py`; un mensaje por campo |
| Separación interfaz / base de datos | `RepositorioORM` hace todo el acceso a datos; el ABM no usa `db.session` |
| Confirmación antes de eliminar | Pantalla «¿Seguro que querés eliminar…?» con «Sí, eliminar» / «No, volver» |
| Integridad referencial | No se puede borrar un cliente con facturas ni un producto facturado |
| Plan de pruebas documentado | [`Plan_de_Pruebas_Facturacion.docx`](Plan_de_Pruebas_Facturacion.docx): 30 casos con 35 capturas reales |

## Reglas de negocio de la facturación

- Al emitir se controla el stock y se descuenta. Factura, detalle y stock se guardan en un único `commit`.
- El precio se toma de la base de datos (no del formulario) y queda guardado en `detalle_factura`,
  así un cambio de precio posterior no altera las facturas ya emitidas.
- Si el mismo producto se carga en dos renglones, se suman las cantidades antes de controlar el stock.
