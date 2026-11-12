"""Controlador principal de rutas de SIGECI."""

import json
import os
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, make_response, redirect, render_template, request, session, url_for

from app.services.agente_ia import analizar_documento
from app.services.leer_insumos import leer_insumos, RUTA_INSUMOS
from app.services.reglas_negocio import (
    CANALES_VALIDOS,
    ESTADOS_VALIDOS,
    PRIORIDADES_VALIDAS,
    RADICADO_PATTERN,
    MOVIMIENTOS_REGISTRADOS,
    PALABRAS_CLAVE_LEGALES,
    ROLES_AUTORIZADOS,
    SLA_RECEPCION,
    SLA_RESPUESTA,
    TIPOS_LEGALES,
    obtener_dias_respuesta,
    obtener_sla_recepcion,
    forzar_prioridad_legal,
    validar_autorizacion,
    validar_canal,
    validar_estado,
    validar_formato_radicado,
    validar_prioridad,
    registrar_movimiento,
)

main_bp = Blueprint("main", __name__)

# Rutas que no requieren autenticación
_RUTAS_LIBRES = {"main.login", "main.salir", "main.health"}


@main_bp.before_request
def _requerir_autenticacion():
    """Regla de acceso: todas las rutas exigen sesión activa, excepto login, salir y health."""
    if request.endpoint not in _RUTAS_LIBRES and not session.get("usuario"):
        return redirect(url_for("main.login"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Pantalla de inicio de sesión con usuario y contraseña desde variables de entorno."""
    error = None
    if request.method == "POST":
        usuario = (request.form.get("usuario") or "").strip()
        clave = (request.form.get("clave") or "").strip()
        usuario_valido = os.environ.get("APP_USUARIO", "")
        clave_valida = os.environ.get("APP_CLAVE", "")
        if usuario == usuario_valido and clave == clave_valida:
            session["usuario"] = usuario
            return redirect(url_for("main.index"))
        error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)


@main_bp.route("/salir")
def salir():
    """Cierra la sesión del usuario y redirige al login."""
    session.pop("usuario", None)
    return redirect(url_for("main.login"))


@main_bp.route("/")
def index():
    """Pantalla de inicio de la aplicación."""
    return render_template("inicio.html")


@main_bp.route("/health")
def health():
    """Endpoint de salud duplicado en el blueprint (por consistencia de rutas)."""
    return {"status": "ok"}


@main_bp.route("/insumos/resumen")
def insumos_resumen():
    """Devuelve un resumen de los insumos leídos de las 4 hojas del Excel.

    Responde con la cantidad de áreas, canales, tipos documentales y
    registros de correspondencia (cifras de control de AGENTS.md).
    """
    datos = leer_insumos()
    resumen = {
        "areas": len(datos["directorio_areas"]),
        "canales": len(datos["canales"]),
        "tipos_documentales": len(datos["tipologia_documental"]),
        "registros_correspondencia": len(datos["registro_correspondencia"]),
        "etapas_flujo": len(datos["contexto_ia_y_matriz"]["etapas"]),
    }
    return jsonify(resumen)


@main_bp.route("/insumos")
def insumos_completo():
    """Devuelve todos los datos de las 4 hojas del Excel de insumos."""
    return jsonify(leer_insumos())


@main_bp.route("/reglas/validar-radicado/<radicado>")
def reglas_validar_radicado(radicado):
    """R1: valida que un radicado cumpla el formato ADEP-AAAA-XXXX."""
    valido = validar_formato_radicado(radicado)
    return jsonify({
        "regla": "R1 - formato de radicado",
        "patron": RADICADO_PATTERN,
        "radicado": radicado,
        "valido": valido,
    })


@main_bp.route("/reglas/validar-estado/<estado>")
def reglas_validar_estado(estado):
    """R2: valida que un estado sea uno de los estados válidos."""
    valido = validar_estado(estado)
    return jsonify({
        "regla": "R2 - estados válidos",
        "estados_validos": sorted(ESTADOS_VALIDOS),
        "estado": estado,
        "valido": valido,
    })


@main_bp.route("/reglas/sla-recepcion/<canal>")
def reglas_sla_recepcion(canal):
    """R3: devuelve el SLA de recepción (horas) de un canal válido."""
    valido = validar_canal(canal)
    horas = obtener_sla_recepcion(canal)
    return jsonify({
        "regla": "R3 - SLA de recepción por canal",
        "canales_validos": sorted(CANALES_VALIDOS),
        "sla_recepcion": SLA_RECEPCION,
        "canal": canal,
        "valido": valido,
        "sla_horas": horas,
    })


@main_bp.route("/reglas/dias-respuesta/<prioridad>")
def reglas_dias_respuesta(prioridad):
    """R4: devuelve los días hábiles de respuesta de una prioridad válida."""
    valido = validar_prioridad(prioridad)
    dias = obtener_dias_respuesta(prioridad)
    return jsonify({
        "regla": "R4 - SLA de respuesta por prioridad",
        "prioridades_validas": sorted(PRIORIDADES_VALIDAS),
        "sla_respuesta": SLA_RESPUESTA,
        "prioridad": prioridad,
        "valido": valido,
        "dias_habiles": dias,
    })


@main_bp.route("/reglas/forzar-legal")
def reglas_forzar_legal():
    """R5: prioridad forzada para asuntos legales / plazos judiciales.

    Query params: tipo_documento, asunto.
    """
    tipo_documento = request.args.get("tipo_documento", "")
    asunto = request.args.get("asunto", "")
    resultado = forzar_prioridad_legal(tipo_documento, asunto)
    return jsonify({
        "regla": "R5 - prioridad forzada para asuntos legales / plazos judiciales",
        "tipos_legales": sorted(TIPOS_LEGALES),
        "palabras_clave_legales": sorted(PALABRAS_CLAVE_LEGALES),
        "tipo_documento": tipo_documento,
        "asunto": asunto,
        "prioridad": resultado["prioridad"],
        "area": resultado["area"],
        "forzada": resultado["forzada"],
    })


@main_bp.route("/reglas/validar-autorizacion")
def reglas_validar_autorizacion():
    """R6: valida que un usuario tenga rol autorizado para validar asignaciones.

    Query params: usuario, rol.
    """
    usuario = request.args.get("usuario", "")
    rol = request.args.get("rol", "")
    resultado = validar_autorizacion(usuario, rol)
    return jsonify({
        "regla": "R6 - reglas de autorización",
        "roles_autorizados": sorted(ROLES_AUTORIZADOS),
        "usuario": usuario,
        "rol": rol,
        "autorizado": resultado["autorizado"],
        "motivo": resultado["motivo"],
    })


@main_bp.route("/reglas/registrar-movimiento", methods=["POST"])
def reglas_registrar_movimiento():
    """R6: registra una constancia de recepción/traslado (fecha, hora, usuario).

    Body JSON: documento_id, accion, usuario, fecha, hora.
    """
    data = request.get_json(silent=True) or {}
    documento_id = data.get("documento_id", "")
    accion = data.get("accion", "")
    usuario = data.get("usuario", "")
    fecha = data.get("fecha", "")
    hora = data.get("hora", "")
    movimiento = registrar_movimiento(documento_id, accion, usuario, fecha, hora)
    return jsonify({
        "regla": "R6 - constancia de recepción / ubicación física",
        "movimiento": movimiento,
        "total_movimientos": len(MOVIMIENTOS_REGISTRADOS),
    }), 201


@main_bp.route("/agente/analizar", methods=["POST"])
def agente_analizar():
    """POST /agente/analizar — Envía un documento al agente de IA (Gemini).

    La IA solo SUGIERE clasificación, prioridad, área y responsable.
    Nunca asigna definitivamente ni distribuye documentos libremente.

    Body JSON:
      texto_extraido, canal_ingreso, fecha_ingreso, hora_ingreso
      (opcional) directorio_areas, tipologia_documental
    """
    data = request.get_json(silent=True) or {}
    texto_extraido = data.get("texto_extraido", "")
    canal_ingreso = data.get("canal_ingreso", "")
    fecha_ingreso = data.get("fecha_ingreso", "")
    hora_ingreso = data.get("hora_ingreso", "")
    directorio_areas = data.get("directorio_areas")
    tipologia_documental = data.get("tipologia_documental")

    # Si no se envían directorio/tipología, leerlos de los insumos.
    if directorio_areas is None or tipologia_documental is None:
        datos_insumos = leer_insumos(RUTA_INSUMOS)
        if directorio_areas is None:
            directorio_areas = datos_insumos["directorio_areas"]
        if tipologia_documental is None:
            tipologia_documental = datos_insumos["tipologia_documental"]

    resultado = analizar_documento(
        texto_extraido=texto_extraido,
        canal_ingreso=canal_ingreso,
        fecha_ingreso=fecha_ingreso,
        hora_ingreso=hora_ingreso,
        directorio_areas=directorio_areas,
        tipologia_documental=tipologia_documental,
    )
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado)


# ============================================================================
# Almacenamiento temporal de documentos (Entrega 6).
# No hay base de datos configurada; se usa estructura en memoria persistida
# en un archivo JSON (app/data/documentos.json) mientras la app corre.
# ============================================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "documentos.json")

DOCUMENTOS: dict = {}


def _asegurar_directorio_datos():
    os.makedirs(DATA_DIR, exist_ok=True)


def _cargar_documentos():
    global DOCUMENTOS
    _asegurar_directorio_datos()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, dict):
                DOCUMENTOS = datos
        except (json.JSONDecodeError, OSError):
            DOCUMENTOS = {}


def _guardar_documentos():
    _asegurar_directorio_datos()
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DOCUMENTOS, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _semillar_desde_insumos():
    """Carga los 10 registros simulados de insumos como documentos iniciales."""
    global DOCUMENTOS
    if DOCUMENTOS:
        return
    try:
        datos_insumos = leer_insumos(RUTA_INSUMOS)
    except Exception:
        return
    for reg in datos_insumos.get("registro_correspondencia", []):
        radicado = reg.get("N° Radicado")
        if not radicado or not validar_formato_radicado(radicado):
            continue
        DOCUMENTOS[radicado] = {
            "radicado": radicado,
            "fecha_ingreso": reg.get("Fecha Ingreso") or "",
            "hora_ingreso": reg.get("Hora") or "",
            "canal_ingreso": reg.get("Canal Ingreso") or "",
            "remitente": reg.get("Remitente (Nombre / Entidad)") or "",
            "asunto": reg.get("Asunto / Resumen del Documento") or "",
            "tipo_documento": reg.get("Tipo Documento") or "Otro",
            "area_asignada": reg.get("Área Asignada") or "",
            "responsable_sugerido": reg.get("Responsable Atención") or "",
            "responsable_atencion": reg.get("Responsable Atención") or "",
            "prioridad": reg.get("Prioridad") or "Media",
            "estado_actual": reg.get("Estado Actual") or "Recibido",
            "fecha_limite_respuesta": reg.get("Fecha Límite Respuesta") or "",
            "observaciones": "Registro cargado desde insumos simulados.",
            "texto_extraido": "",
            "ubicacion": reg.get("Ubicación Archivo / Link") or "Recepción",
            "historial": [],
            "fuente": "insumos",
        }


_cargar_documentos()
_semillar_desde_insumos()


def _consecutivo_para_anio(anio):
    prefijo = f"ADEP-{anio}-"
    maximo = 0
    for radicado in DOCUMENTOS:
        if radicado.startswith(prefijo):
            try:
                numero = int(radicado[len(prefijo):])
                if numero > maximo:
                    maximo = numero
            except ValueError:
                continue
    return maximo


def generar_radicado():
    """Genera un radicado único y consecutivo con formato ADEP-AAAA-XXXX (R1)."""
    anio = date.today().year
    prefijo = f"ADEP-{anio}-"
    consecutivo = _consecutivo_para_anio(anio) + 1
    radicado = f"{prefijo}{consecutivo:04d}"
    while radicado in DOCUMENTOS:
        consecutivo += 1
        radicado = f"{prefijo}{consecutivo:04d}"
    return radicado


def _calcular_fecha_limite(fecha_ingreso_str, prioridad):
    """Calcula la fecha límite de respuesta con el SLA de la prioridad (R4)."""
    dias = obtener_dias_respuesta(prioridad)
    if dias is None:
        dias = SLA_RESPUESTA.get("Media", 3)
    try:
        fecha = datetime.strptime(fecha_ingreso_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        fecha = date.today()
    return (fecha + timedelta(days=dias)).strftime("%Y-%m-%d")


def obtener_historial(radicado):
    """Devuelve el historial de trazabilidad (movimientos) de un documento."""
    historial = []
    visto = set()
    documento = DOCUMENTOS.get(radicado)
    if documento:
        for mov in documento.get("historial", []):
            clave = (mov.get("accion"), mov.get("fecha"), mov.get("hora"))
            if clave not in visto:
                visto.add(clave)
                historial.append(dict(mov))
    for mov in MOVIMIENTOS_REGISTRADOS:
        if mov.get("documento_id") != radicado:
            continue
        clave = (mov.get("accion"), mov.get("fecha"), mov.get("hora"))
        if clave in visto:
            continue
        visto.add(clave)
        historial.append(dict(mov))
    return historial


# ---------------------------------------------------------------------------
# Rutas de la aplicación (Entrega 6)
# ---------------------------------------------------------------------------


@main_bp.route("/registrar", methods=["GET"])
def registrar_form():
    """Pantalla con formulario para registrar correspondencia física/digital."""
    return render_template("inicio.html")


@main_bp.route("/registrar", methods=["POST"])
def registrar_procesar():
    """Procesa el registro: genera radicado, aplica R1-R6, llama al agente IA y guarda."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    canal_ingreso = (data.get("canal_ingreso") or "").strip()
    fecha_ingreso = (data.get("fecha_ingreso") or "").strip() or date.today().strftime("%Y-%m-%d")
    hora_ingreso = (data.get("hora_ingreso") or "").strip() or datetime.now().strftime("%H:%M")
    remitente = (data.get("remitente") or "").strip()
    asunto = (data.get("asunto") or "").strip()
    texto_extraido = (data.get("texto_extraido") or "").strip()
    usuario = (data.get("usuario") or "Sistema").strip()

    # R3: validar canal de ingreso.
    if not validar_canal(canal_ingreso):
        return jsonify({
            "error": "Canal de ingreso no válido.",
            "canales_validos": sorted(CANALES_VALIDOS),
        }), 400

    # R1: generar radicado único y consecutivo ADEP-AAAA-XXXX.
    radicado = generar_radicado()

    # Llamar al agente de IA (misma lógica de POST /agente/analizar).
    datos_insumos = leer_insumos(RUTA_INSUMOS)
    agente = analizar_documento(
        texto_extraido=texto_extraido,
        canal_ingreso=canal_ingreso,
        fecha_ingreso=fecha_ingreso,
        hora_ingreso=hora_ingreso,
        directorio_areas=datos_insumos["directorio_areas"],
        tipologia_documental=datos_insumos["tipologia_documental"],
    )

    ia_disponible = "error" not in agente
    if ia_disponible:
        tipo_documento = agente.get("tipo_documento") or "Otro"
        prioridad = agente.get("prioridad") or "Media"
        area_asignada = agente.get("area_asignada") or ""
        responsable_sugerido = agente.get("responsable_sugerido") or ""
        fecha_limite = agente.get("fecha_limite_respuesta") or ""
        observaciones = agente.get("observaciones") or ""
    else:
        tipo_documento = "Otro"
        prioridad = "Media"
        area_asignada = "Unidad Secretarial y Recepción"
        responsable_sugerido = "Unidad Secretarial"
        fecha_limite = ""
        observaciones = f"IA no disponible: {agente.get('error', '')}. Revisión manual sugerida."

    # R5: prioridad forzada para asuntos legales / plazos judiciales (prioridad sobre la IA).
    legal = forzar_prioridad_legal(tipo_documento, asunto)
    forzada = False
    if legal["forzada"]:
        prioridad = legal["prioridad"]
        area_asignada = legal["area"]
        forzada = True
        observaciones = (
            (observaciones + " | ") if observaciones else ""
        ) + "Regla R5 aplicada: prioridad Urgente y área Asesoría Legal y Jurídica."

    # Validar prioridad (R4).
    if not validar_prioridad(prioridad):
        prioridad = "Media"
    fecha_limite = fecha_limite or _calcular_fecha_limite(fecha_ingreso, prioridad)

    # Estado inicial: Recibido (R2).
    estado_actual = "Recibido"

    documento = {
        "radicado": radicado,
        "fecha_ingreso": fecha_ingreso,
        "hora_ingreso": hora_ingreso,
        "canal_ingreso": canal_ingreso,
        "remitente": remitente,
        "asunto": asunto,
        "tipo_documento": tipo_documento,
        "area_asignada": area_asignada,
        "responsable_sugerido": responsable_sugerido,
        "responsable_atencion": "",
        "prioridad": prioridad,
        "estado_actual": estado_actual,
        "fecha_limite_respuesta": fecha_limite,
        "observaciones": observaciones,
        "texto_extraido": texto_extraido,
        "ubicacion": "Recepción / Ventanilla Única",
        "historial": [],
        "fuente": "registro",
        "ia_forzada": forzada,
        "ia_disponible": ia_disponible,
    }

    # R6: constancia de recepción (fecha, hora, usuario ejecutor).
    movimiento = registrar_movimiento(
        documento_id=radicado,
        accion="Recepción",
        usuario=usuario,
        fecha=fecha_ingreso,
        hora=hora_ingreso,
    )
    documento["historial"].append(movimiento)

    DOCUMENTOS[radicado] = documento
    _guardar_documentos()

    return jsonify({
        "mensaje": "Documento registrado correctamente.",
        "radicado": radicado,
        "estado_actual": estado_actual,
        "prioridad": prioridad,
        "area_asignada": area_asignada,
        "responsable_sugerido": responsable_sugerido,
        "fecha_limite_respuesta": fecha_limite,
        "ia_forzada": forzada,
        "ia_disponible": ia_disponible,
        "detalle_url": f"/detalle/{radicado}",
        "documento": documento,
    }), 201


@main_bp.route("/resultados")
def resultados():
    """Pantalla de resultados con contadores y tabla de registros."""
    docs = sorted(DOCUMENTOS.values(), key=lambda d: d.get("radicado", ""), reverse=True)
    contadores = {
        "total": len(docs),
        "pendientes": sum(1 for d in docs if d["estado_actual"] == "Pendiente de Confirmación"),
        "en_tramite": sum(1 for d in docs if d["estado_actual"] == "En Tramite"),
        "cerrados": sum(1 for d in docs if d["estado_actual"] == "Cerrado"),
        "recibidos": sum(1 for d in docs if d["estado_actual"] == "Recibido"),
        "asignados": sum(1 for d in docs if d["estado_actual"] == "Asignado"),
    }
    return render_template("resultados.html", docs=docs, contadores=contadores)


@main_bp.route("/detalle/<radicado>")
def detalle_registro(radicado):
    """Detalle de un documento con historial de trazabilidad."""
    documento = DOCUMENTOS.get(radicado)
    if not documento:
        return jsonify({"error": f"Documento {radicado} no encontrado."}), 404
    historial = obtener_historial(radicado)
    vencido = False
    try:
        if documento["fecha_limite_respuesta"]:
            fecha_limite = datetime.strptime(documento["fecha_limite_respuesta"], "%Y-%m-%d").date()
            if fecha_limite < date.today() and documento["estado_actual"] != "Cerrado":
                vencido = True
    except (ValueError, TypeError):
        pass
    return render_template("detalle.html", documento=documento, historial=historial, vencido=vencido)


@main_bp.route("/descargar/<radicado>")
def descargar_registro(radicado):
    """Descarga la constancia de recepción del documento."""
    documento = DOCUMENTOS.get(radicado)
    if not documento:
        return jsonify({"error": f"Documento {radicado} no encontrado."}), 404
    lineas = [
        "SIGECI — Constancia de Recepción",
        "Sistema Inteligente de Gestión de Correspondencia Institucional (ADEP)",
        "",
        f"Radicado: {documento['radicado']}",
        f"Fecha de ingreso: {documento['fecha_ingreso']} {documento['hora_ingreso']}",
        f"Canal de ingreso: {documento['canal_ingreso']}",
        f"Remitente: {documento['remitente']}",
        f"Asunto: {documento['asunto']}",
        f"Tipo de documento: {documento['tipo_documento']}",
        f"Prioridad: {documento['prioridad']}",
        f"Área asignada: {documento['area_asignada']}",
        f"Responsable sugerido: {documento['responsable_sugerido']}",
        f"Fecha límite de respuesta: {documento['fecha_limite_respuesta']}",
        f"Estado actual: {documento['estado_actual']}",
        f"Ubicación física: {documento['ubicacion']}",
        "",
        "Historial de trazabilidad (fecha, hora, acción, usuario):",
    ]
    for m in obtener_historial(radicado):
        lineas.append(
            f"- {m.get('fecha','')} {m.get('hora','')} | {m.get('accion','')} | {m.get('usuario','')}"
        )
    lineas.append("")
    lineas.append(
        "Esta constancia certifica la recepción del documento de acuerdo con las reglas de negocio de SIGECI."
    )
    contenido = "\n".join(lineas)
    respuesta = make_response(contenido)
    respuesta.headers["Content-Disposition"] = f'attachment; filename="constancia_{radicado}.txt"'
    respuesta.headers["Content-Type"] = "text/plain; charset=utf-8"
    return respuesta
