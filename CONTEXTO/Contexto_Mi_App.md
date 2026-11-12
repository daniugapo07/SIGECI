# Contexto Mi App
Extraído automáticamente de `contexto/ASISTENTES.docx`.
1. Nombre propuesto para el proyecto
SIGECI
Sistema Inteligente de Gestión de Correspondencia Institucional
Una plataforma web para centralizar, registrar, clasificar, distribuir y dar seguimiento a la correspondencia física y digital de ADEP.
2. Planteamiento del problema
Te propongo redactarlo de esta manera para presentarlo en el curso:
Problema identificado:
En la Asociación de Educadores Pensionados (ADEP), la recepción y gestión de correspondencia institucional representa un desafío administrativo debido a la inexistencia de un mecanismo único y estandarizado para centralizar el ingreso de documentos físicos y digitales.
Actualmente, la correspondencia puede ingresar por diferentes medios y ser recibida por distintas personas o áreas de la organización, sin que necesariamente exista un registro centralizado que permita conocer su ingreso, ubicación, responsable de atención y estado de trámite. Esta situación puede ocasionar que algunos documentos permanezcan en diferentes espacios de las instalaciones, que su distribución no se realice oportunamente o que existan duplicidades y confusiones respecto a las responsabilidades de recepción y traslado.
Asimismo, la falta de delimitación de un procedimiento institucional uniforme puede generar dificultades de coordinación entre colaboradores, problemas internos relacionados con la asignación de responsabilidades y riesgos de pérdida de información o retrasos en la atención de asuntos importantes.
Por tanto, se identifica la necesidad de desarrollar una solución tecnológica que permita centralizar el registro y control de la correspondencia institucional, establecer rutas claras de distribución y garantizar la trazabilidad de cada documento desde su recepción hasta su atención y cierre.
3. ¿Cómo resolvería SIGECI el problema?
La propuesta consiste en que toda correspondencia, independientemente de su canal de ingreso, pueda incorporarse a un mismo sistema.
Ingreso de correspondencia
Física
Cartas, oficios, documentos entregados en las instalaciones.
Digital
WhatsApp, Correos electrónicos, archivos PDF y documentos digitales.
Registro centralizado SIGECI
Cada documento recibe un número consecutivo, fecha, hora y canal de recepción.
Procesamiento mediante agentes de IA
Lectura, clasificación, identificación del destinatario y sugerencia de prioridad.
Distribución institucional
Asignación según reglas, áreas y responsables previamente autorizados.
Seguimiento y cierre
Registro de movimientos, responsables, fechas, respuestas y estado final.
Un ejemplo práctico:
Llega un oficio físico dirigido a la Junta Directiva Central.
La persona autorizada lo recibe y lo registra en SIGECI.
Escanea el documento y lo adjunta al expediente digital.
La IA identifica que es un oficio relacionado con un asunto de Junta Directiva.
El sistema propone el área responsable según las reglas institucionales.
La persona encargada de correspondencia valida la asignación.
El responsable recibe una notificación y confirma su recepción.
El sistema registra los movimientos y permite conocer si el documento está pendiente, en trámite o atendido.
Así, aunque el documento físico se encuentre en otra oficina, su registro digital permite conocer quién tiene la responsabilidad de atenderlo y dónde se encuentra registrado.
4. Los agentes de IA que utilizaría
Aquí es donde tu proyecto se vuelve interesante técnicamente.

