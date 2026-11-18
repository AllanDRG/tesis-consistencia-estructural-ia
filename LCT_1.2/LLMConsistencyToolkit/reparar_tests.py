from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TESTS = ROOT / "tests"

ARCHIVOS = [
    "test_lmstudio.py",
    "test_prompt_validator.py",
    "test_response_evaluator.py",
]

print("\n=== LCT - Reparación de estructura ===\n")

TESTS.mkdir(exist_ok=True)

# Buscar los archivos en cualquier subcarpeta del proyecto.
for nombre in ARCHIVOS:
    encontrados = [
        p for p in ROOT.rglob(nombre)
        if p.parent != TESTS
    ]

    destino = TESTS / nombre

    if destino.exists():
        print(f"[OK] {nombre} ya está correctamente ubicado.")
        continue

    if encontrados:
        origen = encontrados[0]

        print(f"[MOVIENDO] {origen}")
        print(f"        -> {destino}")

        shutil.move(str(origen), str(destino))
    else:
        print(f"[AVISO] No se encontró {nombre}")

# Crear __init__.py para que tests sea un paquete Python.
init_file = TESTS / "__init__.py"

if not init_file.exists():
    init_file.touch()
    print("[CREADO] tests/__init__.py")
else:
    print("[OK] tests/__init__.py")

# Eliminar carpetas tests vacías anidadas.
for carpeta in sorted(
    ROOT.rglob("tests"),
    key=lambda p: len(p.parts),
    reverse=True
):
    if carpeta == TESTS:
        continue

    try:
        # Ignorar __pycache__ al comprobar contenido útil.
        contenido = [
            p for p in carpeta.iterdir()
            if p.name != "__pycache__"
        ]

        if not contenido:
            shutil.rmtree(carpeta)
            print(f"[ELIMINADA] Carpeta duplicada: {carpeta}")

    except OSError:
        pass

print("\nEstructura esperada:\n")

for archivo in ARCHIVOS:
    estado = "OK" if (TESTS / archivo).exists() else "FALTA"
    print(f"[{estado}] tests/{archivo}")

print("\n=== Reparación terminada ===")