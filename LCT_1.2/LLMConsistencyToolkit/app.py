import csv
import io
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

from src.validation.prompt_validator import PromptValidator
from src.validation.response_evaluator import ResponseEvaluator


st.set_page_config(
    page_title="LLM Consistency Toolkit",
    page_icon="🧪",
    layout="wide",
)

# Estilos visuales independientes de la lógica experimental.
from pathlib import Path

_STYLES = Path(__file__).with_name("styles.css")
if _STYLES.is_file():
    st.markdown("<style>" + _STYLES.read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)
else:
    st.warning("No se encontró styles.css. La evaluación sigue disponible sin animaciones.")

# ---------------------------------------------------------
# ESTADO
# ---------------------------------------------------------

if "ipe_result" not in st.session_state:
    st.session_state.ipe_result = None

if "iee_result" not in st.session_state:
    st.session_state.iee_result = None

if "iee_prompts" not in st.session_state:
    st.session_state.iee_prompts = ("", "")


# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------

st.markdown("""
<div class="cyber-hero">
  <div class="cyber-kicker">LCT 1.2 // RESEARCH INTERFACE</div>
  <h1 style="margin:4px 0 0">LLM Consistency Toolkit</h1>
  <div class="cyber-sub">Evaluación estructural de entradas y respuestas · Panel experimental</div>
  <div class="cyber-status">SISTEMA DE EVALUACIÓN LOCAL</div>
</div>
""", unsafe_allow_html=True)

