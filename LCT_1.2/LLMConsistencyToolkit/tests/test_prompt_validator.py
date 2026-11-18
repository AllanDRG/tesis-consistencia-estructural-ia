from src.validation.prompt_validator import PromptValidator


validator = PromptValidator()

prompt_a = "Explique el concepto de latencia en redes."

prompt_b = (
    "Explique cómo reducir la latencia de una red."
)

resultado = validator.validate(prompt_a, prompt_b)

print("\n=== LCT PROMPT VALIDATOR v0.1 ===\n")

print("Entrada A:")
print(prompt_a)

print("\nEntrada B:")
print(prompt_b)

print("\n--- RESULTADOS ---")

print(
    "Equivalencia semántica:",
    resultado.equivalencia_semantica,
    "/ 4"
)

print(
    "Equivalencia de objetivo:",
    resultado.equivalencia_objetivo,
    "/ 4"
)

print(
    "Equivalencia cognitiva:",
    resultado.equivalencia_cognitiva,
    "/ 4"
)

print(
    "Equivalencia de alcance:",
    resultado.equivalencia_alcance,
    "/ 4"
)

print(
    "Neutralidad de reformulación:",
    resultado.neutralidad_reformulacion,
    "/ 4"
)

print("\nPuntaje:", resultado.puntaje_total, "/ 20")
print("IEE:", resultado.iee, "/ 100")

print("\nRevisión humana:", resultado.revision_humana)

print("\nJustificación:")
print(resultado.justificacion)