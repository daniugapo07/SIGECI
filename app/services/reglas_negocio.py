"""Reglas de negocio R1 a R6 de SIGECI.

Implementa como código de aplicación (sin intervención de IA) las reglas
definidas en AGENTS.md:

- R1: formato obligatorio del número de radicado ADEP-AAAA-XXXX.
- R2: estados válidos de un documento.
- R3: canales válidos de ingreso y SLA de recepción por canal (horas).
- R4: SLA de respuesta por prioridad (días hábiles).
- R5: prioridad forzada para asuntos legales / plazos judiciales.
- R6: reglas de autorización, constancia de recepción y ubicación física.
"""

import re

# Patrón obligatorio del número de radicado: ADEP-AAAA-XXXX.
RADICADO_PATTERN = r"^ADEP-\d{4}-\d{4}$"

# Estados válidos de un documento según AGENTS.md.
ESTADOS_VALIDOS = {
    "Recibido",
    "Asignado",
    "En Tramite",
    "Cerrado",
    "Pendiente de Confirmación",
}


def validar_formato_radicado(radicado):
    """R1 — Valida el formato obligatorio del número de radicado.

    Implementa la regla: el radicado debe tener el formato ADEP-AAAA-XXXX
    (prefijo "ADEP", guion, 4 dígitos del año, guion, 4 dígitos consecutivos).

    Args:
        radicado (str): número de radicado a validar.

    Returns:
        bool: True si el formato es válido, False en caso contrario.
    """
    if not isinstance(radicado, str):
        return False
    return bool(re.match(RADICADO_PATTERN, radicado))


def validar_estado(estado):
    """R2 — Valida que el estado de un documento sea uno de los válidos.

    Implementa la regla: los únicos estados permitidos son
    Recibido, Asignado, En Tramite, Cerrado y Pendiente de Confirmación.

    Args:
        estado (str): estado a validar.

    Returns:
        bool: True si el estado es válido, False en caso contrario.
    """
    if not isinstance(estado, str):
        return False
    return estado in ESTADOS_VALIDOS


# Canales válidos de ingreso según AGENTS.md.
CANALES_VALIDOS = {
    "WhatsApp Corporativo",
    "Correo Institucional",
    "Recepción Física",
}

# SLAs de recepción por canal (horas) según AGENTS.md.
SLA_RECEPCION = {
    "WhatsApp Corporativo": 2,
    "Correo Institucional": 4,
    "Recepción Física": 1,
}


def validar_canal(canal):
    """R3 — Valida que el canal de ingreso sea uno de los canales válidos.

    Implementa la regla: los únicos canales de ingreso permitidos son
    WhatsApp Corporativo, Correo Institucional y Recepción Física.

    Args:
        canal (str): nombre del canal de ingreso a validar.

    Returns:
        bool: True si el canal es válido, False en caso contrario.
    """
    if not isinstance(canal, str):
        return False
    return canal in CANALES_VALIDOS


def obtener_sla_recepcion(canal):
    """R3 — Devuelve el SLA de recepción (en horas) de un canal válido.

    Implementa la regla de SLA de recepción por canal:
    WhatsApp Corporativo = 2 hrs, Correo Institucional = 4 hrs,
    Recepción Física = 1 hr.

    Args:
        canal (str): nombre del canal de ingreso.

    Returns:
        int: horas del SLA de recepción si el canal es válido, None si no.
    """
    if not validar_canal(canal):
        return None
    return SLA_RECEPCION[canal]


# Prioridades válidas de respuesta según AGENTS.md.
PRIORIDADES_VALIDAS = {"Urgente", "Alta", "Media", "Baja"}

# SLAs de respuesta por prioridad (días hábiles) según AGENTS.md.
SLA_RESPUESTA = {
    "Urgente": 1,
    "Alta": 2,
    "Media": 3,
    "Baja": 5,
}


def validar_prioridad(prioridad):
    """R4 — Valida que la prioridad sea una de las prioridades válidas.

    Implementa la regla: las únicas prioridades permitidas son
    Urgente, Alta, Media y Baja.

    Args:
        prioridad (str): prioridad a validar.

    Returns:
        bool: True si la prioridad es válida, False en caso contrario.
    """
    if not isinstance(prioridad, str):
        return False
    return prioridad in PRIORIDADES_VALIDAS


