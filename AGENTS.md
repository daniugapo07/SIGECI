# AGENTS.md

## Qué es esta app

**SIGECI** — Sistema Inteligente de Gestión de Correspondencia Institucional.

Plataforma web para centralizar, registrar, clasificar, distribuir y dar seguimiento a la correspondencia física y digital de la Asociación de Educadores Pensionados (ADEP). Permite conocer en todo momento dónde está un documento, quién lo tiene bajo su responsabilidad y qué ha sucedido con él desde que ingresó a la institución (historial de trazabilidad documental).

## Datos de entrada

Archivo de insumos: `insumos/Insumos_ADEP_Gestion_Correspondencia.xlsx` (Excel, 4 hojas).

### Hoja 1: `Directorio_Áreas`
Dimensiones: 15 filas × 9 columnas (10 registros de áreas, filas 6–15).

Columnas:
- `ID Área`
- `Nombre del Área / Departamento`
- `Código Interno`
- `Responsable / Jefatura`
- `Puesto / Cargo`
- `Correo Electrónico`
- `Teléfono / Ext.`
- `Sede / Ubicación Física`

Registros de ejemplo (códigos de área): DIR-001, DIR-002, DIR-003, DIR-004, DIR-005, DIR-006, DIR-007, DIR-008, DIR-009, DIR-010.

### Hoja 2: `Canales_y_Tipología`
Dimensiones: 21 filas × 7 columnas.

Bloque A — Canales de ingreso (filas 6–8):
Columnas: `Código Canal`, `Nombre del Canal`, `Tipo de Medio`, `Formato Entrante`, `SLA Recepción (Horas)`, `Responsable Inicial`
- CAN-01 WhatsApp Corporativo | Digital / Móvil | Texto, Audio, PDF, Imagen | 2 hrs | Recepción / Unidad Secretarial
- CAN-02 Correo Institucional | Digital / Email | PDF, Word, Excel, EML | 4 hrs | Unidad Secretarial
- CAN-03 Recepción Física | Presencial / Físico | Papel impreso, Sobres, Oficios | 1 hr | Recepción / Ventanilla Única

Bloque B — Tipología documental (filas 13–20):
Columnas: `Código Tipo`, `Categoría / Documento`, `Nivel Prioridad Sugerido`, `Días Máximos para Respuesta (SLA)`, `Área Destino Frecuente`
- TD-001 Solicitud de Afiliación / Desafiliación | Media | 3 días hábiles | Afiliaciones y Beneficios
- TD-002 Solicitud de Incapacidad / Ayuda Económica | Alta | 2 días hábiles | Servicios al Asociado y Bienestar
- TD-003 Notificación Judicial / Recurso Legal | Urgente | 1 día hábil | Asesoría Legal y Jurídica
- TD-004 Factura de Proveedor / Cobro | Media | 5 días hábiles | Gestión Financiera y Contabilidad
- TD-005 Oficio Institucional (MEP / JUPEMA / CCSS) | Alta | 2 días hábiles | Dirección Ejecutiva
- TD-006 Consulta General / Sugerencia de Asociado | Baja | 5 días hábiles | Unidad Secretarial y Recepción
- TD-007 Invitación a Evento / Asamblea Exterior | Baja | 3 días hábiles | Junta Directiva y Presidencia
- TD-008 Cotización / Propuesta Comercial | Baja | 5 días hábiles | Proveeduría y Suministros

### Hoja 3: `Registro_Correspondencia`
Dimensiones: 15 filas × 14 columnas (10 registros simulados, filas 6–15).

Columnas:
- `N° Radicado`
- `Fecha Ingreso`
- `Hora`
- `Canal Ingreso`
- `Remitente (Nombre / Entidad)`
- `Asunto / Resumen del Documento`
- `Tipo Documento`
- `Área Asignada`
- `Responsable Atención`
- `Prioridad`
- `Estado Actual`
- `Fecha Límite Respuesta`
- `Ubicación Archivo / Link`

Ejemplo de radicados simulados: `ADEP-2026-0001` a `ADEP-2026-00010`.

