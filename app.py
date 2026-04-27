# ============================================================
# APP: Alfabetización en IA para estudiantes de ciencias de la salud
# Con guardado automático en Supabase/PostgreSQL
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from sqlalchemy import text

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Alfabetización en IA en salud",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# ESCALAS
# ============================================================

LIKERT_7 = {
    1: "1 - Totalmente en desacuerdo",
    2: "2 - En desacuerdo",
    3: "3 - Algo en desacuerdo",
    4: "4 - Ni de acuerdo ni en desacuerdo",
    5: "5 - Algo de acuerdo",
    6: "6 - De acuerdo",
    7: "7 - Totalmente de acuerdo"
}

LIKERT_5 = {
    1: "1 - Totalmente en desacuerdo",
    2: "2 - En desacuerdo",
    3: "3 - Ni de acuerdo ni en desacuerdo",
    4: "4 - De acuerdo",
    5: "5 - Totalmente de acuerdo"
}


# ============================================================
# ÍTEMS
# Nota: versión operativa docente basada en dimensiones validadas.
# Para publicación psicométrica, requiere validación local.
# ============================================================

SNAIL_ITEMS = [
    {"id": "SNAIL_TU_01", "dimension": "Comprensión técnica", "item": "Puedo explicar, en términos generales, qué es la inteligencia artificial."},
    {"id": "SNAIL_TU_02", "dimension": "Comprensión técnica", "item": "Puedo diferenciar una herramienta de IA de un programa informático tradicional."},
    {"id": "SNAIL_TU_03", "dimension": "Comprensión técnica", "item": "Comprendo que muchos sistemas de IA aprenden patrones a partir de datos."},
    {"id": "SNAIL_TU_04", "dimension": "Comprensión técnica", "item": "Puedo explicar por qué la calidad de los datos influye en el resultado de un sistema de IA."},
    {"id": "SNAIL_TU_05", "dimension": "Comprensión técnica", "item": "Comprendo que los sistemas de IA pueden cometer errores aunque parezcan seguros."},
    {"id": "SNAIL_TU_06", "dimension": "Comprensión técnica", "item": "Puedo reconocer ejemplos de aprendizaje automático en aplicaciones cotidianas."},
    {"id": "SNAIL_TU_07", "dimension": "Comprensión técnica", "item": "Entiendo que un modelo de IA puede funcionar bien en un contexto y mal en otro."},
    {"id": "SNAIL_TU_08", "dimension": "Comprensión técnica", "item": "Comprendo que la IA generativa produce respuestas probabilísticas, no verdades garantizadas."},
    {"id": "SNAIL_TU_09", "dimension": "Comprensión técnica", "item": "Puedo explicar de forma básica qué significa entrenar un modelo de IA."},
    {"id": "SNAIL_TU_10", "dimension": "Comprensión técnica", "item": "Comprendo la diferencia entre datos de entrada, procesamiento y salida en un sistema de IA."},
    {"id": "SNAIL_TU_11", "dimension": "Comprensión técnica", "item": "Puedo explicar por qué una IA puede reproducir sesgos presentes en los datos."},
    {"id": "SNAIL_TU_12", "dimension": "Comprensión técnica", "item": "Comprendo que los sistemas de IA no tienen comprensión humana, aunque generen lenguaje coherente."},
    {"id": "SNAIL_TU_13", "dimension": "Comprensión técnica", "item": "Puedo identificar límites técnicos de una herramienta de IA antes de usarla."},
    {"id": "SNAIL_TU_14", "dimension": "Comprensión técnica", "item": "Comprendo que los resultados de IA deben interpretarse según el contexto y el propósito de uso."},

    {"id": "SNAIL_CA_01", "dimension": "Valoración crítica", "item": "Antes de aceptar una respuesta de IA, verifico si la información proviene de fuentes confiables."},
    {"id": "SNAIL_CA_02", "dimension": "Valoración crítica", "item": "Puedo identificar cuándo una respuesta de IA puede contener información falsa o inventada."},
    {"id": "SNAIL_CA_03", "dimension": "Valoración crítica", "item": "Reconozco que el uso de IA en salud requiere precauciones éticas adicionales."},
    {"id": "SNAIL_CA_04", "dimension": "Valoración crítica", "item": "Soy capaz de cuestionar los resultados de IA cuando afectan decisiones académicas o clínicas."},
    {"id": "SNAIL_CA_05", "dimension": "Valoración crítica", "item": "Considero la privacidad y la confidencialidad antes de ingresar información en una herramienta de IA."},
    {"id": "SNAIL_CA_06", "dimension": "Valoración crítica", "item": "Puedo reconocer riesgos de sesgo, discriminación o inequidad en sistemas de IA."},
    {"id": "SNAIL_CA_07", "dimension": "Valoración crítica", "item": "Evalúo si una herramienta de IA es adecuada para la tarea antes de usarla."},
    {"id": "SNAIL_CA_08", "dimension": "Valoración crítica", "item": "Comprendo que una IA no debe reemplazar el juicio profesional en salud."},
    {"id": "SNAIL_CA_09", "dimension": "Valoración crítica", "item": "Puedo explicar por qué la transparencia del modelo es importante en contextos de salud."},
    {"id": "SNAIL_CA_10", "dimension": "Valoración crítica", "item": "Soy capaz de justificar cuándo el uso de IA es apropiado y cuándo no lo es."},

    {"id": "SNAIL_PA_01", "dimension": "Aplicación práctica", "item": "Puedo usar herramientas de IA para apoyar mi aprendizaje sin copiar respuestas de forma acrítica."},
    {"id": "SNAIL_PA_02", "dimension": "Aplicación práctica", "item": "Sé formular instrucciones claras para obtener mejores respuestas de una herramienta de IA."},
    {"id": "SNAIL_PA_03", "dimension": "Aplicación práctica", "item": "Puedo usar IA para organizar ideas, resumir información o planear tareas académicas."},
    {"id": "SNAIL_PA_04", "dimension": "Aplicación práctica", "item": "Puedo comparar la respuesta de una IA con literatura científica o guías académicas."},
    {"id": "SNAIL_PA_05", "dimension": "Aplicación práctica", "item": "Sé cuándo declarar el uso de IA en una actividad académica."},
    {"id": "SNAIL_PA_06", "dimension": "Aplicación práctica", "item": "Puedo integrar la IA como apoyo, manteniendo mi responsabilidad sobre el producto final."},
    {"id": "SNAIL_PA_07", "dimension": "Aplicación práctica", "item": "Puedo usar IA para practicar razonamiento clínico sin asumir que sus respuestas son diagnósticos definitivos."}
]


