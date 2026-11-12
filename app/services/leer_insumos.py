"""Servicio de lectura de insumos de SIGECI.

Lee el archivo Excel de insumos y devuelve los datos de las 4 hojas:
Directorio_Áreas, Canales_y_Tipología, Registro_Correspondencia y
Contexto_IA_y_Matriz.

Este servicio solo consulta el archivo en modo lectura (data_only=True);
nunca modifica la carpeta insumos/.
"""

import os

import openpyxl

# Ruta del archivo de insumos, resuelta a partir de la ubicación de este
# archivo (app/services/) hacia la raíz del proyecto.
RAIZ_PROYECTO = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
RUTA_INSUMOS = os.path.join(
    RAIZ_PROYECTO, "INSUMOS", "Insumos_ADEP_Gestion_Correspondencia.xlsx"
)

# Texto esperado en la primera celda de cada bloque de encabezado.
ENCABEZADO_DIRECTORIO = "ID Área"
ENCABEZADO_CANALES = "Código Canal"
ENCABEZADO_TIPOLOGIA = "Código Tipo"
ENCABEZADO_REGISTRO = "N° Radicado"
ENCABEZADO_ETAPAS = "Etapa del Proceso"


def _buscar_fila_encabezado(ws, texto_primera_columna):
    """Devuelve el número de fila (1-based) cuya primera celda contiene
    exactamente el texto de encabezado indicado.

    Las hojas de insumos tienen filas de título antes del encabezado real, por
    lo que se busca dinámicamente en lugar de asumir un número de fila fijo.
    """
    # Los encabezados de las hojas de insumos están en la columna B (la
    # columna A está vacía). Se busca en la columna B de forma dinámica.
    for fila in ws.iter_rows(min_col=2, max_col=2):
        celda = fila[0]
        if celda.value is not None and str(celda.value).strip() == texto_primera_columna:
            return celda.row
    return None


def _leer_bloque(ws, fila_encabezado):
    """Lee las filas de datos a partir de la fila de encabezado hasta encontrar
    una fila completamente vacía.

    Returns:
        list[dict]: cada fila es un diccionario claveado por el encabezado de
        su columna.
    """
    encabezados = [c.value for c in ws[fila_encabezado]]
    datos = []
    for fila in ws.iter_rows(min_row=fila_encabezado + 1, values_only=True):
        if all(celda is None or str(celda).strip() == "" for celda in fila):
            break
        registro = {}
        for idx, encabezado in enumerate(encabezados):
            if encabezado is None:
                continue
            valor = fila[idx] if idx < len(fila) else None
            registro[str(encabezado).strip()] = valor
        datos.append(registro)
    return datos


def _extraer_prompt_base(ws):
    """Extrae el texto del prompt base sugerido de la hoja
    Contexto_IA_y_Matriz."""
    for fila in ws.iter_rows(values_only=True):
        for celda in fila:
            if isinstance(celda, str) and celda.strip().startswith("Actúas como"):
                return celda.strip()
    return ""


def leer_insumos(ruta_archivo=RUTA_INSUMOS):
    """Lee las 4 hojas del Excel de insumos y devuelve sus datos.

    Returns:
        dict: con las claves:
            - directorio_areas (list): 10 áreas del Directorio_Áreas.
            - canales (list): 3 canales de ingreso de Canales_y_Tipología.
            - tipologia_documental (list): 8 tipos de Canales_y_Tipología.
            - registro_correspondencia (list): 10 registros de
              Registro_Correspondencia.
            - contexto_ia_y_matriz (dict): etapas del flujo y prompt base de
              Contexto_IA_y_Matriz.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
    resultado = {}

    # Hoja 1: Directorio de Áreas (10 registros, filas 6-15).
    ws = wb["Directorio_Áreas"]
    fila = _buscar_fila_encabezado(ws, ENCABEZADO_DIRECTORIO)
    resultado["directorio_areas"] = _leer_bloque(ws, fila)

    # Hoja 2: Canales y Tipología (3 canales + 8 tipos).
    ws = wb["Canales_y_Tipologia"]
    fila_canales = _buscar_fila_encabezado(ws, ENCABEZADO_CANALES)
    resultado["canales"] = _leer_bloque(ws, fila_canales)
    fila_tipologia = _buscar_fila_encabezado(ws, ENCABEZADO_TIPOLOGIA)
    resultado["tipologia_documental"] = _leer_bloque(ws, fila_tipologia)

    # Hoja 3: Registro de Correspondencia (10 registros, filas 7-16).
    ws = wb["Registro_Correspondencia"]
    fila = _buscar_fila_encabezado(ws, ENCABEZADO_REGISTRO)
    resultado["registro_correspondencia"] = _leer_bloque(ws, fila)

    # Hoja 4: Contexto IA y Matriz (5 etapas + prompt base).
    ws = wb["Contexto_IA_y_Matriz"]
    fila_etapas = _buscar_fila_encabezado(ws, ENCABEZADO_ETAPAS)
    resultado["contexto_ia_y_matriz"] = {
        "etapas": _leer_bloque(ws, fila_etapas),
        "prompt_base": _extraer_prompt_base(ws),
    }

    return resultado
