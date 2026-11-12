r"""Pruebas de las cifras de control definidas en AGENTS.md (Entrega 10).

Valida contra los insumos (solo lectura) y las reglas de negocio:
- 10 áreas en Directorio_Áreas
- 3 canales de ingreso válidos
- 8 tipos documentales catalogados (TD-001 a TD-008)
- 10 registros simulados en Registro_Correspondencia
- 5 etapas del flujo de trabajo
- SLAs de recepción y respuesta
- Estados válidos
- Formato de radicado ^ADEP-\d{4}-\d{4}$ (R1)
"""
import re

from app.services.reglas_negocio import (
    CANALES_VALIDOS,
    ESTADOS_VALIDOS,
    RADICADO_PATTERN,
    SLA_RECEPCION,
    SLA_RESPUESTA,
    validar_formato_radicado,
)

COL_ID_AREA = "ID Área"
COL_NOMBRE_AREA = "Nombre del Área / Departamento"
COL_CODIGO_CANAL = "Código Canal"
COL_NOMBRE_CANAL = "Nombre del Canal"
COL_SLA_RECEPCION = "SLA Recepción (Horas)"
COL_CODIGO_TIPO = "Código Tipo"
COL_CATEGORIA = "Categoría / Documento"
COL_RADICADO = "N° Radicado"
COL_CANAL_INGRESO = "Canal Ingreso"
COL_TIPO_DOCUMENTO = "Tipo Documento"
COL_AREA_ASIGNADA = "Área Asignada"
COL_RESPONSABLE = "Responsable Atención"
COL_PRIORIDAD = "Prioridad"
COL_ESTADO = "Estado Actual"
COL_LIMITE = "Fecha Límite Respuesta"
COL_UBICACION = "Ubicación Archivo / Link"
COL_ETAPA = "Etapa del Proceso"


def test_hay_10_areas_en_directorio(datos_insumos):
    areas = datos_insumos["directorio_areas"]
    assert len(areas) == 10
    assert [a[COL_ID_AREA] for a in areas] == [f"DIR-{i:03d}" for i in range(1, 11)]
    nombres = [a[COL_NOMBRE_AREA] for a in areas]
    assert "Asesoría Legal y Jurídica" in nombres


def test_hay_3_canales_de_ingreso(datos_insumos):
    canales = datos_insumos["canales"]
    assert len(canales) == 3
    assert [c[COL_CODIGO_CANAL] for c in canales] == ["CAN-01", "CAN-02", "CAN-03"]
    assert {c[COL_NOMBRE_CANAL] for c in canales} == CANALES_VALIDOS


def test_sla_recepcion_por_canal(datos_insumos):
    sla_excel = {c[COL_NOMBRE_CANAL]: c[COL_SLA_RECEPCION] for c in datos_insumos["canales"]}
    assert sla_excel["WhatsApp Corporativo"] == "2 hrs"
    assert sla_excel["Correo Institucional"] == "4 hrs"
    assert sla_excel["Recepción Física"] == "1 hr"
    assert SLA_RECEPCION["WhatsApp Corporativo"] == 2
    assert SLA_RECEPCION["Correo Institucional"] == 4
    assert SLA_RECEPCION["Recepción Física"] == 1


def test_hay_8_tipos_documentales(datos_insumos):
    tipos = datos_insumos["tipologia_documental"]
    assert len(tipos) == 8
    assert [t[COL_CODIGO_TIPO] for t in tipos] == [f"TD-{i:03d}" for i in range(1, 9)]
    assert {t[COL_CATEGORIA] for t in tipos} == {
        "Solicitud de Afiliación / Desafiliación",
        "Solicitud de Incapacidad / Ayuda Económica",
        "Notificación Judicial / Recurso Legal",
        "Factura de Proveedor / Cobro",
        "Oficio Institucional (MEP / JUPEMA / CCSS)",
        "Consulta General / Sugerencia de Asociado",
        "Invitación a Evento / Asamblea Exterior",
        "Cotización / Propuesta Comercial",
    }


def test_hay_10_registros_simulados(datos_insumos):
    registros = datos_insumos["registro_correspondencia"]
    assert len(registros) == 10
    radicados = [r[COL_RADICADO] for r in registros]
    assert len(set(radicados)) == 10  # sin duplicados en los insumos
    assert all(r[COL_CANAL_INGRESO] in CANALES_VALIDOS for r in registros)


def test_hay_5_etapas_del_flujo(datos_insumos):
    etapas = datos_insumos["contexto_ia_y_matriz"]["etapas"]
    assert len(etapas) == 5
    nombres = [e[COL_ETAPA] for e in etapas]
    assert nombres[0].startswith("1. Captura")
    assert nombres[1].startswith("2. Clasificación")
    assert nombres[2].startswith("3. Enrutamiento")
    assert nombres[3].startswith("4. Gestión")
    assert nombres[4].startswith("5. Cierre")


def test_sla_respuesta_por_prioridad():
    assert SLA_RESPUESTA == {"Urgente": 1, "Alta": 2, "Media": 3, "Baja": 5}


def test_estados_validos():
    assert ESTADOS_VALIDOS == {
        "Recibido",
        "Asignado",
        "En Tramite",
        "Cerrado",
        "Pendiente de Confirmación",
    }


def test_formato_de_radicado_cumple_r1():
    assert re.match(RADICADO_PATTERN, "ADEP-2026-0001") is not None
    assert re.match(RADICADO_PATTERN, "ADEP-2026-0009") is not None
    assert validar_formato_radicado("ADEP-2026-0001") is True
    assert validar_formato_radicado("ADEP-2026-0009") is True


def test_formato_de_radicado_rechaza_valores_invalidos():
    assert validar_formato_radicado("ADEP-2026-00010") is False  # 5 dígitos al final
    assert validar_formato_radicado("ADEP-2026-1") is False
    assert validar_formato_radicado("ADEP-26-0001") is False
    assert validar_formato_radicado("ABC-2026-0001") is False
    assert validar_formato_radicado("") is False


def test_todos_los_radicados_de_los_registros_cumplen_r1(datos_insumos):
    """Cifra de control: los 10 radicados de Registro_Correspondencia deben
    cumplir el formato obligatorio ADEP-AAAA-XXXX (R1)."""
    registros = datos_insumos["registro_correspondencia"]
    invalidos = [
        r[COL_RADICADO]
        for r in registros
        if not validar_formato_radicado(r[COL_RADICADO])
    ]
    assert invalidos == [], f"Radicados que violan R1: {invalidos}"