### Hoja 4: `Contexto_IA_y_Matriz`
Dimensiones: 20 filas × 7 columnas.

Bloque A — Matriz de trabajo y flujo de correspondencia (5 etapas):
- 1. Captura & Extracción
- 2. Clasificación & Prioridad
- 3. Enrutamiento Automático
- 4. Gestión y Seguimiento
- 5. Cierre y Archivo

Bloque B — Prompt base sugerido para la IA: asistente virtual de la Unidad Secretarial de ADEP que analiza correspondencia de 3 canales, extrae datos clave, clasifica prioridad y determina área/responsable según el Directorio Institucional. Formato de radicado: `ADEP-AAAA-XXXX`. Prioridades: Urgente (1 día), Alta (2 días), Media (3 días), Baja (5 días).

## Reglas de negocio (código, sin IA)

Estas reglas se implementan como código de aplicación (no las decide la IA):

```python
# Formato de radicado obligatorio
RADICADO_PATTERN = r"^ADEP-\d{4}-\d{4}$"  # ADEP-AAAA-XXXX

# Estados válidos de un documento
ESTADOS_VALIDOS = {"Recibido", "Asignado", "En Tramite", "Cerrado", "Pendiente de Confirmación"}

# Canales válidos de ingreso
CANALES_VALIDOS = {"WhatsApp Corporativo", "Correo Institucional", "Recepción Física"}

# SLAs de recepción por canal (horas)
SLA_RECEPCION = {
    "WhatsApp Corporativo": 2,
    "Correo Institucional": 4,
    "Recepción Física": 1,
}

# SLAs de respuesta por prioridad (días hábiles)
SLA_RESPUESTA = {
    "Urgente": 1,
    "Alta": 2,
    "Media": 3,
    "Baja": 5,
}

# Prioridad forzada para asuntos legales / plazos judiciales
if tipo_documento in {"Notificación Judicial", "Recurso Legal"} or \
   "judicial" in asunto.lower() or "plazo" in asunto.lower():
    prioridad = "Urgente"
    area_asignada = "Asesoría Legal y Jurídica"

# Reglas de autorización
# - Solo personal autorizado (Unidad Secretarial / Recepción) valida la asignación final.
# - La IA nunca distribuye documentos libremente; solo sugiere área y responsable.
# - Cualquier movimiento (recibir, trasladar, asignar, cerrar) debe registrar:
#     fecha, hora y usuario que lo ejecuta (constancia de recepción).
# - Se lleva registro de ubicación física del documento.
```

## Lo que hace el agente de IA (con el contrato JSON)

El agente de IA (modelo Gemini) actúa como asistente virtual de la Unidad Secretarial de ADEP. Su rol es **sugerir**, nunca decidir ni distribuir definitivamente.

Entrada del agente (JSON):
```json
{
  "documento": {
    "texto_extraido": "string (resultado de OCR / extracción de PDF)",
    "canal_ingreso": "WhatsApp Corporativo | Correo Institucional | Recepción Física",
    "fecha_ingreso": "YYYY-MM-DD",
    "hora_ingreso": "HH:MM"
  },
  "directorio_areas": [
    {
      "id_area": "DIR-001",
      "nombre_area": "Junta Directiva y Presidencia",
      "codigo_interno": "SEC-JD",
      "responsable": "Dra. Carmen Rodríguez Mena",
      "puesto": "Presidenta ADEP"
    }
  ],
  "tipologia_documental": [
    {
      "codigo_tipo": "TD-001",
      "categoria": "Solicitud de Afiliación / Desafiliación",
      "prioridad_sugerida": "Media",
      "dias_maximo_respuesta": 3,
      "area_destino": "Afiliaciones y Beneficios"
    }
  ]
}
```

Salida del agente (JSON):
```json
{
  "radicado": "ADEP-2026-0001",
  "tipo_documento": "Oficio Institucional (MEP / JUPEMA / CCSS)",
  "prioridad": "Urgente | Alta | Media | Baja",
  "area_asignada": "Junta Directiva y Presidencia",
  "responsable_sugerido": "Dra. Carmen Rodríguez Mena",
  "fecha_limite_respuesta": "YYYY-MM-DD",
  "observaciones": "string"
}
```

