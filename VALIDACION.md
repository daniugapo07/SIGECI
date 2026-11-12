# VALIDACIÓN — SIGECI (Entrega 11)

Informe de validación del proyecto **SIGECI** contra las cifras de control y los casos límite definidos en `AGENTS.md`, a partir de los resultados reales de las pruebas de la **Entrega 10** (`pytest`).

Resultado global de las pruebas: **35 pruebas ejecutadas, 34 pasadas, 1 fallada.**

Archivos de prueba utilizados:
- `tests/test_cifras_control.py`
- `tests/test_reglas_negocio.py`
- `tests/test_casos_limite.py`

---

## 1. Cifras de control (Esperado vs Obtenido)

| # | Cifra de control | Esperado | Obtenido | Estado | Causa probable |
|---|------------------|----------|----------|--------|----------------|
| 1 | Áreas en `Directorio_Áreas` | 10 áreas (DIR-001 a DIR-010) | 10 áreas (DIR-001 a DIR-010) | PASA | — |
| 2 | Canales de ingreso válidos | 3 canales (CAN-01, CAN-02, CAN-03) | 3 canales (CAN-01, CAN-02, CAN-03) | PASA | — |
| 3 | Tipos documentales catalogados | 8 tipos (TD-001 a TD-008) | 8 tipos (TD-001 a TD-008) | PASA | — |
| 4 | Registros simulados en `Registro_Correspondencia` | 10 registros | 10 registros | PASA | — |
| 5 | Etapas del flujo de trabajo | 5 etapas | 5 etapas | PASA | — |
| 6 | SLA de recepción por canal | WhatsApp 2 hrs, Correo 4 hrs, Física 1 hr | Coincide con lo esperado | PASA | — |
| 7 | SLA de respuesta por prioridad | Urgente 1 día, Alta 2 días, Media 3 días, Baja 5 días | Coincide con lo esperado | PASA | — |
| 8 | Estados válidos | Recibido, Asignado, En Tramite, Cerrado, Pendiente de Confirmación | Coincide con lo esperado | PASA | — |
| 9 | Formato de radicado R1 `^ADEP-\d{4}-\d{4}$` | Todos los radicados cumplen R1 | `ADEP-2026-00010` tiene 5 dígitos al final y viola R1 | FALLA | El insumo `Registro_Correspondencia` incluye el radicado `ADEP-2026-00010` (5 dígitos en la posición final), que excede el formato R1 de 4 dígitos. No se modificó `insumos/`; se debe corregir ese radicado o generar uno nuevo consecutivo válido. |

---

## 2. Casos límite (Esperado vs Obtenido)

| # | Caso límite | Esperado (AGENTS.md) | Obtenido (pruebas Entrega 10) | Estado | Causa probable |
|---|-------------|----------------------|-------------------------------|--------|----------------|
| CL1 | Documento escaneado sin texto legible (OCR fallido) | Revisión y digitación manual; la app sugiere revisión manual en observaciones | `analizar_documento("")` devuelve error con "Gemini"; el registro se crea con observación "Revisión manual sugerida" (201) | PASA | — |
| CL2 | Prioridad conflictiva (plazo judicial / asunto legal) | Se fuerza `Urgente` y se enruta a `Asesoría Legal y Jurídica` | `forzar_prioridad_legal` y `/registrar` con asunto judicial devuelven prioridad `Urgente`, área `Asesoría Legal y Jurídica`, `ia_forzada = True` | PASA | — |
| CL3 | Remitente no identificado o canal no reconocido | Se marca para revisión manual | Canal no reconocido se rechaza (400 "Canal de ingreso no válido."); remitente vacío se acepta **sin** marcar revisión manual (comportamiento actual documentado en prueba) | FALLA (parcial) | El canal no reconocido sí se rechaza correctamente, pero el remitente no identificado no se marca para revisión manual aunque AGENTS.md lo indique. La prueba documenta este desvío del comportamiento actual. |
| CL4 | Área destino inexistente en el Directorio | No se puede asignar; se notifica a Administración | `"Área Inexistente"` no está en el Directorio (PASA), pero el controlador almacena el área sugerida aunque no exista en el Directorio (comportamiento actual documentado) | FALLA (parcial) | El controlador no valida que el área exista en el Directorio antes de asignar, cuando AGENTS.md indica que no se puede asignar y debe notificarse a Administración. |
| CL5 | Fecha límite de respuesta vencida | Alerta inmediata | Registros no cerrados con límite anterior a 2026-11-04 identificados como vencidos (`ADEP-2026-0001`, `0002`, `0004`); el detalle muestra "Alerta" y "venció" | PASA | — |
| CL6 | Radicado duplicado | Se rechaza y se genera uno nuevo consecutivo | `generar_radicado()` produce radicados válidos, no duplicados, con 4 dígitos; ante duplicado genera `ADEP-2026-0012` | PASA | — |
| CL7 | Documento sin confirmación de recepción por el responsable | Permanece como `Pendiente de Confirmación` | El estado `Pendiente de Confirmación` es válido y se mantiene en el detalle del documento | PASA | — |

**Nota importante:** los 16 tests de `tests/test_casos_limite.py` pasaron en `pytest` porque validan el comportamiento actual implementado. CL3 y CL4 se marcan como **FALLA (parcial)** porque las propias pruebas documentan un desvío respecto a lo que espera `AGENTS.md` (comparación Esperado vs Obtenido contra el documento de reglas de negocio).

---

## 3. Resumen

| Métrica | Valor |
|---------|-------|
| Pruebas totales ejecutadas | 35 |
| Pruebas pasadas | 34 |
| Pruebas falladas | 1 |
| Prueba fallada | `tests/test_cifras_control.py::test_todos_los_radicados_de_los_registros_cumplen_r1` |
| Causa de la falla | Radicado `ADEP-2026-00010` con 5 dígitos viola el formato R1 `^ADEP-\d{4}-\d{4}$` |

---

### Cómo verificarlo en pantalla

Abrir `VALIDACION.md` y revisar que cada fila de la Sección 1 y la Sección 2 tenga su columna `Estado` (`PASA` o `FALLA`) y su columna `Causa probable` completada. La Sección 3 debe mostrar 35 pruebas totales, 34 pasadas y 1 fallada.
