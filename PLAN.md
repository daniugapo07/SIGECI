# PLAN.md

## 1. RESUMEN

Vamos a construir SIGECI, una plataforma web para centralizar, registrar, clasificar, distribuir y dar seguimiento a la correspondencia física y digital de ADEP. Entra como datos de entrada el archivo `insumos/Insumos_ADEP_Gestion_Correspondencia.xlsx` con sus 4 hojas (Directorio_Áreas, Canales_y_Tipología, Registro_Correspondencia, Contexto_IA_y_Matriz). El agente de IA (Gemini) lee documentos mediante OCR, clasifica tipos documentales, sugiere prioridad y area responsable, y entrega su respuesta en contrato JSON. Sale como resultado una app Flask con pantallas de inicio y resultados, contadores, tabla con filtro, historial de trazabilidad, constancias de recepción y alertas por vencimiento de SLA.

## 2. LO QUE ENCONTRÉ

### Carpeta contexto/
- `ASISTENTES.docx` — origen del contexto (ya cerrado en Word).
- `Contexto_Mi_App.md` — extraído del docx: nombre del proyecto SIGECI, problema, solución, agentes de IA (lector, clasificador, enrutador, priorizador, seguimiento, analista), funcionalidades principales, objetivos, stack tecnológico propuesto, ejemplo de trazabilidad.

### Carpeta insumos/
- `Insumos_ADEP_Gestion_Correspondencia.xlsx` — Excel con 4 hojas:
  - `Directorio_Áreas`: 15 filas × 9 columnas, 10 registros (DIR-001 a DIR-010).
  - `Canales_y_Tipología`: 21 filas × 7 columnas, 3 canales (CAN-01, CAN-02, CAN-03) y 8 tipos documentales (TD-001 a TD-008).
  - `Registro_Correspondencia`: 15 filas × 14 columnas, 10 registros simulados (ADEP-2026-0001 a ADEP-2026-00010).
  - `Contexto_IA_y_Matriz`: 20 filas × 7 columnas, matriz de flujo (5 etapas) y prompt base para IA.

### ¿Coincide con AGENTS.md?
Sí. AGENTS.md ya documenta los 4 insumos, sus columnas, las reglas de negocio (R1 a R6), el contrato JSON del agente, las cifras de control (10 áreas, 3 canales, 8 tipos, 10 registros, 5 etapas) y los casos límite. Todo lo que hay en contexto e insumos está reflejado en AGENTS.md.

### Qué falta o no cuadra
No hay faltantes críticos. La app aún no existe (no hay código, ni plantillas, ni pruebas). El archivo `.env` con la llave de Gemini no existe aún y deberá crearse por el usuario.

---

## 3. ENTREGAS POR SUBAGENTE

### Entrega 1 — @backend: Estructura base MVC con uv
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 1 | @backend | Proyecto Flask base con `create_app()`, `wsgi.py`, `iniciar_app.bat`, `.env.example` y estructura de carpetas MVC (`app/`, `app/controllers/`, `app/services/`). Instalar dependencias con `uv add` (flask, python-dotenv, openpyxl). | `app/__init__.py`, `wsgi.py`, `iniciar_app.bat`, `.env.example`, `pyproject.toml` (uv) | Ninguno (primera entrega) | Ejecutar `iniciar_app.bat`, abrir el navegador en `http://localhost:5000`, ver la app arrancar sin errores. |

### Entrega 2 — @backend: Lectura de insumos y reglas de negocio R1-R2
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 2 | @backend | Servicio para leer el Excel de insumos (4 hojas) y reglas de negocio R1 (formato de radicado `ADEP-AAAA-XXXX`) y R2 (estados válidos). Una función por regla con su comentario. | `app/services/leer_insumos.py`, `app/services/reglas_negocio.py` | Estructura base de Entrega 1 | Ejecutar la app y ver en consola/pantalla que lee las 4 hojas y devuelve: 10 áreas, 3 canales, 8 tipos, 10 registros. |

### Entrega 3 — @backend: Reglas de negocio R3-R4
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 3 | @backend | Reglas R3 (canales válidos y SLA de recepción por canal) y R4 (SLA de respuesta por prioridad). Una función por regla con su comentario. | `app/services/reglas_negocio.py` (modificar) | Estructura + lectura de insumos (Entrega 2) | Ver en pantalla que los SLAs se muestran correctamente: 2 hrs WhatsApp, 4 hrs Correo, 1 hr Física; 1 día Urgente, 2 días Alta, 3 días Media, 5 días Baja. |