GAAIS_ITEMS = [
    {"id": "GAAIS_POS_01", "dimension": "Actitud positiva hacia la IA", "item": "La inteligencia artificial puede tener aplicaciones beneficiosas en la educación en salud."},
    {"id": "GAAIS_POS_02", "dimension": "Actitud positiva hacia la IA", "item": "La inteligencia artificial puede apoyar el aprendizaje de los estudiantes de ciencias de la salud."},
    {"id": "GAAIS_POS_03", "dimension": "Actitud positiva hacia la IA", "item": "Me interesa aprender a usar herramientas de inteligencia artificial de forma responsable."},
    {"id": "GAAIS_POS_04", "dimension": "Actitud positiva hacia la IA", "item": "La inteligencia artificial puede ayudar a mejorar algunos procesos académicos o clínicos."},
    {"id": "GAAIS_POS_05", "dimension": "Actitud positiva hacia la IA", "item": "Considero que comprender la IA será importante para mi futuro profesional."},

    {"id": "GAAIS_NEG_01", "dimension": "Preocupación o actitud negativa hacia la IA", "item": "Me preocupa que la inteligencia artificial se use sin suficiente supervisión humana."},
    {"id": "GAAIS_NEG_02", "dimension": "Preocupación o actitud negativa hacia la IA", "item": "Me preocupa que los estudiantes dependan demasiado de la inteligencia artificial."},
    {"id": "GAAIS_NEG_03", "dimension": "Preocupación o actitud negativa hacia la IA", "item": "Me preocupa que la inteligencia artificial produzca errores difíciles de detectar."},
    {"id": "GAAIS_NEG_04", "dimension": "Preocupación o actitud negativa hacia la IA", "item": "Me preocupa que la inteligencia artificial afecte la privacidad de las personas."},
    {"id": "GAAIS_NEG_05", "dimension": "Preocupación o actitud negativa hacia la IA", "item": "Me preocupa que la inteligencia artificial sea usada de manera poco ética en salud."}
]


