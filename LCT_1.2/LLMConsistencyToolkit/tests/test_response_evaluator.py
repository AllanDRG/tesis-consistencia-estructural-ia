from src.validation.response_evaluator import ResponseEvaluator


evaluator = ResponseEvaluator()

entrada_a = "Explique qué es la latencia en redes."

respuesta_a = """
La latencia es el tiempo que tarda un paquete de datos
en desplazarse desde un punto de origen hasta un destino
dentro de una red.

Puede estar influenciada por la distancia, el procesamiento
de los dispositivos y la congestión de la red.

Por ejemplo, una conexión con alta latencia puede provocar
un retraso perceptible durante una videollamada.
"""


entrada_b = "Describa qué se entiende por latencia en redes."

respuesta_b = """
La latencia es el retraso existente en una comunicación
de red.
"""


resultado = evaluator.compare(
    entrada_a,
    respuesta_a,
    entrada_b,
    respuesta_b
)


print("\n=== RESPONSE EVALUATOR v0.1 ===")

print("\nRESPUESTA A")
print("Definición:", resultado.respuesta_a.definicion_conceptual)
print("Causalidad:", resultado.respuesta_a.relacion_causal)
print("Ejemplificación:", resultado.respuesta_a.ejemplificacion)
print("Aplicación:", resultado.respuesta_a.aplicacion)
print("TOTAL:", resultado.respuesta_a.total, "/ 16")
print("IPE:", resultado.respuesta_a.ipe)

print("\nRESPUESTA B")
print("Definición:", resultado.respuesta_b.definicion_conceptual)
print("Causalidad:", resultado.respuesta_b.relacion_causal)
print("Ejemplificación:", resultado.respuesta_b.ejemplificacion)
print("Aplicación:", resultado.respuesta_b.aplicacion)
print("TOTAL:", resultado.respuesta_b.total, "/ 16")
print("IPE:", resultado.respuesta_b.ipe)

print("\nCOMPARACIÓN")
print("ΔIPE:", resultado.delta_ipe)
print("Diferencia absoluta:", resultado.diferencia_absoluta)