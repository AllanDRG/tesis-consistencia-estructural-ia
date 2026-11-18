import csv
import io
from datetime import datetime

import streamlit as st

from src.validation.prompt_validator import PromptValidator
from src.validation.response_evaluator import ResponseEvaluator


st.set_page_config(
    page_title="LLM Consistency Toolkit",
    page_icon="🧪",
    layout="wide",
)

# ---------------------------------------------------------
# ESTADO
# ---------------------------------------------------------

if "ipe_result" not in st.session_state:
    st.session_state.ipe_result = None


# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------

st.title("LLM Consistency Toolkit")
st.caption("LCT · Candidate Build · Experimental Analysis")

meta1, meta2, meta3, meta4 = st.columns([1, 1, 2, 2])

with meta1:
    mode = st.selectbox(
        "Modo",
        ["Piloto", "Oficial"],
    )

with meta2:
    case_id = st.text_input(
        "ID del caso",
        placeholder="NET-001",
    )

with meta3:
    area = st.text_input(
        "Área",
        placeholder="Redes",
    )

with meta4:
    topic = st.text_input(
        "Tema",
        placeholder="Latencia",
    )

if mode == "Piloto":
    st.info(
        "MODO PILOTO · Los resultados pueden utilizarse para calibrar "
        "el instrumento. No deben incorporarse todavía como datos oficiales."
    )
else:
    st.warning(
        "MODO OFICIAL · Utilice únicamente instrumentos previamente "
        "validados y congelados para la ejecución experimental."
    )


tab_iee, tab_ipe = st.tabs([
    "01 · Validación de entradas (IEE)",
    "02 · Análisis de respuestas (IPE)",
])


# =========================================================
# IEE
# =========================================================