# ============================================================
# FUNCIONES DE CÁLCULO
# ============================================================

def porcentaje_desde_media(media, minimo, maximo):
    if pd.isna(media):
        return np.nan
    return ((media - minimo) / (maximo - minimo)) * 100


def interpretar_porcentaje(porcentaje):
    if pd.isna(porcentaje):
        return "Sin información suficiente"
    if porcentaje < 40:
        return "Nivel bajo"
    elif porcentaje < 70:
        return "Nivel intermedio"
    else:
        return "Nivel alto"


def recomendacion_por_nivel(nombre, porcentaje):
    nivel = interpretar_porcentaje(porcentaje)

    if nivel == "Nivel bajo":
        return (
            f"En {nombre} se recomienda iniciar con formación básica, ejemplos guiados, "
            "actividades demostrativas y verificación constante de comprensión."
        )
    elif nivel == "Nivel intermedio":
        return (
            f"En {nombre} se recomienda fortalecer la aplicación contextual, el análisis crítico "
            "y la transferencia a problemas propios de ciencias de la salud."
        )
    elif nivel == "Nivel alto":
        return (
            f"En {nombre} se observa un desempeño favorable. Se recomienda avanzar hacia tareas "
            "de evaluación crítica, uso ético, diseño de instrucciones y análisis de casos complejos."
        )
    else:
        return "No fue posible generar recomendación por ausencia de datos."


def calcular_resultados(respuestas, items, minimo, maximo):
    registros = []

    for item in items:
        valor = respuestas.get(item["id"], np.nan)
        registros.append({
            "id": item["id"],
            "dimension": item["dimension"],
            "item": item["item"],
            "respuesta": valor
        })

    df = pd.DataFrame(registros)

    resumen_dimension = (
        df.groupby("dimension")
        .agg(
            n_items=("respuesta", "count"),
            media=("respuesta", "mean"),
            suma=("respuesta", "sum")
        )
        .reset_index()
    )

    resumen_dimension["porcentaje"] = resumen_dimension["media"].apply(
        lambda x: porcentaje_desde_media(x, minimo, maximo)
    )

    resumen_dimension["interpretacion"] = resumen_dimension["porcentaje"].apply(
        interpretar_porcentaje
    )

    media_global = df["respuesta"].mean()
    porcentaje_global = porcentaje_desde_media(media_global, minimo, maximo)

    resultado_global = {
        "media_global": media_global,
        "porcentaje_global": porcentaje_global,
        "interpretacion_global": interpretar_porcentaje(porcentaje_global)
    }

    return df, resumen_dimension, resultado_global


def cronbach_alpha(df_items):
    df = df_items.dropna(axis=0, how="any")

    if df.shape[0] < 2 or df.shape[1] < 2:
        return np.nan

    item_variances = df.var(axis=0, ddof=1)
    total_score = df.sum(axis=1)
    n_items = df.shape[1]
    total_variance = total_score.var(ddof=1)

    if total_variance == 0:
        return np.nan

    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
    return alpha


# ============================================================
# GUARDADO EN SUPABASE / POSTGRESQL
# ============================================================

