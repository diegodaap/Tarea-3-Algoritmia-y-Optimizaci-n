import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak)

NOMBRE = "Diego Alejandro Puente Ruiz"
MATRICULA = 2095327
REPO = "https://github.com/diegodaap/Tarea-3-Algoritmia-y-Optimizaci-n"
N_BOOT = 10000

df = pd.read_csv("resultados.csv")
anova = pd.read_csv("anova.csv", index_col=0)
res = pd.read_csv("tabla_resumen.csv").set_index("n")
niv = df.groupby("nivel").temperatura.first().to_dict()
orden = ["bajo", "medio", "alto"]
rng = np.random.default_rng(MATRICULA)


def boot(x):
    m = np.median(rng.choice(np.asarray(x), size=(N_BOOT, len(x)), replace=True), axis=1)
    return np.median(m), np.percentile(m, 2.5), np.percentile(m, 97.5)


filas = []
for n in [5, 10, 15]:
    for nv in orden:
        med, lo, hi = boot(df[(df.tamano == n) & (df.nivel == nv)].costo)
        filas.append(dict(n=n, nivel=nv, T=niv[nv], med=med, lo=lo, hi=hi))
P = pd.DataFrame(filas)
best = P.loc[P.groupby("n").med.idxmin()].sort_values("n").set_index("n")
sd = df.groupby(["tamano", "nivel"]).costo.std().round(2)

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontSize=10, leading=14, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=14, spaceBefore=10)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, spaceBefore=8)
title = ParagraphStyle("t", parent=ss["Title"], fontSize=18)
small = ParagraphStyle("s", parent=body, fontSize=8.5, leading=11)


def tabla(data, widths=None):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EDF3")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def pv(p):
    return "< 0.0001" if p < 1e-4 else f"= {p:.4f}"


r = (niv["bajo"] - 0.1) / 99.9 / 0.3
pt, pn, pi = (anova.loc[k, "PR(>F)"] for k in
              ["C(temperatura)", "C(tamano)", "C(temperatura):C(tamano)"])
p10, p15, p5 = res.loc[10, "p_temperatura"], res.loc[15, "p_temperatura"], res.loc[5, "p_temperatura"]

S = []
azul = colors.HexColor("#1F3A5F")
c_inst = ParagraphStyle("ci", parent=body, fontSize=11, leading=15, textColor=colors.white, alignment=1)
c_tit = ParagraphStyle("ct", parent=body, fontSize=26, leading=32, textColor=colors.white, alignment=1)
c_sub = ParagraphStyle("cs", parent=body, fontSize=13, leading=18, textColor=colors.HexColor("#DCE6F2"), alignment=1)
c_dat = ParagraphStyle("cd", parent=body, fontSize=12, leading=18, alignment=1)
S.append(Spacer(1, 0.6 * inch))
banda = Table([[Paragraph("FACULTAD DE CIENCIAS F&Iacute;SICO MATEM&Aacute;TICAS<br/>Universidad Aut&oacute;noma de Nuevo Le&oacute;n", c_inst)],
               [Spacer(1, 0.5 * inch)],
               [Paragraph("<b>Ajuste de par&aacute;metros con<br/>Dise&ntilde;o de Experimentos</b>", c_tit)],
               [Spacer(1, 0.2 * inch)],
               [Paragraph("Temperatura del Recocido Simulado (2-opt) en el TSP", c_sub)],
               [Spacer(1, 0.5 * inch)]], colWidths=[6.8 * inch])
banda.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), azul),
                           ("TOPPADDING", (0, 0), (-1, 0), 22)]))