### Entrega 4 — @backend: Regla de negocio R5 y R6
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 4 | @backend | Reglas R5 (prioridad forzada Urgente + Asesoría Legal para asuntos judiciales) y R6 (autorización: solo personal autorizado valida, la IA solo sugiere, constancia de recepción con fecha/hora/usuario). | `app/services/reglas_negocio.py` (modificar) | Reglas R1-R4 (Entrega 3) | Ver en pantalla que un documento con "plazo judicial" se marca como Urgente y se enruta a Asesoría Legal y Jurídica. |

### Entrega 5 — @backend: Integración del agente de IA con contrato JSON y llave en .env
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 5 | @backend | Servicio de integración con Gemini: lee la llave de `.env`, envía entrada JSON (texto extraído, canal, fecha, hora, directorio de áreas, tipología) y recibe salida JSON (radicado, tipo, prioridad, área, responsable, fecha límite, observaciones). La IA solo sugiere, nunca asigna definitivamente. | `app/services/agente_ia.py`, `.env` (creado por el usuario con su llave) | Reglas R1-R6 (Entrega 4) | Ver en pantalla una respuesta JSON válida del agente con los campos del contrato: radicado, tipo_documento, prioridad, area_asignada, responsable_sugerido, fecha_limite_respuesta, observaciones. |

### Entrega 6 — @backend: Controladores y rutas de la app
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 6 | @backend | Controladores para las rutas: inicio, registro de correspondencia, resultados con contadores, detalle por registro, y descarga de resultados. | `app/controllers/main.py` (o similar), `app/__init__.py` (registrar blueprints) | Agente de IA integrado (Entrega 5) | Navegar por las rutas de la app y ver que cada una responde sin error 404/500. |

### Entrega 7 — @frontend: Pantalla de inicio y estilo de la app
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 7 | @frontend | Plantilla `base.html` con CSS embebido (estilo profesional en español), pantalla `inicio.html` con formulario de registro de correspondencia. Sin librerías JS externas. | `app/templates/base.html`, `app/templates/inicio.html`, `app/static/` (si aplica) | Rutas del backend (Entrega 6) | Abrir `http://localhost:5000` y ver la pantalla de inicio con formulario funcional en español. |

### Entrega 8 — @frontend: Pantalla de resultados con contadores y tabla
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 8 | @frontend | Pantalla `resultados.html` con tablero de contadores grandes (total documentos, pendientes, en trámite, cerrados) y tabla con filtro por columnas. | `app/templates/resultados.html` | Pantalla de inicio (Entrega 7) | Ver en pantalla los contadores y una tabla con los 10 registros de insumos, con filtro funcional. |

### Entrega 9 — @frontend: Detalle por registro
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 9 | @frontend | Pantalla de detalle por registro individual (ficha digital de radicado) con historial de trazabilidad, constancia de recepción y ubicación física. | `app/templates/detalle.html` (o dentro de resultados) | Pantalla de resultados (Entrega 8) | Hacer clic en un registro de la tabla y ver su detalle completo con trazabilidad. |

### Entrega 10 — @tester: Pruebas en tests/ contra cifras de control y casos límite
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 10 | @tester | Pruebas con pytest en `tests/` que validen: 10 áreas, 3 canales, 8 tipos, 10 registros, 5 etapas, SLAs, estados válidos, formato de radicado, y los 7 casos límite de AGENTS.md. Configurar pythonpath. | `tests/test_*.py`, `pytest.ini` o `conftest.py` | App completa (Entregas 1-9) | Ejecutar `pytest` y ver en pantalla cuántas pruebas pasan y cuántas fallan, con causa probable de cada fallo. |

### Entrega 11 — @tester: VALIDACION.md
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 11 | @tester | Archivo `VALIDACION.md` con una tabla de esperado vs obtenido para cada cifra de control y cada caso límite. | `VALIDACION.md` | Pruebas ejecutadas (Entrega 10) | Abrir `VALIDACION.md` y revisar que cada fila tenga su estado (PASA/FALLA) y causa probable. |

