"""Pruebas de las reglas de negocio R1-R6 de app/services/reglas_negocio.py."""
import re

from app.services.reglas_negocio import (
    CANALES_VALIDOS,
    ESTADOS_VALIDOS,
    PRIORIDADES_VALIDAS,
    RADICADO_PATTERN,
    SLA_RECEPCION,
    SLA_RESPUESTA,
    TIPOS_LEGALES,
    forzar_prioridad_legal,
    obtener_dias_respuesta,
    obtener_sla_recepcion,
    validar_autorizacion,
    validar_canal,
    validar_estado,
    validar_formato_radicado,
    validar_prioridad,
)


def test_validar_formato_radicado():
    assert validar_formato_radicado("ADEP-2026-0001") is True
    assert validar_formato_radicado("ADEP-2026-0009") is True
    assert validar_formato_radicado("ADEP-2026-00010") is False  # 5 dígitos
    assert validar_formato_radicado("ADEP-2026-1") is False
    assert validar_formato_radicado("ABC-2026-0001") is False
    assert validar_formato_radicado("") is False
    assert re.match(RADICADO_PATTERN, "ADEP-2026-0001") is not None


def test_validar_estado():
    for estado in ESTADOS_VALIDOS:
        assert validar_estado(estado) is True
    assert validar_estado("Anulado") is False
    assert validar_estado("") is False
    assert validar_estado(123) is False


def test_validar_canal():
    for canal in CANALES_VALIDOS:
        assert validar_canal(canal) is True
        assert obtener_sla_recepcion(canal) is not None
    assert validar_canal("Telegram") is False
    assert validar_canal("") is False
    assert obtener_sla_recepcion("Telegram") is None


def test_sla_recepcion_valores():
    assert SLA_RECEPCION == {
        "WhatsApp Corporativo": 2,
        "Correo Institucional": 4,
        "Recepción Física": 1,
    }


def test_sla_respuesta_valores():
    assert SLA_RESPUESTA == {"Urgente": 1, "Alta": 2, "Media": 3, "Baja": 5}
    for prioridad in PRIORIDADES_VALIDAS:
        assert validar_prioridad(prioridad) is True
        assert obtener_dias_respuesta(prioridad) is not None
    assert obtener_dias_respuesta("Crítica") is None


def test_forzar_prioridad_legal_por_tipo_documento():
    for tipo in TIPOS_LEGALES:
        resultado = forzar_prioridad_legal(tipo, "cualquier asunto")
        assert resultado == {
            "prioridad": "Urgente",
            "area": "Asesoría Legal y Jurídica",
            "forzada": True,
        }


def test_forzar_prioridad_legal_por_palabra_clave():
    resultado = forzar_prioridad_legal("Solicitud de Afiliación", "vence el plazo judicial")
    assert resultado["forzada"] is True
    assert resultado["prioridad"] == "Urgente"
    assert resultado["area"] == "Asesoría Legal y Jurídica"


def test_forzar_prioridad_legal_no_se_activa_sin_indicios():
    resultado = forzar_prioridad_legal("Factura de Proveedor / Cobro", "pago de servicios de internet")
    assert resultado["forzada"] is False
    assert resultado["prioridad"] is None
    assert resultado["area"] is None


def test_validar_autorizacion():
    assert validar_autorizacion("Secretaria", "Unidad Secretarial")["autorizado"] is True
    assert validar_autorizacion("Recepcionista", "Recepción")["autorizado"] is True
    assert validar_autorizacion("Jefe de Finanzas", "Gestión Financiera y Contabilidad")["autorizado"] is False
    assert validar_autorizacion("", "Unidad Secretarial")["autorizado"] is False
