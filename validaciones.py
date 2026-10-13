"""
Interpreta las reglas definidas en entidades.py.

No sabe nada de Flask ni de la base de datos: recibe los datos del
formulario (diccionario campo -> texto) y las reglas, y devuelve:
    - datos: los valores ya limpios y convertidos (int / float)
    - errores: diccionario campo -> mensaje (vacío si está todo bien)
"""
import re

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SIGNOS_PERMITIDOS_EN_TEXTO = " .'-&"   # para "Comercial Sur S.A.", "D'Angelo", etc.


def _es_texto(valor):
    tiene_letra = any(c.isalpha() for c in valor)
    return tiene_letra and all(c.isalpha() or c in SIGNOS_PERMITIDOS_EN_TEXTO for c in valor)


def validar(datos_formulario, campos, reglas):
    datos = {}
    errores = {}

    for campo in campos:
        regla = reglas.get(campo, {})
        etiqueta = regla.get("etiqueta", campo)
        valor = (datos_formulario.get(campo) or "").strip()
        error = None

        # Un campo que no diga lo contrario es obligatorio
        if valor == "":
            if regla.get("obligatorio", True):
                errores[campo] = f"{etiqueta}: es obligatorio."
            datos[campo] = None if regla.get("tipo") in ("entero", "decimal") else ""
            continue

        tipo = regla.get("tipo", "libre")
        largo_min = regla.get("largo_min")
        largo_max = regla.get("largo_max")

        if largo_min and len(valor) < largo_min:
            error = f"debe tener al menos {largo_min} caracteres."
        elif largo_max and len(valor) > largo_max:
            error = f"no puede superar los {largo_max} caracteres."
        elif tipo == "texto" and not _es_texto(valor):
            error = "debe contener solo letras."
        elif tipo == "numero" and not valor.isdigit():
            error = "debe contener solo números."
        elif tipo == "email" and not PATRON_EMAIL.match(valor):
            error = "no tiene un formato de email válido (ejemplo: nombre@dominio.com)."
        elif tipo == "entero":
            if not valor.isdigit():
                error = "debe ser un número entero sin signos ni decimales."
            else:
                valor = int(valor)
        elif tipo == "decimal":
            texto_numero = valor.replace(",", ".")
            # Solo dígitos y a lo sumo un punto: así se rechazan "1e5", "inf", "-3", etc.
            if texto_numero.replace(".", "", 1).isdigit():
                valor = round(float(texto_numero), 2)
            else:
                error = "debe ser un número (se acepta coma o punto para los decimales)."

        # Rango (solo para números ya convertidos)
        if error is None and tipo in ("entero", "decimal"):
            if "minimo" in regla and valor < regla["minimo"]:
                error = f"no puede ser menor que {regla['minimo']}."
            elif "maximo" in regla and valor > regla["maximo"]:
                error = f"no puede ser mayor que {regla['maximo']}."

        if error:
            # Si la regla tiene mensaje propio, se usa ese en lugar del automático
            errores[campo] = f"{etiqueta}: {regla.get('mensaje', error)}"
        datos[campo] = valor

    return datos, errores