def obtener_dias_respuesta(prioridad):
    """R4 — Devuelve los días hábiles de respuesta de una prioridad válida.

    Implementa la regla de SLA de respuesta por prioridad:
    Urgente = 1 día, Alta = 2 días, Media = 3 días, Baja = 5 días.

    Args:
        prioridad (str): prioridad del documento.

    Returns:
        int: días hábiles de respuesta si la prioridad es válida, None si no.
    """
    if not validar_prioridad(prioridad):
        return None
    return SLA_RESPUESTA[prioridad]


# Tipos documentales que forzan prioridad Urgente según AGENTS.md.
TIPOS_LEGALES = {"Notificación Judicial", "Recurso Legal"}

# Palabras clave en el asunto que forzan prioridad Urgente según AGENTS.md.
PALABRAS_CLAVE_LEGALES = {"judicial", "plazo"}


def forzar_prioridad_legal(tipo_documento, asunto):
    """R5 — Prioridad forzada para asuntos legales / plazos judiciales.

    Implementa la regla: si tipo_documento es "Notificación Judicial" o
    "Recurso Legal", o si el asunto contiene "judicial" o "plazo"
    (insensible a mayúsculas), se fuerza prioridad="Urgente" y
    area_asignada="Asesoría Legal y Jurídica". La IA solo sugiere; esta
    regla de aplicación tiene prioridad sobre cualquier sugerencia de IA.

    Args:
        tipo_documento (str): tipo de documento del registro.
        asunto (str): asunto / resumen del documento.

    Returns:
        dict: {"prioridad": str, "area": str, "forzada": bool}. Cuando
              se activa la regla, prioridad="Urgente" y
              area="Asesoría Legal y Jurídica".
    """
    asunto_lower = (asunto or "").lower()
    es_legal = (
        tipo_documento in TIPOS_LEGALES
        or any(palabra in asunto_lower for palabra in PALABRAS_CLAVE_LEGALES)
    )
    if es_legal:
        return {
            "prioridad": "Urgente",
            "area": "Asesoría Legal y Jurídica",
            "forzada": True,
        }
    return {
        "prioridad": None,
        "area": None,
        "forzada": False,
    }


# Roles autorizados para validar asignaciones finales según AGENTS.md.
ROLES_AUTORIZADOS = {"Unidad Secretarial", "Recepción"}

# Registro de constancias de recepción / traslado (fecha, hora, usuario).
MOVIMIENTOS_REGISTRADOS = []


def validar_autorizacion(usuario, rol):
    """R6 — Valida que el usuario tenga rol autorizado para validar asignaciones.

    Implementa la regla de autorización: solo personal autorizado
    (Unidad Secretarial / Recepción) valida la asignación final de un
    documento. La IA nunca distribuye documentos libremente; solo sugiere
    área y responsable.

    Args:
        usuario (str): nombre o identificador del usuario.
        rol (str): rol del usuario.

    Returns:
        dict: {"autorizado": bool, "usuario": str, "rol": str, "motivo": str}.
    """
    if not isinstance(usuario, str) or not usuario.strip():
        return {
            "autorizado": False,
            "usuario": usuario,
            "rol": rol,
            "motivo": "Usuario no válido.",
        }
    if rol in ROLES_AUTORIZADOS:
        return {
            "autorizado": True,
            "usuario": usuario,
            "rol": rol,
            "motivo": "Rol autorizado para validar asignación.",
        }
    return {
        "autorizado": False,
        "usuario": usuario,
        "rol": rol,
        "motivo": "Rol no autorizado para validar asignación.",
    }


def registrar_movimiento(documento_id, accion, usuario, fecha, hora):
    """R6 — Registra una constancia de recepción/traslado de un documento.

    Implementa la regla de trazabilidad: cualquier movimiento (recibir,
    trasladar, asignar, cerrar) debe registrar fecha, hora y usuario
    ejecutor (constancia de recepción). Se lleva registro de la ubicación
    física del documento a través de la acción registrada.

    Args:
        documento_id (str): número de radicado o identificador del documento.
        accion (str): tipo de movimiento (ej. "Recepción", "Traslado",
                      "Asignación", "Cierre").
        usuario (str): usuario que ejecuta el movimiento.
        fecha (str): fecha del movimiento (YYYY-MM-DD).
        hora (str): hora del movimiento (HH:MM).

    Returns:
        dict: el movimiento registrado con documento_id, accion, usuario,
              fecha y hora.
    """
    movimiento = {
        "documento_id": documento_id,
        "accion": accion,
        "usuario": usuario,
        "fecha": fecha,
        "hora": hora,
    }
    MOVIMIENTOS_REGISTRADOS.append(movimiento)
    return movimiento