def guardar_respuestas_en_bd(
    datos_participante,
    df_snail,
    global_snail,
    df_gaais,
    global_gaais
):
    """
    Guarda cada respuesta individual en Supabase/PostgreSQL.
    Requiere configurar en Streamlit Secrets:

    [connections.respuestas_db]
    url = "postgresql://usuario:contraseña@host:puerto/postgres"
    """

    conn = st.connection("respuestas_db", type="sql")

    df_snail_export = df_snail.copy()
    df_snail_export["instrumento"] = "SNAIL - Alfabetización en IA"
    df_snail_export["porcentaje_global_alfabetizacion"] = global_snail["porcentaje_global"]
    df_snail_export["interpretacion_global_alfabetizacion"] = global_snail["interpretacion_global"]
    df_snail_export["porcentaje_global_actitudes"] = global_gaais["porcentaje_global"]
    df_snail_export["interpretacion_global_actitudes"] = global_gaais["interpretacion_global"]

    df_gaais_export = df_gaais.copy()
    df_gaais_export["instrumento"] = "GAAIS - Actitudes hacia IA"
    df_gaais_export["porcentaje_global_alfabetizacion"] = global_snail["porcentaje_global"]
    df_gaais_export["interpretacion_global_alfabetizacion"] = global_snail["interpretacion_global"]
    df_gaais_export["porcentaje_global_actitudes"] = global_gaais["porcentaje_global"]
    df_gaais_export["interpretacion_global_actitudes"] = global_gaais["interpretacion_global"]

    df_final = pd.concat([df_snail_export, df_gaais_export], ignore_index=True)

    with conn.session as session:
        for _, row in df_final.iterrows():
            session.execute(
                text("""
                    INSERT INTO respuestas_ia_salud (
                        codigo,
                        programa,
                        semestre,
                        edad,
                        uso_ia,
                        instrumento,
                        item_id,
                        dimension,
                        item_texto,
                        respuesta,
                        porcentaje_global_alfabetizacion,
                        interpretacion_global_alfabetizacion,
                        porcentaje_global_actitudes,
                        interpretacion_global_actitudes
                    )
                    VALUES (
                        :codigo,
                        :programa,
                        :semestre,
                        :edad,
                        :uso_ia,
                        :instrumento,
                        :item_id,
                        :dimension,
                        :item_texto,
                        :respuesta,
                        :porcentaje_global_alfabetizacion,
                        :interpretacion_global_alfabetizacion,
                        :porcentaje_global_actitudes,
                        :interpretacion_global_actitudes
                    )
                """),
                {
                    "codigo": datos_participante["codigo"],
                    "programa": datos_participante["programa"],
                    "semestre": datos_participante["semestre"],
                    "edad": int(datos_participante["edad"]),
                    "uso_ia": datos_participante["uso_ia"],
                    "instrumento": row["instrumento"],
                    "item_id": row["id"],
                    "dimension": row["dimension"],
                    "item_texto": row["item"],
                    "respuesta": int(row["respuesta"]),
                    "porcentaje_global_alfabetizacion": float(row["porcentaje_global_alfabetizacion"]),
                    "interpretacion_global_alfabetizacion": row["interpretacion_global_alfabetizacion"],
                    "porcentaje_global_actitudes": float(row["porcentaje_global_actitudes"]),
                    "interpretacion_global_actitudes": row["interpretacion_global_actitudes"]
                }
            )

        session.commit()


# ============================================================
# PDF
# ============================================================

