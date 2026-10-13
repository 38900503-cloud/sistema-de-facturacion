"""
Definición de las entidades que administra el ABM genérico.

Igual que en el TP de Vehículos y Propietarios: cada entidad tiene una lista
de campos y un diccionario de reglas donde la CLAVE es el nombre del campo y
el VALOR es otro diccionario con sus reglas. validaciones.py es el único que
interpreta esas reglas.

Reglas posibles:
    etiqueta     texto que se muestra en el formulario y en la tabla
    obligatorio  True/False (si no se indica, el campo es obligatorio)
    tipo         "texto" (solo letras), "numero" (solo dígitos), "entero",
                 "decimal", "email" o "libre"
    largo_min / largo_max   cantidad de caracteres
    minimo / maximo         rango para "entero" y "decimal"
    unico        no puede repetirse en la tabla
    mensaje      mensaje propio (si no está, validaciones.py arma uno automático)
"""

# ---------------------------------------------------------------- Clientes
campos_cliente = ["nombre", "direccion", "telefono", "email"]

reglas_cliente = {
    "nombre": {
        "etiqueta": "Nombre / Razón social",
        "tipo": "texto",
        "largo_min": 2,
        "largo_max": 120,
    },
    "direccion": {
        "etiqueta": "Dirección",
        "obligatorio": False,
        "tipo": "libre",
        "largo_max": 200,
    },
    "telefono": {
        "etiqueta": "Teléfono",
        "tipo": "numero",
        "largo_min": 8,
        "largo_max": 15,
        "mensaje": "solo números, entre 8 y 15 dígitos (sin guiones ni espacios).",
    },
    "email": {
        "etiqueta": "Email",
        "tipo": "email",
        "largo_max": 120,
        "unico": True,
    },
}

# --------------------------------------------------------------- Productos
campos_producto = ["descripcion", "precio", "stock"]

reglas_producto = {
    "descripcion": {
        "etiqueta": "Descripción",
        "tipo": "libre",
        "largo_min": 2,
        "largo_max": 200,
        "unico": True,
    },
    "precio": {
        "etiqueta": "Precio",
        "tipo": "decimal",
        "minimo": 0.01,
        "maximo": 99999999,
    },
    "stock": {
        "etiqueta": "Stock",
        "tipo": "entero",
        "minimo": 0,
        "maximo": 100000,
    },
}