## Tabla
| Agente | Función || --- | --- || 1. Lector documental | Lee PDF, imágenes escaneadas y documentos digitales mediante OCR y extracción de texto. || 2. Clasificador | Identifica si es oficio, solicitud, invitación, circular, factura, comunicación u otro tipo documental. || 3. Enrutador inteligente | Sugiere el área y responsable según el contenido y las reglas institucionales. || 4. Priorizador | Detecta fechas límite, urgencias y asuntos que requieren atención especial. || 5. Seguimiento | Identifica documentos pendientes, atrasados y sin confirmación de recepción. || 6. Analista de gestión | Genera reportes de volumen, tiempos de atención, documentos pendientes y movimientos. |
Una precisión importante: el sistema no debe permitir que la IA distribuya documentos libremente ni que cualquier colaborador se atribuya la recepción oficial. El ingreso, la validación y las asignaciones deben estar sujetos a permisos y reglas institucionales.
5. Funcionalidades principales de la aplicación web
Para que el proyecto sea viable durante el curso, propongo comenzar con estos módulos:

## Tabla
| Módulo | Funcionalidad || --- | --- || Bandeja de entrada | Registrar correspondencia física y digital. || Registro documental | Asignar consecutivo, fecha, remitente y tipo de documento. || Clasificación IA | Identificar contenido, categoría y prioridad sugerida. || Distribución | Asignar área y responsable según un directorio autorizado. || Seguimiento | Consultar quién tiene el documento y su estado. || Alertas | Notificar documentos pendientes y vencimientos. || Reportes | Consultar estadísticas y tiempos de atención. || Administración | Gestionar usuarios, permisos y reglas de distribución. |
Una función que considero indispensable es la constancia de recepción: cada vez que alguien recibe o traslada un documento, debe quedar registrado el movimiento con fecha, hora y usuario.
También incorporaría un registro de ubicación física: por ejemplo, recibido en recepción, trasladado a Secretaría, entregado a Dirección Administrativa o enviado a otra área.
6. Objetivo general del proyecto
Desarrollar una aplicación web inteligente, mediante la integración de agentes de inteligencia artificial y APIs, que permita centralizar y optimizar la recepción, clasificación, distribución y seguimiento de la correspondencia física y digital de ADEP, fortaleciendo la trazabilidad documental, la delimitación de responsabilidades y la eficiencia de los procesos administrativos.
Objetivos específicos:
Centralizar el registro de la correspondencia institucional, independientemente de su medio de recepción.
Implementar agentes de IA que permitan leer, clasificar y analizar documentos.
Establecer mecanismos de asignación y distribución basados en reglas y responsables autorizados.
Implementar un sistema de seguimiento que permita conocer el estado, ubicación y responsable de cada documento.
Generar reportes que faciliten el control administrativo y la toma de decisiones.
7. ¿Con qué tecnología podrías construirlo?

## Tabla
| Componente | Tecnología propuesta || --- | --- || Desarrollo asistido | OpenCode || Interfaz web | React || Backend | Python + FastAPI || Agentes | API de OpenAI || Lectura de documentos | OCR + extracción de PDF || Base de datos | PostgreSQL || Gestión de archivos | Almacenamiento documental || Notificaciones | Correo electrónico mediante API |
Para el prototipo puedes simular el correo de entrada y utilizar documentos de prueba. No necesitas conectarte directamente a los sistemas internos de ADEP ni utilizar correspondencia confidencial.
8. Un elemento que haría destacar tu proyecto
Yo agregaría una funcionalidad denominada Historial de trazabilidad documental.
Ejemplo de expediente de correspondencia
Documento: OF-2026-00125
En trámite
Asunto: Solicitud de información institucional
Recepción del documento
4 de noviembre, 8:15 a. m.
Recibido físicamente y registrado en el sistema.
Clasificación mediante IA
4 de noviembre, 8:17 a. m.
Clasificado como oficio. Destinatario sugerido: área correspondiente.
Validación y asignación
4 de noviembre, 9:00 a. m.
Asignado por usuario autorizado.
Confirmación de recepción
Pendiente
El responsable aún no confirma la recepción.
Responsable actual
Área asignada
Ubicación física
Pendiente de confirmar
Esto permitiría responder una pregunta que actualmente puede resultar difícil de contestar:
¿Dónde está la correspondencia, quién la tiene bajo su responsabilidad y qué ha sucedido con ella desde que ingresó a la institución?
