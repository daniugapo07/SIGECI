"""Pruebas de los 7 casos límite definidos en AGENTS.md (Entrega 10).

Cada prueba documenta el comportamiento esperado. Cuando la aplicación se
desvía de AGENTS.md, la prueba falla (o documenta el comportamiento actual)
para reportar la causa probable en el informe de validación.
"""
from datetime import date, datetime

import app.controllers.main as controlador
from app.controllers.main import DOCUMENTOS, generar_radicado
from app.services.agente_ia import analizar_documento
from app.services.reglas_negocio import (
    ESTADOS_VALIDOS,
    forzar_prioridad_legal,
    validar_canal,
    validar_estado,
    validar_formato_radicado,
)

COL_RADICADO = "N° Radicado"
COL_CANAL_INGRESO = "Canal Ingreso"
COL_TIPO_DOCUMENTO = "Tipo Documento"
COL_AREA_ASIGNADA = "Área Asignada"
COL_PRIORIDAD = "Prioridad"
COL_ESTADO = "Estado Actual"
COL_LIMITE = "Fecha Límite Respuesta"

FECHA_HOY = date(2026, 11, 4)  # fecha del entorno según el enunciado


def _post_registro(client, **campos):
    datos = {
        "canal_ingreso": "Recepción Física",
        "texto_extraido": "texto de prueba",
        "fecha_ingreso": "2026-11-04",
        "hora_ingreso": "09:00",
        "remitente": "Remitente de prueba",
        "asunto": "Asunto de prueba",
        "usuario": "Recepcionista",
    }
    datos.update(campos)
    return client.post("/registrar", json=datos)


# Caso límite 1: documento escaneado sin texto legible (OCR fallido) -> revisión manual
def test_ocr_fallido_sin_texto_sugiere_revision_manual(client):
    """Sin llave de Gemini configurada la IA no puede analizar; el controlador
    no asigna definitivamente y sugiere revisión manual en observaciones."""
    salida = analizar_documento(
        "", "WhatsApp Corporativo", "2026-11-04", "09:00", [], []
    )
    assert "error" in salida
    assert "Gemini" in salida["error"]

    respuesta = _post_registro(client, texto_extraido="", asunto="Escaneo sin texto legible")
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert "Revisión manual sugerida" in cuerpo["documento"]["observaciones"]


# Caso límite 2: prioridad conflictiva (plazo judicial) -> Urgente + Asesoría Legal
def test_plazo_judicial_forza_urgente_y_asesoria_legal():
    resultado = forzar_prioridad_legal("Notificación Judicial", "Recurso de amparo")
    assert resultado["forzada"] is True
    assert resultado["prioridad"] == "Urgente"
    assert resultado["area"] == "Asesoría Legal y Jurídica"

    resultado = forzar_prioridad_legal("Solicitud de Afiliación", "vence el plazo hoy")
    assert resultado["forzada"] is True
    assert resultado["prioridad"] == "Urgente"


