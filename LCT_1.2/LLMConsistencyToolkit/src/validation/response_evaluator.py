
import json
from dataclasses import dataclass

from src.llm.local_llm import LocalLLM


CRITERIA_KEYS = (
    "definicion_conceptual",
    "relacion_causal",
    "ejemplificacion",
    "aplicacion",
)


@dataclass
class CriterionScore:
    score: int
    justification: str


@dataclass
class ResponseScore:
    definicion_conceptual: CriterionScore
    relacion_causal: CriterionScore
    ejemplificacion: CriterionScore
    aplicacion: CriterionScore

    @property
    def total(self) -> int:
        return (
            self.definicion_conceptual.score
            + self.relacion_causal.score
            + self.ejemplificacion.score
            + self.aplicacion.score
        )

    @property
    def ipe(self) -> float:
        return (self.total / 16) * 100


@dataclass
class ComparisonResult:
    respuesta_a: ResponseScore
    respuesta_b: ResponseScore

    @property
    def delta_ipe(self) -> float:
        return self.respuesta_a.ipe - self.respuesta_b.ipe


class ResponseEvaluator:

    MAX_ATTEMPTS = 2

    def __init__(self):
        self.llm = LocalLLM()

    @staticmethod
    def _parse_evaluation(raw: str) -> ResponseScore:
        """
        Interpreta y valida la evaluación del modelo auxiliar.

        No modifica puntuaciones ni reconstruye JSON
        incorrectos mediante suposiciones.
        """

        if not isinstance(raw, str):
            raise ValueError(
                "El modelo auxiliar no devolvió texto."
            )

        cleaned = raw.strip()

        # Eliminar delimitadores Markdown si existen.
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines.pop(0)

            if lines and lines[-1].strip() == "```":
                lines.pop()

            cleaned = "\n".join(lines).strip()

        if not cleaned:
            raise ValueError(
                "El modelo auxiliar devolvió una respuesta vacía."
            )

        try:
            data = json.loads(cleaned)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "El modelo auxiliar devolvió JSON inválido. "
                f"Línea {exc.lineno}, columna {exc.colno}: "
                f"{exc.msg}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "La evaluación debe ser un objeto JSON."
            )

        criteria = {}

        for key in CRITERIA_KEYS:

            if key not in data:
                raise ValueError(
                    f"Falta la dimensión obligatoria: {key}"
                )

            item = data[key]

            if not isinstance(item, dict):
                raise ValueError(
                    f"{key}: debe contener un objeto JSON."
                )

            if "score" not in item:
                raise ValueError(
                    f"{key}: falta el campo score."
                )

            if "justification" not in item:
                raise ValueError(
                    f"{key}: falta el campo justification."
                )

            score = item["score"]
            justification = item["justification"]

            # bool es subtipo de int en Python.
            # Por eso se utiliza type(score) is int.
            if type(score) is not int or not 0 <= score <= 4:
                raise ValueError(
                    f"{key}: score debe ser un entero entre 0 y 4."
                )

            if (
                not isinstance(justification, str)
                or not justification.strip()
            ):
                raise ValueError(
                    f"{key}: justification debe ser texto no vacío."
                )

            criteria[key] = CriterionScore(
                score=score,
                justification=justification.strip()
            )

        return ResponseScore(**criteria)

    def _evaluate_single(
        self,
        entrada: str,
        respuesta: str
    ) -> ResponseScore:

        instruction = f"""
Actúa como asistente de evaluación de profundidad explicativa.

Evalúa ÚNICAMENTE la respuesta proporcionada respecto de la entrada
que la originó. Esta evaluación es independiente. No utilices ni
supongas información de evaluaciones anteriores.

ENTRADA:
{entrada}

RESPUESTA:
{respuesta}

Evalúa cuatro dimensiones utilizando números enteros de 0 a 4.

DEFINICIÓN CONCEPTUAL
0 = ausente
1 = mínima, vaga o imprecisa
2 = desarrollo básico
3 = clara, correcta y suficientemente desarrollada
4 = precisa, amplia y bien integrada

RELACIÓN CAUSAL
0 = ausente
1 = relación superficial
2 = explicación básica de relaciones
3 = relaciones causales claras y adecuadamente desarrolladas
4 = relaciones profundas, pertinentes y bien integradas

EJEMPLIFICACIÓN
0 = ausente
1 = ejemplo débil o poco pertinente
2 = ejemplo básico
3 = ejemplo claro y pertinente
4 = ejemplos altamente pertinentes e integrados en la explicación

APLICACIÓN
0 = ausente
1 = aplicación mínima
2 = aplicación básica
3 = aplicación clara y contextualizada
4 = aplicación desarrollada, pertinente y bien integrada

REGLAS:
- No premies una respuesta únicamente por ser más extensa.
- Evalúa calidad y desarrollo, no cantidad de palabras.
- No compares con otra respuesta.
- No inventes contenido que no esté presente.
- Justifica cada puntuación por separado.
- La puntuación es una sugerencia auxiliar y puede ser modificada
  posteriormente por el investigador.
- Devuelve exactamente las cuatro dimensiones solicitadas.
- Utiliza puntuaciones enteras de 0 a 4.
- No agregues comentarios fuera del JSON.
- No utilices bloques Markdown.
- Escapa correctamente las comillas dentro de las justificaciones.

Devuelve EXCLUSIVAMENTE JSON válido con esta estructura:

{{
  "definicion_conceptual": {{
    "score": 0,
    "justification": "..."
  }},
  "relacion_causal": {{
    "score": 0,
    "justification": "..."
  }},
  "ejemplificacion": {{
    "score": 0,
    "justification": "..."
  }},
  "aplicacion": {{
    "score": 0,
    "justification": "..."
  }}
}}
"""

        last_error = None

        for attempt in range(1, self.MAX_ATTEMPTS + 1):

            raw = self.llm.chat(instruction)

            try:
                return self._parse_evaluation(raw)

            except ValueError as exc:
                last_error = exc

                # Solo se reintenta cuando la salida
                # no puede convertirse en una evaluación válida.
                if attempt < self.MAX_ATTEMPTS:
                    continue

        raise RuntimeError(
            "No fue posible completar la evaluación "
            f"después de {self.MAX_ATTEMPTS} intentos. "
            f"Último error: {last_error}"
        ) from last_error

    def compare(
        self,
        entrada_a: str,
        respuesta_a: str,
        entrada_b: str,
        respuesta_b: str,
    ) -> ComparisonResult:

        # Cada respuesta se evalúa por separado.
        # No se comparten puntuaciones entre A y B.

        score_a = self._evaluate_single(
            entrada_a,
            respuesta_a
        )

        score_b = self._evaluate_single(
            entrada_b,
            respuesta_b
        )

        return ComparisonResult(
            respuesta_a=score_a,
            respuesta_b=score_b
        )