### Entrega 12 — @revisor: Revisión de seguridad y cumplimiento de AGENTS.md
| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 12 | @revisor | Lista de hallazgos con prioridad (Alta/Media/Baja), archivo/línea, descripción y corrección propuesta. Revisar llaves en código, `.env` expuesto, `.gitignore`, datos sensibles, y que no haya columnas/reglas fuera de AGENTS.md. | Ninguno (solo lee y reporta) | App completa + pruebas + VALIDACION.md | Leer el reporte de hallazgos mostrado en pantalla por el revisor. |

---

## 4. PUNTOS DE CONTROL

| Punto de control | Después de qué entrega | Qué debe ver el usuario en pantalla |
|------------------|------------------------|-------------------------------------|
| PC1 | Entrega 1 (@backend) | App Flask arranca en `http://localhost:5000` sin errores al ejecutar `iniciar_app.bat`. |
| PC2 | Entrega 2 (@backend) | Consola/pantalla muestra que se leen las 4 hojas del Excel: 10 áreas, 3 canales, 8 tipos documentales, 10 registros simulados. |
| PC3 | Entrega 4 (@backend) | Un documento con "plazo judicial" o "notificación judicial" se marca como prioridad **Urgente** y se asigna a **Asesoría Legal y Jurídica**. |
| PC4 | Entrega 5 (@backend) | Respuesta JSON válida del agente con todos los campos del contrato: `radicado`, `tipo_documento`, `prioridad`, `area_asignada`, `responsable_sugerido`, `fecha_limite_respuesta`, `observaciones`. |
| PC5 | Entrega 8 (@frontend) | Tablero con contadores grandes (total, pendientes, en trámite, cerrados) y tabla con filtro que muestra los 10 registros de insumos. |
| PC6 | Entrega 10 (@tester) | Ejecutar `pytest`: se ven los resultados de prueba (pasadas/falladas) con causa probable de cada fallo. |
| PC7 | Entrega 11 (@tester) | `VALIDACION.md` muestra tabla esperado vs obtenido con estado PASA/FALLA para cada cifra de control y caso límite. |
| PC8 | Entrega 12 (@revisor) | Reporte de hallazgos con prioridad y corrección propuesta; sin llaves expuestas en código ni `.env` subido a GitHub. |

---

## 5. RIESGOS

| Riesgo | Qué hará cada subagente si pasa |
|--------|---------------------------------|
| Datos incompletos en insumos | @backend pregunta al usuario antes de continuar; no inventa columnas ni valores. @revisor lo reporta como hallazgo. |
| Archivos escaneados sin texto legible (OCR fallido) | @backend implementa manejo de error: marca el documento para revisión y digitación manual (caso límite de AGENTS.md). @frontend muestra aviso en pantalla. |
| Respuesta del agente que no es JSON válido | @backend valida la respuesta del agente; si no es JSON, rechaza y pide revisión manual. @tester escribe una prueba para este caso. |
| Límite de la llave gratis de Gemini | @backend lee la llave de `.env` y maneja error de cuota/rate limit con mensaje claro. @revisor verifica que la llave no esté escrita en el código. |
| Radicado duplicado | @backend rechaza el duplicado y genera uno nuevo consecutivo (regla de negocio en AGENTS.md). @tester valida este caso límite. |
| Área destino inexistente en el Directorio | @backend no puede asignar; notifica a Administración. @frontend muestra aviso en pantalla. |

---

## 6. PREGUNTAS PARA MÍ

Antes de empezar a construir, necesito que confirme:

1. **Llave de Gemini**: ¿usted creará el archivo `.env` con su llave de API de Gemini, o quiere que el plan contemple una variable de entorno simulada para pruebas sin llave real?
2. **Base de datos**: ¿usa un archivo local (ej. SQLite o JSON/Excel como almacenamiento temporal) o prefiere PostgreSQL como sugiere el contexto original? AGENTS.md menciona PostgreSQL pero los insumos son Excel simulados.
3. **Autenticación de usuarios**: ¿quiere que el módulo de Administración (usuarios, permisos) se incluya en esta primera versión o se deja para una fase posterior?
4. **¿Aproba este PLAN.md?** Si hay algún ajuste en las entregas, dígame antes de que los subagentes empiecen a trabajar.

---

**Siguiente paso:** Quedo a la espera de su aprobación de la tabla de entregas y de sus respuestas a las preguntas de la sección 6 antes de que los subagentes comiencen a construir.