def test_registro_con_plazo_judicial_aplica_r5(client):
    respuesta = _post_registro(
        client,
        texto_extraido="notificación judicial",
        asunto="Plazo judicial: recurso de amparo contra resolución",
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["prioridad"] == "Urgente"
    assert cuerpo["area_asignada"] == "Asesoría Legal y Jurídica"
    assert cuerpo["ia_forzada"] is True


# Caso límite 3: remitente no identificado o canal no reconocido -> revisión manual
def test_canal_no_reconocido_se_rechaza(client):
    respuesta = _post_registro(client, canal_ingreso="Canal Inexistente")
    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"] == "Canal de ingreso no válido."


def test_canal_no_es_valido_según_las_reglas():
    assert validar_canal("Canal Inexistente") is False
    assert validar_canal("Telegram") is False


def test_remitente_no_identificado_no_marca_revision_manual(client):
    """Comportamiento actual: la app acepta un remitente vacío sin marcar
    revisión manual (AGENTS.md indica que debería marcarse para revisión)."""
    respuesta = _post_registro(client, remitente="")
    assert respuesta.status_code == 201
    assert respuesta.get_json()["documento"]["remitente"] == ""


# Caso límite 4: área destino inexistente -> no se puede asignar
def test_area_inexistente_no_esta_en_directorio(datos_insumos):
    areas_validas = {
        a["Nombre del Área / Departamento"] for a in datos_insumos["directorio_areas"]
    }
    assert "Área Inexistente" not in areas_validas


def test_controlador_almacena_area_inexistente_sin_validarla(monkeypatch, client):
    """Comportamiento actual: el controlador almacena el área sugerida aunque
    no exista en el Directorio. AGENTS.md dice que no se puede asignar."""
    def falso_analisis(*args, **kwargs):
        return {
            "radicado": "ADEP-2026-0050",
            "tipo_documento": "Otro",
            "prioridad": "Media",
            "area_asignada": "Área Inexistente",
            "responsable_sugerido": "Nadie",
            "fecha_limite_respuesta": "2026-11-10",
            "observaciones": "prueba de área inexistente",
        }

    monkeypatch.setattr(controlador, "analizar_documento", falso_analisis)
    respuesta = _post_registro(client, canal_ingreso="Correo Institucional")
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["area_asignada"] == "Área Inexistente"


# Caso límite 5: fecha límite vencida -> alerta inmediata
def test_registros_con_limite_vencido_hoy(datos_insumos):
    """A la fecha de entorno (2026-11-04), los registros no cerrados con
    límite anterior a hoy deben considerarse vencidos."""
    vencidos = []
    for r in datos_insumos["registro_correspondencia"]:
        if r[COL_ESTADO] == "Cerrado":
            continue
        try:
            limite = datetime.strptime(r[COL_LIMITE], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if limite < FECHA_HOY:
            vencidos.append(r[COL_RADICADO])
    assert set(vencidos) == {"ADEP-2026-0001", "ADEP-2026-0002", "ADEP-2026-0004"}


def test_detalle_de_documento_vencido_muestra_alerta(client):
    respuesta = client.get("/detalle/ADEP-2026-0001")
    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)
    assert "Alerta" in html
    assert "venció" in html

    respuesta_ok = client.get("/detalle/ADEP-2026-0003")
    assert "Alerta" not in respuesta_ok.get_data(as_text=True)


# Caso límite 6: radicado duplicado -> se rechaza y se genera uno nuevo
def test_generar_radicado_no_duplica_y_cumple_formato():
    radicado = generar_radicado()
    assert validar_formato_radicado(radicado) is True
    assert radicado not in DOCUMENTOS
    assert radicado.startswith("ADEP-2026-")


def test_ante_duplicado_se_genera_nuevo_consecutivo():
    DOCUMENTOS["ADEP-2026-00011"] = {"radicado": "ADEP-2026-00011"}
    nuevo = generar_radicado()
    assert nuevo == "ADEP-2026-0012"  # 4 dígitos (formato R1): 11 + 1 = 12 -> "0012"
    assert nuevo not in DOCUMENTOS
    assert validar_formato_radicado(nuevo) is True


# Caso límite 7: documento sin confirmación -> permanece Pendiente de Confirmación
def test_estado_pendiente_de_confirmacion_es_valido():
    assert validar_estado("Pendiente de Confirmación") is True
    assert "Pendiente de Confirmación" in ESTADOS_VALIDOS


def test_documento_sin_confirmacion_permanece_pendiente(client):
    controlador.DOCUMENTOS["ADEP-2026-0099"] = {
        "radicado": "ADEP-2026-0099",
        "fecha_ingreso": "2026-11-04",
        "hora_ingreso": "09:00",
        "canal_ingreso": "Recepción Física",
        "remitente": "Remitente no identificado",
        "asunto": "Documento pendiente de confirmar",
        "tipo_documento": "Otro",
        "area_asignada": "",
        "responsable_sugerido": "",
        "responsable_atencion": "",
        "prioridad": "Media",
        "estado_actual": "Pendiente de Confirmación",
        "fecha_limite_respuesta": "2026-11-09",
        "observaciones": "Espera de confirmación del responsable.",
        "texto_extraido": "",
        "ubicacion": "Recepción",
        "historial": [],
        "fuente": "prueba",
    }
    respuesta = client.get("/detalle/ADEP-2026-0099")
    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)
    assert "Pendiente de Confirmación" in html
    assert controlador.DOCUMENTOS["ADEP-2026-0099"]["estado_actual"] == "Pendiente de Confirmación"


def test_registro_nuevo_tiene_estado_inicial_recibido(client):
    respuesta = _post_registro(client)
    assert respuesta.status_code == 201
    assert respuesta.get_json()["estado_actual"] == "Recibido"