S.append(banda)
S.append(Spacer(1, 0.9 * inch))
S.append(Paragraph("<b>Tarea 3</b><br/>Algoritmia y Optimizaci&oacute;n", ParagraphStyle("ct2", parent=c_dat, fontSize=15, leading=22)))
S.append(Spacer(1, 0.5 * inch))
S.append(Paragraph(f"<b>{NOMBRE}</b><br/>Matr&iacute;cula {MATRICULA}", c_dat))
S.append(Spacer(1, 0.5 * inch))
S.append(Paragraph("Enfoque: Opci&oacute;n A (factorial completo 3 x 3, ANOVA de dos factores y bootstrap)", c_dat))
S.append(Spacer(1, 0.3 * inch))
S.append(Paragraph(f"Repositorio: {REPO}", ParagraphStyle("cr", parent=c_dat, fontSize=10)))
S.append(Spacer(1, 0.3 * inch))
S.append(Paragraph("15 de noviembre de 2026", ParagraphStyle("cf", parent=c_dat, fontSize=10, textColor=colors.grey)))
S.append(PageBreak())
S.append(Paragraph("1. Planteamiento y dise&ntilde;o", h1))
S.append(Paragraph(
    "Se ajusta la temperatura inicial T0 del Recocido Simulado con vecindario 2-opt sobre el TSP. El factor es T0 "
    "(3 niveles) y el bloque es el tama&ntilde;o del problema, n = 5, 10 y 15, con una instancia fija por tama&ntilde;o "
    "(ciudades con coordenadas aleatorias en [0, 100]). Cada combinacion se ejecuto 10 veces con semillas distintas, "
    "es decir 9 puntos de dise&ntilde;o y 90 corridas. La respuesta es el costo (longitud del recorrido) final.", body))
S.append(Paragraph(
    f"Los niveles se obtienen con un unico r generado una vez: <i>random.seed({MATRICULA}); r = random.random()</i>, "
    f"que resulto r = {r:.4f}. El rango de temperatura se fijo en [T_min, T_max] = [0.1, 100], de la misma escala que "
    "las distancias del problema. Con la Opcion A, las fracciones son 0.3r, 0.3r + 0.3 y 0.3r + 0.6, y "
    "T = T_min + fraccion x (T_max - T_min).", body))
S.append(tabla([["Nivel", "Fraccion", "T0"]] +
               [[nv, f"{f:.4f}", f"{niv[nv]:.2f}"] for nv, f in
                zip(orden, [0.3 * r, 0.3 * r + 0.3, 0.3 * r + 0.6])],
               [1.4 * inch, 1.4 * inch, 1.4 * inch]))
S.append(Spacer(1, 6))
S.append(Paragraph(
    "<b>Configuracion del algoritmo:</b> solucion inicial aleatoria, 150 iteraciones, enfriamiento geometrico "
    "con factor 0.97 y aceptacion de Metropolis. La respuesta es el costo del recorrido al terminar.", body))

S.append(Paragraph("2. ANOVA de dos factores (nivel de significancia 0.05)", h1))
nom = {"C(temperatura)": "Temperatura", "C(tamano)": "Tama&ntilde;o",
       "C(temperatura):C(tamano)": "Interaccion", "Residual": "Error"}
rows = [["Fuente", "Suma cuad.", "g.l.", "F", "p-value", "Signif."]]
for k, nm in nom.items():
    a = anova.loc[k]
    rows.append([Paragraph(nm, small), f"{a.sum_sq:.1f}", int(a.df),
                 "" if np.isnan(a.F) else f"{a.F:.3f}",
                 "" if np.isnan(a["PR(>F)"]) else ("< 0.0001" if a["PR(>F)"] < 1e-4 else f"{a['PR(>F)']:.4f}"),
                 "" if np.isnan(a.F) else ("Si" if a["PR(>F)"] < 0.05 else "No")])
S.append(tabla(rows))
S.append(Spacer(1, 6))
S.append(Paragraph(
    f"El tama&ntilde;o domina la variacion (p {pv(pn)}), algo esperable porque el costo crece con el numero de "
    f"ciudades. En cambio, ni la temperatura (p = {pt:.3f}) ni la interaccion temperatura x tama&ntilde;o "
    f"(p = {pi:.3f}) resultan significativas en el analisis global: no hay evidencia de que el efecto de "
    "la temperatura cambie de un tama&ntilde;o a otro. Como el costo de cada n tiene una escala muy distinta, "
    "se complemento con un ANOVA de un factor dentro de cada tama&ntilde;o (bloque).", body))
S.append(tabla([["n", "p-value (temperatura)", "Significativo"],
                [5, f"{p5:.4f}", "No"], [10, f"{p10:.4f}", "Si"], [15, f"{p15:.4f}", "No"]],
               [0.8 * inch, 2 * inch, 1.4 * inch]))

S.append(PageBreak())
S.append(Paragraph("3. Graficas", h1))
S.append(Paragraph("Efectos principales", h2))
S.append(Image("efectos_principales.png", width=6.3 * inch, height=2.52 * inch))
S.append(Paragraph("Interaccion temperatura x tama&ntilde;o", h2))
S.append(Image("interaccion.png", width=4.2 * inch, height=2.8 * inch))
S.append(Paragraph("Mediana bootstrap con IC 95% por punto de dise&ntilde;o", h2))
S.append(Image("bootstrap_medianas.png", width=6.5 * inch, height=2.0 * inch))