Funciones del agente:
1. **Lector documental:** lee PDF, imágenes escaneadas y documentos digitales mediante OCR y extracción de texto.
2. **Clasificador:** identifica si es oficio, solicitud, invitación, circular, factura, comunicación u otro tipo documental.
3. **Enrutador inteligente:** sugiere el área y responsable según el contenido y las reglas institucionales.
4. **Priorizador:** detecta fechas límite, urgencias y asuntos que requieren atención especial.
5. **Seguimiento:** identifica documentos pendientes, atrasados y sin confirmación de recepción.
6. **Analista de gestión:** genera reportes de volumen, tiempos de atención, documentos pendientes y movimientos.

## Qué produce la app

- Registro centralizado de correspondencia con número de radicado único (`ADEP-AAAA-XXXX`).
- Ficha digital de registro por documento (consecutivo, fecha, remitente, tipo de documento).
- Clasificación y prioridad sugerida por la IA (validada por usuario autorizado).
- Asignación de área y responsable según el directorio autorizado.
- Constancia de recepción: cada recepción o traslado registra fecha, hora y usuario.
- Registro de ubicación física (ej. recibida en recepción, trasladada a Secretaría, entregada a Dirección, enviada a otra área).
- Historial de trazabilidad documental (movimientos, estados, responsables, fechas).
- Consultas de quién tiene el documento y su estado actual.
- Alertas por documentos pendientes y vencimientos de SLA.
- Reportes de volumen, tiempos de atención y movimientos.
- Gestión de usuarios, permisos y reglas de distribución (módulo de Administración).

## Quién decide

| Actor | Decide |
|-------|--------|
| IA (Gemini) | Sugiere clasificación, prioridad, área y responsable. Nunca asigna definitivamente ni distribuye libremente. |
| Usuario autorizado (Unidad Secretarial / Recepción) | Valida la asignación propuesta por la IA y confirma el ingreso oficial. |
| Responsable del área destino | Confirma recepción del documento y gestiona su trámite hasta el cierre. |

## Cifras de control (delimitadas por los insumos simulados)

- 10 áreas institucionales en `Directorio_Áreas`.
- 3 canales de ingreso válidos.
- 8 tipos documentales catalogados (`TD-001` a `TD-008`).
- 10 registros simulados en `Registro_Correspondencia`.
- 5 etapas del flujo de trabajo (captura, clasificación, enrutamiento, gestión, cierre).
- SLAs de recepción: 2 hrs (WhatsApp), 4 hrs (Correo), 1 hr (Recepción Física).
- SLAs de respuesta: 1 día (Urgente), 2 días (Alta), 3 días (Media), 5 días (Baja).

## Casos límite

- Documento escaneado sin texto legible (OCR fallido) → requiere revisión y digitación manual.
- Prioridad conflictiva (ej. oficio con plazo judicial) → se fuerza `Urgente` y se enruta a Asesoría Legal.
- Remitente no identificado o canal no reconocido → se marca para revisión manual.
- Área destino inexistente en el Directorio → no se puede asignar; se notifica a Administración.
- Fecha límite de respuesta ya vencida al momento del registro → alerta inmediata.
- Intento de duplicar un radicado existente → se rechaza y se genera uno nuevo consecutivo.
- Documento sin confirmación de recepción por el responsable → permanece como `Pendiente de Confirmación`.

## Reglas del sistema

- Un documento = un radicado único y consecutivo (`ADEP-AAAA-XXXX`).
- Solo personal autorizado puede validar asignaciones y cerrar documentos.
- La IA nunca asigna definitivamente; siempre es una sugerencia sujeta a validación humana.
- Todo movimiento registra fecha, hora y usuario ejecutor.
- Estados válidos: `Recibido`, `Asignado`, `En Tramite`, `Cerrado`, `Pendiente de Confirmación`.
- Canales válidos: `WhatsApp Corporativo`, `Correo Institucional`, `Recepción Física`.
- Si hay aspectos legales o plazos judiciales → prioridad `Urgente` y área `Asesoría Legal y Jurídica`.
