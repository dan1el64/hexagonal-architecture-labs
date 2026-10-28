# Explicar los laboratorios en una entrevista

## Presentación de 60 segundos

"Preparé dos ejemplos independientes en Python para mostrar puertos y adaptadores. En inventario, el caso de uso depende de un contrato de reserva atómica, no de SQLite. Puedo cambiar memoria por SQLite sin cambiar las reglas. El contrato cubre idempotencia y evita vender la misma unidad a dos solicitudes concurrentes. En evaluación, separé el proveedor de respuestas de una rúbrica determinista. Uso fixtures sintéticos para que cualquiera reproduzca los casos sin claves ni costos. No lo presento como un benchmark semántico ni como entrenamiento de un modelo."

## Demo de cinco minutos

1. Abre `labs/inventory/domain.py` y muestra que no importa infraestructura.
2. Compara `ports.py` con los dos adaptadores. Explica por qué deducción de stock y registro de solicitud pertenecen a una única operación atómica.
3. Ejecuta `python -m unittest discover -s tests -v`. Busca el caso de concurrencia y el reintento con distinto contenido.
4. Ejecuta dos veces `python -m labs.inventory.cli --adapter sqlite --request-id interview-001`. En una base nueva, el stock queda en 8 en ambas ejecuciones; el segundo intento no descuenta de nuevo.
5. Ejecuta `python -m labs.evaluation.cli`. Explica por qué un caso pasa y dos fallan intencionalmente.
6. Muestra `docs/architecture.md` y los resultados de GitHub Actions.

## Preguntas que deberías poder responder

**¿Qué hace hexagonal a este ejemplo?** La dirección de las dependencias y los contratos. El dominio no conoce los adaptadores; el punto de composición elige implementaciones. No basta con tener carpetas llamadas domain y adapters.

**¿Por qué no hacer getStock y save desde el caso de uso?** Separarlos sin una unidad transaccional permitiría que dos solicitudes leyeran la misma cantidad disponible. La operación del puerto expresa la garantía necesaria y cada adaptador debe cumplirla.

**¿Qué sucede si un cliente repite una solicitud?** La misma clave y contenido devuelve la reserva previa; la misma clave con otro contenido se rechaza. Una operación fallida no deja una reserva parcial.

**¿Es esto una plataforma de IA en producción?** No. Es un evaluador reproducible de ejemplo. La rúbrica léxica puede aceptar texto que contiene palabras correctas pero razona mal, y rechazar paráfrasis válidas. Un modelo real necesitaría trazabilidad, presupuesto, manejo de errores y revisión de la evaluación.

**¿Cómo se relaciona con Revelo y Stefanini?** Sirve para explicar criterios de evaluación, calidad e infraestructura y la separación de responsabilidades que aplicas en backend. Es código nuevo con datos sintéticos; no contiene tareas contractuales ni prueba por sí solo resultados de esas empresas.

**¿Qué harías para producción?** Añadiría autorización, migraciones y expiración de reservas al inventario; evaluaciones revisadas por humanos y aislamiento de ejecución al evaluador. Primero definiría riesgos y alcance, no agregaría servicios cloud solo por mostrar herramientas.

## Preparación personal

Practica ejecutando ambos ejemplos y explicando una prueba fallida. Cambia una regla pequeña y comprueba qué test detecta la regresión. Mantén claro qué código existía en tus proyectos, qué añadiste en este laboratorio y qué sigue siendo una propuesta.