S.append(PageBreak())
S.append(Paragraph("4. Bootstrap de la mediana", h1))
S.append(Paragraph(f"Remuestreo con reemplazo ({N_BOOT} remuestras) e intervalo de confianza del 95% por percentiles. "
                   "Se reporta en los 9 puntos; el unico tama&ntilde;o con efecto significativo de la temperatura "
                   "es n = 10.", body))
rows = [["n", "Nivel", "T0", "Desv. est.", "Mediana boot.", "IC 95% inf.", "IC 95% sup."]]
for _, p in P.iterrows():
    rows.append([int(p.n), p.nivel, f"{p['T']:.2f}", f"{sd[(int(p.n), p.nivel)]:.2f}",
                 f"{p.med:.2f}", f"{p.lo:.2f}", f"{p.hi:.2f}"])
S.append(tabla(rows))

S.append(Paragraph("5. Mejor temperatura por tama&ntilde;o", h1))
rows = [["n", "T0 elegida", "Nivel", "Mediana bootstrap", "IC 95%"]]
for n, m in best.iterrows():
    rows.append([int(n), f"{m['T']:.2f}", m.nivel, f"{m.med:.2f}", f"[{m.lo:.2f}, {m.hi:.2f}]"])
S.append(tabla(rows))
S.append(Spacer(1, 6))
S.append(Paragraph(
    "<b>Criterio.</b> Para cada n se comparo la mediana bootstrap del costo en los tres niveles y se eligio la "
    "menor, apoyando la decision con el ANOVA dentro de cada tama&ntilde;o. Solo para n = 10 la diferencia entre "
    "temperaturas es estadisticamente significativa; en n = 5 y n = 15 la eleccion es indicativa.", body))

S.append(Paragraph("6. Analisis", h1))
S.append(Paragraph(
    f"<b>n = 5.</b> Casi todas las corridas llegan al mismo costo ({best.loc[5].med:.2f}), que es el optimo de una "
    "instancia con solo 12 recorridos distintos. Unicamente el nivel alto produjo una corrida peor, por lo que el "
    f"ANOVA no detecta efecto (p = {p5:.3f}). Se elige el nivel bajo, aunque la diferencia es practicamente nula.", body))
S.append(Paragraph(
    f"<b>n = 10.</b> Aqui si hay efecto significativo (p = {p10:.4f}). El nivel bajo obtiene la menor mediana "
    f"({best.loc[10].med:.2f}) y el medio queda muy cerca; el nivel alto es el peor "
    f"(mediana {P[(P.n == 10) & (P.nivel == 'alto')].med.iloc[0]:.2f}). Con solo 150 iteraciones, una temperatura "
    "alta mantiene al algoritmo aceptando empeoramientos hasta muy tarde y no le da tiempo de converger.", body))
S.append(Paragraph(
    f"<b>n = 15.</b> El nivel bajo tiene la menor mediana ({best.loc[15].med:.2f}), pero la variabilidad es muy "
    f"grande (desviaciones de 38 a 53) y el efecto no es significativo (p = {p15:.3f}); los intervalos "
    "bootstrap se traslapan casi por completo.", body))
S.append(Paragraph(
    "<b>Relacion entre n y T*.</b> En los tres tama&ntilde;os el mejor nivel es el bajo, de modo que no se observa una "
    "tendencia de T* con n. Esto es coherente con la interaccion no significativa del ANOVA global. La conclusion "
    "practica es que, con este esquema de enfriamiento corto, convienen temperaturas iniciales bajas a moderadas "
    "y las altas perjudican. Como los intervalos de n = 15 son anchos, un experimento con mas replicas o con mas "
    "iteraciones por corrida daria conclusiones mas firmes.", body))
S.append(Paragraph("7. Reproducibilidad", h1))
S.append(Paragraph(
    f"El codigo <i>doe_recocido.py</i> genera resultados.csv, anova.csv, tabla_resumen.csv y las graficas con la "
    f"semilla de la matricula {MATRICULA}. El reporte se genera con <i>make_pdf.py</i>.", body))

SimpleDocTemplate("DAPR_Tarea3.pdf", pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                  topMargin=0.7 * inch, bottomMargin=0.7 * inch, title="Tarea 3 DOE", author=NOMBRE).build(S)