with tab_iee:

    st.header("Índice de Equivalencia de Entrada")
    st.write(
        "Analiza preliminarmente si dos formulaciones mantienen "
        "equivalencia suficiente para una comparación experimental."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        prompt_a = st.text_area(
            "Entrada A",
            height=180,
            key="iee_a",
            placeholder="Ingrese la primera entrada...",
        )

    with col_b:
        prompt_b = st.text_area(
            "Entrada B",
            height=180,
            key="iee_b",
            placeholder="Ingrese la segunda entrada...",
        )

    if st.button(
        "Analizar equivalencia",
        type="primary",
        use_container_width=True,
    ):

        if not prompt_a.strip() or not prompt_b.strip():
            st.error("Debe ingresar ambas entradas.")

        else:
            try:
                with st.spinner("Analizando equivalencia..."):
                    result = PromptValidator().validate(
                        prompt_a.strip(),
                        prompt_b.strip(),
                    )

                st.divider()

                cols = st.columns(5)

                values = [
                    ("Semántica", result.equivalencia_semantica),
                    ("Objetivo", result.equivalencia_objetivo),
                    ("Nivel cognitivo", result.equivalencia_cognitiva),
                    ("Alcance", result.equivalencia_alcance),
                    ("Neutralidad", result.neutralidad_reformulacion),
                ]

                for col, (label, value) in zip(cols, values):
                    col.metric(label, f"{value}/4")

                st.subheader("IEE")
                st.progress(result.iee / 100)
                st.metric("Índice de equivalencia", f"{result.iee:.2f}/100")

                if result.iee >= 90:
                    st.success("ALTA EQUIVALENCIA")
                elif result.iee >= 75:
                    st.warning("REVISIÓN RECOMENDADA")
                else:
                    st.error("NO APTO")

                st.subheader("Justificación")
                st.write(result.justificacion)

            except Exception as exc:
                st.error("No fue posible completar el análisis.")
                st.exception(exc)


# =========================================================
# IPE
# =========================================================

with tab_ipe:

    st.header("Índice de Profundidad Explicativa")

    st.write(
        "Las respuestas A y B se evalúan independientemente. "
        "LCT propone puntuaciones y el investigador establece "
        "la evaluación oficial."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Caso A")

        input_a = st.text_area(
            "Entrada original A",
            height=100,
            key="ipe_input_a",
        )

        answer_a = st.text_area(
            "Respuesta A",
            height=260,
            key="ipe_answer_a",
        )

        st.caption(
            f"{len(answer_a.split())} palabras · "
            f"{len(answer_a)} caracteres"
        )

    with col_b:
        st.subheader("Caso B")

        input_b = st.text_area(
            "Entrada original B",
            height=100,
            key="ipe_input_b",
        )

        answer_b = st.text_area(
            "Respuesta B",
            height=260,
            key="ipe_answer_b",
        )

        st.caption(
            f"{len(answer_b.split())} palabras · "
            f"{len(answer_b)} caracteres"
        )

    if st.button(
        "Analizar respuestas",
        type="primary",
        use_container_width=True,
    ):

        fields = [input_a, answer_a, input_b, answer_b]

        if not all(field.strip() for field in fields):
            st.error("Debe completar ambas entradas y ambas respuestas.")

        else:
            try:
                with st.spinner(
                    "Evaluando A y B mediante solicitudes independientes..."
                ):
                    st.session_state.ipe_result = ResponseEvaluator().compare(
                        input_a.strip(),
                        answer_a.strip(),
                        input_b.strip(),
                        answer_b.strip(),
                    )

            except Exception as exc:
                st.error("No fue posible completar la evaluación.")
                st.exception(exc)

    result = st.session_state.ipe_result

    if result is not None:

        a = result.respuesta_a
        b = result.respuesta_b

        st.divider()
        st.header("Evaluación sugerida por LCT")

        criteria = [
            (
                "Definición conceptual",
                "definicion_conceptual",
            ),
            (
                "Relación causal",
                "relacion_causal",
            ),
            (
                "Ejemplificación",
                "ejemplificacion",
            ),
            (
                "Aplicación",
                "aplicacion",
            ),
        ]

        head = st.columns([2, 1, 1])
        head[0].markdown("**Criterio**")
        head[1].markdown("**A**")
        head[2].markdown("**B**")

        for label, attr in criteria:
            row = st.columns([2, 1, 1])
            row[0].write(label)
            row[1].write(f"{getattr(a, attr).score}/4")
            row[2].write(f"{getattr(b, attr).score}/4")

            with st.expander(f"Justificación · {label}"):
                ja, jb = st.columns(2)
                ja.markdown("**Respuesta A**")
                ja.write(getattr(a, attr).justification)
                jb.markdown("**Respuesta B**")
                jb.write(getattr(b, attr).justification)

        suggested = st.columns(3)
        suggested[0].metric("IPE sugerido A", f"{a.ipe:.2f}")
        suggested[1].metric("IPE sugerido B", f"{b.ipe:.2f}")
        suggested[2].metric(
            "ΔIPE sugerido",
            f"{result.delta_ipe:+.2f}",
        )

        st.divider()
        st.header("Evaluación oficial del investigador")

        st.caption(
            "Los valores sugeridos se cargan inicialmente, pero pueden "
            "modificarse antes de registrar el resultado oficial."
        )

        official_scores = {}

        for label, attr in criteria:

            cols = st.columns([2, 1, 1])

            cols[0].write(label)

            official_scores[f"a_{attr}"] = cols[1].number_input(
                f"A · {label}",
                min_value=0,
                max_value=4,
                value=getattr(a, attr).score,
                step=1,
                key=f"official_a_{attr}",
                label_visibility="collapsed",
            )

            official_scores[f"b_{attr}"] = cols[2].number_input(
                f"B · {label}",
                min_value=0,
                max_value=4,
                value=getattr(b, attr).score,
                step=1,
                key=f"official_b_{attr}",
                label_visibility="collapsed",
            )

        total_a = sum(
            official_scores[f"a_{attr}"]
            for _, attr in criteria
        )

        total_b = sum(
            official_scores[f"b_{attr}"]
            for _, attr in criteria
        )

        official_ipe_a = total_a / 16 * 100
        official_ipe_b = total_b / 16 * 100
        official_delta = official_ipe_a - official_ipe_b

        metrics = st.columns(4)

        metrics[0].metric(
            "IPE oficial A",
            f"{official_ipe_a:.2f}",
        )

        metrics[1].metric(
            "IPE oficial B",
            f"{official_ipe_b:.2f}",
        )

        metrics[2].metric(
            "ΔIPE oficial",
            f"{official_delta:+.2f}",
        )

        metrics[3].metric(
            "|ΔIPE|",
            f"{abs(official_delta):.2f}",
        )

        st.divider()

        # -------------------------------------------------
        # EXPORTACIÓN CSV
        # -------------------------------------------------

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow([
            "timestamp",
            "mode",
            "case_id",
            "area",
            "topic",
            "input_a",
            "input_b",
            "answer_a",
            "answer_b",
            "words_a",
            "words_b",
            "suggested_ipe_a",
            "suggested_ipe_b",
            "official_definition_a",
            "official_causal_a",
            "official_example_a",
            "official_application_a",
            "official_definition_b",
            "official_causal_b",
            "official_example_b",
            "official_application_b",
            "official_ipe_a",
            "official_ipe_b",
            "official_delta_ipe",
            "absolute_delta_ipe",
        ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            mode,
            case_id,
            area,
            topic,
            input_a,
            input_b,
            answer_a,
            answer_b,
            len(answer_a.split()),
            len(answer_b.split()),
            f"{a.ipe:.2f}",
            f"{b.ipe:.2f}",
            official_scores["a_definicion_conceptual"],
            official_scores["a_relacion_causal"],
            official_scores["a_ejemplificacion"],
            official_scores["a_aplicacion"],
            official_scores["b_definicion_conceptual"],
            official_scores["b_relacion_causal"],
            official_scores["b_ejemplificacion"],
            official_scores["b_aplicacion"],
            f"{official_ipe_a:.2f}",
            f"{official_ipe_b:.2f}",
            f"{official_delta:.2f}",
            f"{abs(official_delta):.2f}",
        ])

        filename = (
            f"{case_id or 'LCT_CASE'}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        st.download_button(
            "Descargar resultado CSV",
            data=output.getvalue(),
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
        )

        st.caption(
            "Qwen propone · Python calcula · "
            "el investigador establece la puntuación oficial."
        )
