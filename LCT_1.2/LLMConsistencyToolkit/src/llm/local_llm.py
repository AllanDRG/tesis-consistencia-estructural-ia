
from openai import OpenAI


class LocalLLM:

    def __init__(
        self,
        model="qwen/qwen3-8b",
        base_url="http://127.0.0.1:1234/v1"
    ):
        self.model = model

        self.client = OpenAI(
            base_url=base_url,
            api_key="lm-studio",
            timeout=180.0,
            max_retries=1
        )

    @staticmethod
    def _evaluation_schema():
        """
        Esquema de evaluación de profundidad explicativa.
        Conserva las cuatro dimensiones de LCT 1.2.
        """

        criterion = {
            "type": "object",
            "properties": {
                "score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 4
                },
                "justification": {
                    "type": "string"
                }
            },
            "required": [
                "score",
                "justification"
            ],
            "additionalProperties": False
        }

        dimensions = [
            "definicion_conceptual",
            "relacion_causal",
            "ejemplificacion",
            "aplicacion"
        ]

        return {
            "type": "object",
            "properties": {
                key: criterion
                for key in dimensions
            },
            "required": dimensions,
            "additionalProperties": False
        }

    def chat(self, message: str) -> str:
        """
        Envía una solicitud independiente al modelo local.

        Utiliza JSON Schema para evaluaciones estructuradas
        y texto normal para otras solicitudes.
        """

        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "La instrucción enviada al modelo está vacía."
            )

        requires_json = (
            "Devuelve EXCLUSIVAMENTE JSON válido" in message
        )

        system_instruction = (
            "Eres un asistente técnico del "
            "LLM Consistency Toolkit. "
            "Aplica exclusivamente los criterios proporcionados. "
            "No inventes información ni puntuaciones."
        )

        if requires_json:
            system_instruction += (
                " Devuelve únicamente JSON válido conforme "
                "al esquema solicitado. "
                "No agregues Markdown ni texto adicional."
            )

        parameters = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0,
            "max_tokens": 2048
        }

        if requires_json:
            parameters["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "lct_response_evaluation",
                    "strict": True,
                    "schema": self._evaluation_schema()
                }
            }

        try:
            response = self.client.chat.completions.create(
                **parameters
            )

        except Exception as exc:
            raise RuntimeError(
                "No fue posible obtener una respuesta "
                "del modelo local. "
                f"Detalle: {exc}"
            ) from exc

        if not response.choices:
            raise RuntimeError(
                "El modelo local no devolvió resultados."
            )

        choice = response.choices[0]
        content = choice.message.content

        if choice.finish_reason == "length":
            raise RuntimeError(
                "La respuesta del modelo fue truncada "
                "por el límite de tokens."
            )

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                "El modelo local devolvió una respuesta vacía."
            )

        return content.strip()
