import json
from dataclasses import dataclass
from src.llm.local_llm import LocalLLM


@dataclass
class ValidationResult:
    equivalencia_semantica: int
    equivalencia_objetivo: int
    equivalencia_cognitiva: int
    equivalencia_alcance: int
    neutralidad_reformulacion: int
    justificacion: str

    @property
    def dimensiones(self) -> list[int]:
        return [
            self.equivalencia_semantica,
            self.equivalencia_objetivo,
            self.equivalencia_cognitiva,
            self.equivalencia_alcance,
            self.neutralidad_reformulacion,
        ]

    @property
    def puntaje_total(self) -> int:
        return sum(self.dimensiones)

    @property
    def iee(self) -> float:
        return (self.puntaje_total / 20) * 100

    @property
    def minimo_dimensional(self) -> int:
        return min(self.dimensiones)

    @property
    def admisible(self) -> bool:
        return self.iee >= 90 and self.minimo_dimensional >= 3

    @property
    def estado_admision(self) -> str:
        return "ADMISIBLE" if self.admisible else "REQUIERE REVISION"

    @property
    def motivo_admision(self) -> str:
        if self.admisible:
            return "IEE >= 90 y todas las dimensiones >= 3/4."

        motivos = []
        if self.iee < 90:
            motivos.append(f"IEE {self.iee:.2f} < 90")
        if self.minimo_dimensional < 3:
            motivos.append(
                f"al menos una dimension es {self.minimo_dimensional}/4 (< 3/4)"
            )
        return "; ".join(motivos) + "."


class PromptValidator:

    def __init__(self):
        self.llm = LocalLLM()

    def validate(self, prompt_a: str, prompt_b: str) -> ValidationResult:

        instruction = f"""
Analiza el siguiente par de entradas academicas.

ENTRADA A:
{prompt_a}

ENTRADA B:
{prompt_b}

Evalua cada dimension utilizando unicamente numeros enteros de 0 a 4:

- equivalencia_semantica:
  0 = significado diferente
  4 = mismo significado conceptual

- equivalencia_objetivo:
  0 = solicitan tareas diferentes
  4 = solicitan exactamente el mismo objetivo

- equivalencia_cognitiva:
  0 = requieren niveles cognitivos diferentes
  4 = requieren el mismo nivel cognitivo

- equivalencia_alcance:
  0 = alcance claramente diferente
  4 = mismo alcance conceptual

- neutralidad_reformulacion:
  0 = la reformulacion introduce informacion que puede alterar la respuesta
  4 = unicamente cambia la formulacion linguistica

La evaluacion es auxiliar y NO constituye validacion cientifica.
No decidas si el par es admisible ni si requiere revision humana. Esa decision
se calcula de forma determinista y se confirma posteriormente por el investigador.

Devuelve EXCLUSIVAMENTE JSON valido con esta estructura:

{{
  "equivalencia_semantica": 0,
  "equivalencia_objetivo": 0,
  "equivalencia_cognitiva": 0,
  "equivalencia_alcance": 0,
  "neutralidad_reformulacion": 0,
  "justificacion": "explicacion breve"
}}
"""

        raw = self.llm.chat(instruction)
        raw = raw.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)

        campos = [
            "equivalencia_semantica",
            "equivalencia_objetivo",
            "equivalencia_cognitiva",
            "equivalencia_alcance",
            "neutralidad_reformulacion",
        ]

        for campo in campos:
            valor = data[campo]
            if not isinstance(valor, int) or not 0 <= valor <= 4:
                raise ValueError(f"{campo} debe ser un entero entre 0 y 4.")

        data["justificacion"] = str(data["justificacion"])
        return ValidationResult(**data)