# HUD ambiental: decorativo, sin indicadores ficticios de actividad.
st.markdown("""
<div class="lct-hud-strip" aria-label="Panel visual de interfaz">
  <div class="lct-hud-module"><span class="lct-hud-code">SYS // LCT-1.2</span><span class="lct-hud-copy">INTERFAZ EXPERIMENTAL</span></div>
  <div class="lct-hud-scanner" aria-hidden="true"><span class="lct-hud-ring r1"></span><span class="lct-hud-ring r2"></span><span class="lct-hud-core"></span></div>
  <div class="lct-hud-module lct-hud-right"><span class="lct-hud-code">IEE / IPE</span><span class="lct-hud-copy">EVALUACIÓN ESTRUCTURAL</span></div>
</div>
""", unsafe_allow_html=True)

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
                    st.session_state.iee_result = result
                    st.session_state.iee_prompts = (
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

                st.metric(
                    "Mínimo dimensional",
                    f"{result.minimo_dimensional}/4",
                )

                iee_chart = go.Figure(go.Bar(
                    x=["Semántica", "Objetivo", "Nivel cognitivo", "Alcance", "Neutralidad"],
                    y=[result.equivalencia_semantica, result.equivalencia_objetivo,
                       result.equivalencia_cognitiva, result.equivalencia_alcance,
                       result.neutralidad_reformulacion],
                    marker_color="#44ead7",
                    text=[result.equivalencia_semantica, result.equivalencia_objetivo,
                          result.equivalencia_cognitiva, result.equivalencia_alcance,
                          result.neutralidad_reformulacion],
                    textposition="outside",
                ))
                iee_chart.update_layout(
                    height=315, paper_bgcolor="#0b1426", plot_bgcolor="#0b1426",
                    font=dict(color="#dce9f9"), margin=dict(l=20,r=20,t=20,b=25),
                    yaxis=dict(range=[0,4.6], dtick=1, gridcolor="#23334c"),
                )
                st.plotly_chart(iee_chart, use_container_width=True)

                if result.admisible:
                    st.success("ESTADO: ADMISIBLE")
                else:
                    st.warning("ESTADO: REQUIERE REVISIÓN")

                st.caption(result.motivo_admision)
                st.caption(
                    "Criterio operativo: IEE >= 90 y ninguna dimensión < 3/4. "
                    "La decisión final permanece bajo revisión del investigador."
                )

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

        vector_a = [
            official_scores["a_definicion_conceptual"],
            official_scores["a_relacion_causal"],
            official_scores["a_ejemplificacion"],
            official_scores["a_aplicacion"],
        ]
        vector_b = [
            official_scores["b_definicion_conceptual"],
            official_scores["b_relacion_causal"],
            official_scores["b_ejemplificacion"],
            official_scores["b_aplicacion"],
        ]
        same_ipe = abs(official_delta) < 1e-9
        same_vector = vector_a == vector_b
        compensated_variation = same_ipe and not same_vector

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

        st.caption(
            f"Vector A: {vector_a} · Vector B: {vector_b} · "
            f"IPE igual: {'Sí' if same_ipe else 'No'} · "
            f"Vector igual: {'Sí' if same_vector else 'No'} · "
            f"Variación compensada: {'Sí' if compensated_variation else 'No'}"
        )

        st.subheader("Visualización dimensional")
        chart = go.Figure()
        dimension_labels = [label for label, _ in criteria]
        chart.add_trace(go.Bar(
            name="Respuesta A", x=dimension_labels, y=vector_a,
            marker_color="#44ead7", text=vector_a, textposition="outside"
        ))
        chart.add_trace(go.Bar(
            name="Respuesta B", x=dimension_labels, y=vector_b,
            marker_color="#e45ec8", text=vector_b, textposition="outside"
        ))
        chart.update_layout(
            barmode="group", height=380,
            paper_bgcolor="#0b1426", plot_bgcolor="#0b1426",
            font=dict(color="#dce9f9"),
            margin=dict(l=20, r=20, t=30, b=30),
            yaxis=dict(range=[0, 4.6], dtick=1, gridcolor="#23334c", title="Puntuación (0–4)"),
            xaxis=dict(tickangle=-15),
            legend=dict(orientation="h", y=1.14),
        )
        st.plotly_chart(chart, use_container_width=True)
        st.caption(
            "Visualización de las puntuaciones oficiales ajustadas por el investigador. "
            "La gráfica no modifica las evaluaciones ni los indicadores."
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
            "vector_a",
            "vector_b",
            "same_ipe",
            "same_vector",
            "compensated_variation",
            "iee",
            "iee_semantic",
            "iee_objective",
            "iee_cognitive",
            "iee_scope",
            "iee_neutrality",
            "iee_min_dimension",
            "iee_admission_status",
            "iee_admission_reason",
        ])

        iee_result = st.session_state.iee_result
        iee_prompt_a, iee_prompt_b = st.session_state.iee_prompts
        iee_matches_case = (
            iee_result is not None
            and iee_prompt_a == input_a.strip()
            and iee_prompt_b == input_b.strip()
        )

        if iee_result is not None and not iee_matches_case:
            st.warning(
                "El último IEE calculado no corresponde exactamente con las entradas "
                "A/B de este análisis IPE. Los campos IEE se exportarán vacíos para "
                "evitar asociar mediciones de casos distintos."
            )

        export_iee = iee_result if iee_matches_case else None

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
            str(vector_a),
            str(vector_b),
            same_ipe,
            same_vector,
            compensated_variation,
            f"{export_iee.iee:.2f}" if export_iee else "",
            export_iee.equivalencia_semantica if export_iee else "",
            export_iee.equivalencia_objetivo if export_iee else "",
            export_iee.equivalencia_cognitiva if export_iee else "",
            export_iee.equivalencia_alcance if export_iee else "",
            export_iee.neutralidad_reformulacion if export_iee else "",
            export_iee.minimo_dimensional if export_iee else "",
            export_iee.estado_admision if export_iee else "",
            export_iee.motivo_admision if export_iee else "",
        ])

        filename = (
            f"{case_id or 'LCT_CASE'}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        st.download_button(
            "Descargar resultado CSV",
            data=output.getvalue().encode("utf-8-sig"),
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
        )

        st.caption(
            "Qwen propone · Python calcula · "
            "el investigador establece la puntuación oficial."
        )
