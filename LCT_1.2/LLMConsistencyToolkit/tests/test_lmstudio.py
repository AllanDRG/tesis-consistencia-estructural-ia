from src.llm.local_llm import LocalLLM


print("=== LLM CONSISTENCY TOOLKIT ===")
print("Probando conexión con LM Studio...\n")

llm = LocalLLM()

respuesta = llm.chat(
    "Responde únicamente: LCT conectado correctamente."
)

print("Respuesta:")
print(respuesta)