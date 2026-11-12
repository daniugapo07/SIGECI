"""Servicio de integración con el agente de IA (Gemini) de SIGECI.

Entrega 5 — Integración del agente de IA con contrato JSON y la llave en .env.

Este servicio se comunica con la API de Gemini
(generativelanguage.googleapis.com) para analizar un documento de
correspondencia y devolver una sugerencia en el contrato JSON definido en
AGENTS.md:

Entrada:
  { documento: { texto_extraido, canal_ingreso, fecha_ingreso, hora_ingreso },
    directorio_areas: [...], tipologia_documental: [...] }

Salida (sugerencia de la IA, nunca asignación definitiva):
  { radicado, tipo_documento, prioridad, area_asignada,
    responsable_sugerido, fecha_limite_respuesta, observaciones }

IMPORTANTE: La IA SOLO SUGIERE. Nunca asigna definitivamente ni distribuye
documentos libremente. La validación final corresponde a un usuario
autorizado (Unidad Secretarial / Recepción), según las reglas de negocio
de AGENTS.md.
"""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (si existe).
load_dotenv()

# Llave de API de Gemini leída de .env.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Modelo de Gemini a utilizar.
GEMINI_MODEL = "gemini-1.5-flash-latest"

# Valor placeholder que indica que la llave no está configurada.
GEMINI_PLACEHOLDER = "TU_LLAVE_DE_GEMINI_AQUI"

# Campos obligatorios de la salida del contrato JSON.
CAMPOS_SALIDA = [
    "radicado",
    "tipo_documento",
    "prioridad",
    "area_asignada",
    "responsable_sugerido",
    "fecha_limite_respuesta",
    "observaciones",
]


def _llave_configurada():
    """Devuelve True si GEMINI_API_KEY tiene un valor real distinto del
    placeholder. False si no hay llave o si aún es el placeholder."""
    if not GEMINI_API_KEY or not GEMINI_API_KEY.strip():
        return False
    return GEMINI_API_KEY.strip() != GEMINI_PLACEHOLDER


def armar_entrada(texto_extraido, canal_ingreso, fecha_ingreso, hora_ingreso,
                  directorio_areas, tipologia_documental):
    """Arma el JSON de entrada según el contrato de AGENTS.md."""
    return {
        "documento": {
            "texto_extraido": texto_extraido,
            "canal_ingreso": canal_ingreso,
            "fecha_ingreso": fecha_ingreso,
            "hora_ingreso": hora_ingreso,
        },
        "directorio_areas": directorio_areas,
        "tipologia_documental": tipologia_documental,
    }


def _construir_prompt(entrada):
    """Construye el prompt (en español) que se envía a Gemini.

    Pide al modelo que actúe como asistente virtual de la Unidad Secretarial
    de ADEP, analice el documento, clasifique tipo/prioridad, sugiera área y
    responsable, y responda ÚNICAMENTE con JSON válido del contrato.
    """
    directorio_json = json.dumps(
        entrada["directorio_areas"], ensure_ascii=False, indent=2
    )
    tipologia_json = json.dumps(
        entrada["tipologia_documental"], ensure_ascii=False, indent=2
    )
    doc = entrada["documento"]

    prompt = f"""
Actúas como el asistente virtual de la Unidad Secretarial de la Asociación
de Educadores Pensionados (ADEP). Analiza la correspondencia entrante y
devuelve una SUGERENCIA (nunca una asignación definitiva) en formato JSON.

DATOS DEL DOCUMENTO:
- Texto extraído (OCR): {doc['texto_extraido']}
- Canal de ingreso: {doc['canal_ingreso']}
- Fecha de ingreso: {doc['fecha_ingreso']}
- Hora de ingreso: {doc['hora_ingreso']}

DIRECTORIO DE ÁREAS (solo para sugerir área/responsable):
{directorio_json}

TIPOLOGÍA DOCUMENTAL (para clasificar el tipo de documento):
{tipologia_json}

REGLAS DE NEGOCIO (aplícalas como guía para tu sugerencia):
- Formato de radicado obligatorio: ADEP-AAAA-XXXX.
- Prioridades y días hábiles de respuesta: Urgente=1, Alta=2, Media=3, Baja=5.
- Si el asunto implica aspectos legales o plazos judiciales (ej. notificación
  judicial, recurso legal, plazo), sugiere prioridad "Urgente" y área
  "Asesoría Legal y Jurídica".
- La IA solo sugiere área y responsable; nunca asigna definitivamente.

INSTRUCCIÓN DE SALIDA:
Responde ÚNICAMENTE con un objeto JSON válido (sin texto adicional, sin
bloques de código markdown) con exactamente estos campos:
- radicado (string, formato ADEP-AAAA-XXXX)
- tipo_documento (string, uno de los tipos de la tipología o "Otro")
- prioridad (string: "Urgente", "Alta", "Media" o "Baja")
- area_asignada (string, nombre del área del directorio)
- responsable_sugerido (string, responsable del área sugerida)
- fecha_limite_respuesta (string, formato YYYY-MM-DD)
- observaciones (string)

Si el texto extraído no es legible o falta información, indícalo en
observaciones y sugiere revisión manual.
""".strip()
    return prompt