def crear_pdf(
    datos_participante,
    resumen_snail,
    global_snail,
    resumen_gaais,
    global_gaais,
    respuestas_snail,
    respuestas_gaais
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "Titulo",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
        spaceAfter=12
    )

    subtitulo_style = ParagraphStyle(
        "Subtitulo",
        parent=styles["Heading2"],
        alignment=TA_LEFT,
        fontSize=12,
        leading=14,
        spaceBefore=10,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        spaceAfter=6
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )

    story = []

    story.append(Paragraph(
        "Informe de alfabetización en inteligencia artificial para estudiantes de ciencias de la salud",
        titulo_style
    ))

    story.append(Paragraph(
        f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        normal_style
    ))

    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Datos generales", subtitulo_style))

    datos_tabla = [
        ["Campo", "Respuesta"],
        ["Nombre o código", datos_participante.get("codigo", "")],
        ["Programa", datos_participante.get("programa", "")],
        ["Semestre", datos_participante.get("semestre", "")],
        ["Edad", str(datos_participante.get("edad", ""))],
        ["Uso previo de IA", datos_participante.get("uso_ia", "")]
    ]

    tabla = Table(datos_tabla, colWidths=[150, 330])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))
    story.append(tabla)

    story.append(Spacer(1, 12))
    story.append(Paragraph("2. Resultados: alfabetización en IA", subtitulo_style))

    texto_snail = (
        f"Puntaje global: {global_snail['porcentaje_global']:.1f}% "
        f"({global_snail['interpretacion_global']}). "
        f"Media global: {global_snail['media_global']:.2f} sobre 7."
    )
    story.append(Paragraph(texto_snail, normal_style))

    tabla_snail = [["Dimensión", "Media", "Porcentaje", "Interpretación"]]
    for _, row in resumen_snail.iterrows():
        tabla_snail.append([
            row["dimension"],
            f"{row['media']:.2f}",
            f"{row['porcentaje']:.1f}%",
            row["interpretacion"]
        ])

    t_snail = Table(tabla_snail, colWidths=[210, 70, 80, 120])
    t_snail.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))
    story.append(t_snail)

    story.append(Spacer(1, 8))
    story.append(Paragraph("Recomendaciones por dimensión", subtitulo_style))

    for _, row in resumen_snail.iterrows():
        story.append(Paragraph(
            f"<b>{row['dimension']}:</b> {recomendacion_por_nivel(row['dimension'], row['porcentaje'])}",
            normal_style
        ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("3. Resultados: actitudes hacia la IA", subtitulo_style))

    texto_gaais = (
        f"Puntaje global: {global_gaais['porcentaje_global']:.1f}% "
        f"({global_gaais['interpretacion_global']}). "
        f"Media global: {global_gaais['media_global']:.2f} sobre 5."
    )
    story.append(Paragraph(texto_gaais, normal_style))

    tabla_gaais = [["Dimensión", "Media", "Porcentaje", "Interpretación"]]
    for _, row in resumen_gaais.iterrows():
        tabla_gaais.append([
            row["dimension"],
            f"{row['media']:.2f}",
            f"{row['porcentaje']:.1f}%",
            row["interpretacion"]
        ])

    t_gaais = Table(tabla_gaais, colWidths=[210, 70, 80, 120])
    t_gaais.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))
    story.append(t_gaais)

    story.append(Spacer(1, 12))
    story.append(Paragraph("4. Nota metodológica", subtitulo_style))

    nota = (
        "Este informe tiene propósito educativo y descriptivo. Los puntos de corte bajo, intermedio y alto "
        "son criterios operativos para retroalimentación pedagógica; no equivalen a baremos clínicos ni "
        "a normas poblacionales. La versión en español incluida en la aplicación debe considerarse una "
        "adaptación operativa. Para uso investigativo publicable, se recomienda realizar traducción directa, "
        "traducción inversa, juicio de expertos, pilotaje, análisis de consistencia interna, análisis factorial "
        "y evaluación de validez de contenido y constructo."
    )
    story.append(Paragraph(nota, normal_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph("5. Referencias base", subtitulo_style))

    referencias = [
        "Laupichler, M. C., Aster, A., Haverkamp, N., & Raupach, T. (2023). Development of the “Scale for the assessment of non-experts’ AI literacy” – An exploratory factor analysis. Computers in Human Behavior Reports, 12, 100338. https://doi.org/10.1016/j.chbr.2023.100338",
        "Laupichler, M. C., Aster, A., Meyerheim, M., Raupach, T., & Mergen, M. (2024). Medical students’ AI literacy and attitudes towards AI: A cross-sectional two-center study using pre-validated assessment instruments. BMC Medical Education, 24, 401. https://doi.org/10.1186/s12909-024-05400-7",
        "Schepman, A., & Rodway, P. (2020). Initial validation of the general attitudes towards Artificial Intelligence Scale. Computers in Human Behavior Reports, 1, 100014. https://doi.org/10.1016/j.chbr.2020.100014"
    ]

    for ref in referencias:
        story.append(Paragraph(ref, small_style))

    story.append(PageBreak())
    story.append(Paragraph("Anexo. Respuestas por ítem", subtitulo_style))

    story.append(Paragraph("SNAIL - Alfabetización en IA", subtitulo_style))
    for _, row in respuestas_snail.iterrows():
        story.append(Paragraph(
            f"<b>{row['id']} | {row['dimension']}:</b> {row['item']} <br/>Respuesta: {row['respuesta']}",
            small_style
        ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("GAAIS - Actitudes hacia IA", subtitulo_style))
    for _, row in respuestas_gaais.iterrows():
        story.append(Paragraph(
            f"<b>{row['id']} | {row['dimension']}:</b> {row['item']} <br/>Respuesta: {row['respuesta']}",
            small_style
        ))

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# ============================================================
# INTERFAZ
# ============================================================

st.title("🧠 Alfabetización en inteligencia artificial para estudiantes de ciencias de la salud")

st.markdown(
    """
Esta aplicación permite diligenciar dos formularios:

**1. Alfabetización en IA**, basada en la estructura del instrumento SNAIL.  
**2. Actitudes hacia la IA**, basada en la estructura del instrumento GAAIS.

Al finalizar, la aplicación calcula resultados, genera un informe PDF y guarda automáticamente las respuestas en la base de datos.
"""
)

st.warning(
    "Nota metodológica: los ítems en español incluidos son una adaptación operativa docente. "
    "Para investigación psicométrica publicable, valide formalmente la traducción/adaptación antes de reportarla como versión validada."
)


# ============================================================
# DATOS GENERALES
# ============================================================

st.header("1. Datos generales del estudiante")

col1, col2 = st.columns(2)

with col1:
    codigo = st.text_input("Nombre o código del estudiante")
    programa = st.selectbox(
        "Programa académico",
        [
            "Fisioterapia",
            "Fonoaudiología",
            "Terapia Ocupacional",
            "Medicina",
            "Enfermería",
            "Otro"
        ]
    )
    semestre = st.selectbox(
        "Semestre",
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Otro"]
    )

with col2:
    edad = st.number_input("Edad", min_value=10, max_value=100, value=18, step=1)
    uso_ia = st.selectbox(
        "Frecuencia de uso previo de herramientas de IA",
        [
            "Nunca",
            "Rara vez",
            "Algunas veces al mes",
            "Algunas veces a la semana",
            "Todos o casi todos los días"
        ]
    )


datos_participante = {
    "codigo": codigo,
    "programa": programa,
    "semestre": semestre,
    "edad": edad,
    "uso_ia": uso_ia
}


# ============================================================
# FORMULARIO SNAIL
# ============================================================

st.header("2. Formulario de alfabetización en IA")

st.markdown(
    "Escala de respuesta: **1 = Totalmente en desacuerdo** a **7 = Totalmente de acuerdo**."
)

respuestas_snail = {}

for dimension in ["Comprensión técnica", "Valoración crítica", "Aplicación práctica"]:
    with st.expander(f"Dimensión: {dimension}", expanded=False):
        items_dimension = [i for i in SNAIL_ITEMS if i["dimension"] == dimension]

        for item in items_dimension:
            respuesta = st.radio(
                label=f"{item['id']}. {item['item']}",
                options=list(LIKERT_7.keys()),
                format_func=lambda x: LIKERT_7[x],
                horizontal=False,
                key=item["id"],
                index=None
            )
            respuestas_snail[item["id"]] = respuesta


# ============================================================
# FORMULARIO GAAIS
# ============================================================

st.header("3. Formulario de actitudes hacia la IA")

st.markdown(
    "Escala de respuesta: **1 = Totalmente en desacuerdo** a **5 = Totalmente de acuerdo**."
)

respuestas_gaais = {}

for dimension in ["Actitud positiva hacia la IA", "Preocupación o actitud negativa hacia la IA"]:
    with st.expander(f"Dimensión: {dimension}", expanded=False):
        items_dimension = [i for i in GAAIS_ITEMS if i["dimension"] == dimension]

        for item in items_dimension:
            respuesta = st.radio(
                label=f"{item['id']}. {item['item']}",
                options=list(LIKERT_5.keys()),
                format_func=lambda x: LIKERT_5[x],
                horizontal=False,
                key=item["id"],
                index=None
            )
            respuestas_gaais[item["id"]] = respuesta


# ============================================================
# PROGRESO
# ============================================================

total_snail = len(SNAIL_ITEMS)
total_gaais = len(GAAIS_ITEMS)

contestadas_snail = sum(1 for v in respuestas_snail.values() if v is not None)
contestadas_gaais = sum(1 for v in respuestas_gaais.values() if v is not None)

st.sidebar.header("Progreso")
st.sidebar.write(f"SNAIL: {contestadas_snail}/{total_snail} ítems")
st.sidebar.progress(contestadas_snail / total_snail)

st.sidebar.write(f"GAAIS: {contestadas_gaais}/{total_gaais} ítems")
st.sidebar.progress(contestadas_gaais / total_gaais)


# ============================================================
# RESULTADOS
# ============================================================

st.header("4. Resultados")

calcular = st.button("Calcular resultados, guardar respuestas y preparar informe PDF")

if calcular:

    if contestadas_snail < total_snail or contestadas_gaais < total_gaais:
        st.error("Faltan respuestas por diligenciar. Revisa los formularios antes de calcular el informe.")

    elif not codigo.strip():
        st.error("Por favor diligencia el nombre o código del estudiante.")

    else:
        df_snail, resumen_snail, global_snail = calcular_resultados(
            respuestas=respuestas_snail,
            items=SNAIL_ITEMS,
            minimo=1,
            maximo=7
        )

        df_gaais, resumen_gaais, global_gaais = calcular_resultados(
            respuestas=respuestas_gaais,
            items=GAAIS_ITEMS,
            minimo=1,
            maximo=5
        )

        st.success("Resultados calculados correctamente.")

        try:
            guardar_respuestas_en_bd(
                datos_participante=datos_participante,
                df_snail=df_snail,
                global_snail=global_snail,
                df_gaais=df_gaais,
                global_gaais=global_gaais
            )

            st.success("Las respuestas fueron guardadas correctamente en la base de datos.")

        except Exception as e:
            st.warning(
                f"Los resultados se calcularon, pero no fue posible guardar en la base de datos: {e}"
            )

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Alfabetización en IA")
            st.metric("Porcentaje global", f"{global_snail['porcentaje_global']:.1f}%")
            st.write(f"**Interpretación:** {global_snail['interpretacion_global']}")
            st.dataframe(resumen_snail, use_container_width=True)

        with col_b:
            st.subheader("Actitudes hacia la IA")
            st.metric("Porcentaje global", f"{global_gaais['porcentaje_global']:.1f}%")
            st.write(f"**Interpretación:** {global_gaais['interpretacion_global']}")
            st.dataframe(resumen_gaais, use_container_width=True)

        st.subheader("Recomendaciones pedagógicas automáticas")

        st.markdown("### Alfabetización en IA")
        for _, row in resumen_snail.iterrows():
            st.write(
                f"**{row['dimension']}**: "
                f"{recomendacion_por_nivel(row['dimension'], row['porcentaje'])}"
            )

        st.markdown("### Actitudes hacia la IA")
        for _, row in resumen_gaais.iterrows():
            st.write(
                f"**{row['dimension']}**: "
                f"{recomendacion_por_nivel(row['dimension'], row['porcentaje'])}"
            )

        df_snail_export = df_snail.copy()
        df_snail_export["instrumento"] = "SNAIL - Alfabetización en IA"

        df_gaais_export = df_gaais.copy()
        df_gaais_export["instrumento"] = "GAAIS - Actitudes hacia IA"

        df_export = pd.concat([df_snail_export, df_gaais_export], ignore_index=True)

        for k, v in datos_participante.items():
            df_export[k] = v

        csv = df_export.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Descargar respuestas en CSV",
            data=csv,
            file_name=f"respuestas_ia_{codigo}.csv",
            mime="text/csv"
        )

        pdf = crear_pdf(
            datos_participante=datos_participante,
            resumen_snail=resumen_snail,
            global_snail=global_snail,
            resumen_gaais=resumen_gaais,
            global_gaais=global_gaais,
            respuestas_snail=df_snail,
            respuestas_gaais=df_gaais
        )

        st.download_button(
            label="Descargar informe PDF",
            data=pdf,
            file_name=f"informe_alfabetizacion_ia_{codigo}.pdf",
            mime="application/pdf"
        )


# ============================================================
# ANÁLISIS GRUPAL OPCIONAL
# ============================================================

st.header("5. Análisis grupal opcional")

st.markdown(
    """
Cuando tengas varios archivos CSV descargados desde esta aplicación, puedes unirlos en Excel
o cargarlos aquí posteriormente para calcular consistencia interna y análisis grupales.
"""
)

archivo_grupal = st.file_uploader(
    "Sube un CSV consolidado con respuestas de varios estudiantes",
    type=["csv"]
)

if archivo_grupal is not None:
    try:
        df_grupal = pd.read_csv(archivo_grupal)

        st.subheader("Vista previa de datos grupales")
        st.dataframe(df_grupal.head(), use_container_width=True)

        if "instrumento" in df_grupal.columns and "id" in df_grupal.columns and "respuesta" in df_grupal.columns:
            resultados_alpha = []

            for instrumento in df_grupal["instrumento"].dropna().unique():
                df_inst = df_grupal[df_grupal["instrumento"] == instrumento].copy()

                if "codigo" not in df_inst.columns:
                    st.warning("El archivo debe incluir la columna 'codigo' para análisis grupal.")
                    continue

                matriz = df_inst.pivot_table(
                    index="codigo",
                    columns="id",
                    values="respuesta",
                    aggfunc="first"
                )

                alpha = cronbach_alpha(matriz)
                resultados_alpha.append({
                    "instrumento": instrumento,
                    "n_estudiantes": matriz.shape[0],
                    "n_items": matriz.shape[1],
                    "alpha_cronbach": alpha
                })

            if resultados_alpha:
                df_alpha = pd.DataFrame(resultados_alpha)
                st.subheader("Consistencia interna grupal")
                st.dataframe(df_alpha, use_container_width=True)

            resumen_grupal = (
                df_grupal
                .groupby(["instrumento", "dimension"])
                .agg(
                    media=("respuesta", "mean"),
                    desviacion=("respuesta", "std"),
                    n_respuestas=("respuesta", "count")
                )
                .reset_index()
            )

            st.subheader("Resumen grupal por dimensión")
            st.dataframe(resumen_grupal, use_container_width=True)

        else:
            st.error(
                "El CSV debe contener, como mínimo, las columnas: instrumento, id, dimension, respuesta y codigo."
            )

    except Exception as e:
        st.error(f"No fue posible leer el archivo: {e}")


# ============================================================
# PIE METODOLÓGICO
# ============================================================

st.divider()

st.markdown(
    """
**Referencias base:**  
- Laupichler, M. C., Aster, A., Haverkamp, N., & Raupach, T. (2023). *Development of the “Scale for the assessment of non-experts’ AI literacy” – An exploratory factor analysis*. Computers in Human Behavior Reports, 12, 100338.  
- Laupichler, M. C., Aster, A., Meyerheim, M., Raupach, T., & Mergen, M. (2024). *Medical students’ AI literacy and attitudes towards AI: A cross-sectional two-center study using pre-validated assessment instruments*. BMC Medical Education, 24, 401.  
- Schepman, A., & Rodway, P. (2020). *Initial validation of the general attitudes towards Artificial Intelligence Scale*. Computers in Human Behavior Reports, 1, 100014.
"""
)