def _llamar_gemini(prompt):
    """Envía el prompt a la API de Gemini y devuelve el texto de respuesta.

    Raises:
        RuntimeError: si la llave no está configurada o la API devuelve error.
    """
    if not _llave_configurada():
        raise RuntimeError(
            "GEMINI_API_KEY no está configurada en .env. "
            "Reemplaza el placeholder TU_LLAVE_DE_GEMINI_AQUI por tu llave real."
        )

    cuerpo = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
    url = (
        "https://generativelanguage.googleapis.com/v1beta"
        f"/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    req = urllib.request.Request(
        url,
        data=datos,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as respuesta:
            leido = respuesta.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Error de la API de Gemini ({exc.code}): {detalle}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"No se pudo conectar con la API de Gemini: {exc}")

    try:
        payload = json.loads(leido)
    except json.JSONDecodeError:
        raise RuntimeError("La API de Gemini no devolvió JSON válido.")

    # Extraer el texto generado del candidato.
    candidatos = payload.get("candidates", [])
    if not candidatos:
        raise RuntimeError("La API de Gemini no devolvió candidatos.")
    partes = candidatos[0].get("content", {}).get("parts", [])
    if not partes:
        raise RuntimeError("La respuesta de Gemini no contiene partes de texto.")
    texto = partes[0].get("text", "")
    return texto


def _extraer_json_de_texto(texto):
    """Extrae un objeto JSON de un texto que puede venir envuelto en bloques
    de markdown (```json ... ```) o con texto adicional alrededor."""
    texto = texto.strip()

    # Eliminar bloques de código markdown si los hay.
    if "```" in texto:
        inicio = texto.find("```")
        fin = texto.find("```", inicio + 3)
        if fin != -1:
            bloque = texto[inicio + 3:fin]
            bloque = bloque.strip()
            if bloque.lower().startswith("json"):
                bloque = bloque[4:].strip()
            texto = bloque.strip()
        else:
            texto = texto[inicio + 3:].strip()

    # Buscar la primera llave de apertura y la última de cierre.
    primero = texto.find("{")
    ultimo = texto.rfind("}")
    if primero != -1 and ultimo != -1 and ultimo > primero:
        texto = texto[primero:ultimo + 1]

    return json.loads(texto)


def _validar_salida(salida):
    """Devuelve True si la salida del agente tiene todos los campos del
    contrato JSON."""
    if not isinstance(salida, dict):
        return False
    for campo in CAMPOS_SALIDA:
        if campo not in salida:
            return False
    return True


def analizar_documento(texto_extraido, canal_ingreso, fecha_ingreso, hora_ingreso,
                       directorio_areas, tipologia_documental):
    """Envía un documento al agente de IA (Gemini) y devuelve la sugerencia
    en contrato JSON de AGENTS.md.

    La respuesta de la IA es solo una SUGERENCIA: radicado, tipo_documento,
    prioridad, area_asignada, responsable_sugerido, fecha_limite_respuesta
    y observaciones. Nunca se asigna definitivamente aquí; un usuario
    autorizado debe validar la asignación final.

    Args:
        texto_extraido (str): resultado del OCR / extracción de texto.
        canal_ingreso (str): canal de ingreso válido.
        fecha_ingreso (str): fecha de ingreso (YYYY-MM-DD).
        hora_ingreso (str): hora de ingreso (HH:MM).
        directorio_areas (list): lista de áreas del Directorio_Áreas.
        tipologia_documental (list): lista de tipos documentales.

    Returns:
        dict: salida del agente con los campos del contrato, o un dict con
        la clave "error" cuando no se puede llamar a la API o la respuesta
        no es válida.
    """
    if not _llave_configurada():
        return {
            "error": (
                "No se encontró una llave de API de Gemini válida en .env. "
                "Configura GEMINI_API_KEY con tu llave real de Gemini en el "
                "archivo .env y reinicia la aplicación."
            )
        }

    entrada = armar_entrada(
        texto_extraido, canal_ingreso, fecha_ingreso, hora_ingreso,
        directorio_areas, tipologia_documental,
    )
    prompt = _construir_prompt(entrada)

    try:
        texto_respuesta = _llamar_gemini(prompt)
        salida = _extraer_json_de_texto(texto_respuesta)
    except (RuntimeError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}

    if not _validar_salida(salida):
        return {
            "error": (
                "La respuesta del agente no contiene todos los campos del "
                "contrato JSON. Campos requeridos: "
                + ", ".join(CAMPOS_SALIDA)
            ),
            "respuesta_cruda": salida,
        }

    return salida


def analizar_desde_insumos(texto_extraido, canal_ingreso, fecha_ingreso,
                           hora_ingreso, ruta_insumos=None):
    """Conveniencia: lee directorio y tipología de los insumos y llama al
    agente de IA. Útil para pruebas sin armar la entrada manualmente."""
    from app.services.leer_insumos import leer_insumos, RUTA_INSUMOS

    datos = leer_insumos(ruta_insumos or RUTA_INSUMOS)
    return analizar_documento(
        texto_extraido=texto_extraido,
        canal_ingreso=canal_ingreso,
        fecha_ingreso=fecha_ingreso,
        hora_ingreso=hora_ingreso,
        directorio_areas=datos["directorio_areas"],
        tipologia_documental=datos["tipologia_documental"],
    )
