"""
Tarea 3 - Ajuste de temperatura del Recocido Simulado (2-opt, TSP) con DOE.
Opcion A: factorial completo 3 (temperatura) x 3 (tamano), 10 replicas por punto.
Salidas: graficas PNG, resultados.csv, anova.csv y tabla_resumen.csv
"""
import math
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

MATRICULA = 2095327
TAMANOS = [5, 10, 15]
REPLICAS = 10
T_MIN, T_MAX = 0.1, 100.0      # rango de temperatura elegido (coordenadas en [0,100])
ALPHA_ENF = 0.97               # enfriamiento geometrico
ITERACIONES = 150
N_BOOT = 10000
ALFA = 0.05

# ---------- r fijo (una sola vez, con la matricula como semilla) ----------
random.seed(MATRICULA)
r = random.random()
fracciones = {"bajo": 0.3 * r, "medio": 0.3 * r + 0.3, "alto": 0.3 * r + 0.6}
NIVELES = {k: T_MIN + f * (T_MAX - T_MIN) for k, f in fracciones.items()}
print(f"r = {r:.4f}")
print("Niveles de temperatura:", {k: round(v, 2) for k, v in NIVELES.items()})


# ---------- instancias TSP (una por tamano, fijas) ----------
def crear_instancia(n):
    rng = random.Random(MATRICULA + n)
    return [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]


def longitud(tour, pts):
    return sum(math.dist(pts[tour[i]], pts[tour[(i + 1) % len(tour)]])
               for i in range(len(tour)))


# ---------- Recocido simulado con vecindario 2-opt ----------
def recocido(pts, T0, semilla):
    rng = random.Random(semilla)
    n = len(pts)
    actual = list(range(n))
    rng.shuffle(actual)
    costo = longitud(actual, pts)
    mejor = costo
    T = T0
    for _ in range(ITERACIONES):
        i, j = sorted(rng.sample(range(n), 2))
        if j - i < 1:
            continue
        vecino = actual[:i] + actual[i:j + 1][::-1] + actual[j + 1:]
        c_vec = longitud(vecino, pts)
        delta = c_vec - costo
        if delta < 0 or rng.random() < math.exp(-delta / max(T, 1e-12)):
            actual, costo = vecino, c_vec
            mejor = min(mejor, costo)
        T *= ALPHA_ENF
    return costo   # costo de la solucion final (sensible a la temperatura)


# ---------- Experimento ----------
filas = []
for n in TAMANOS:
    pts = crear_instancia(n)
    for nombre, T0 in NIVELES.items():
        for rep in range(REPLICAS):
            semilla = MATRICULA * 1000 + n * 100 + list(NIVELES).index(nombre) * 10 + rep
            filas.append({"tamano": n, "nivel": nombre, "temperatura": round(T0, 3),
                          "rep": rep, "costo": recocido(pts, T0, semilla)})
df = pd.DataFrame(filas)
df.to_csv("resultados.csv", index=False)

# ---------- ANOVA de dos factores ----------
modelo = ols("costo ~ C(temperatura) * C(tamano)", data=df).fit()
anova = sm.stats.anova_lm(modelo, typ=2)
print("\nANOVA dos factores:\n", anova)
anova.to_csv("anova.csv")

# ANOVA por tamano (bloque): efecto de la temperatura dentro de cada n
signif_por_n = {}
for n in TAMANOS:
    sub = df[df.tamano == n]
    if sub.costo.nunique() == 1:     # sin variacion (p. ej. n=5 todos hallan el optimo)
        signif_por_n[n] = (float("nan"), False)
        continue
    a = sm.stats.anova_lm(ols("costo ~ C(temperatura)", data=sub).fit(), typ=2)
    p = a.loc["C(temperatura)", "PR(>F)"]
    signif_por_n[n] = (p, p < ALFA)
    print(f"n={n}: p(temperatura) = {p:.4f}")


# ---------- Bootstrap de la mediana ----------
def boot_mediana(x, rng=np.random.default_rng(MATRICULA)):
    x = np.asarray(x)
    meds = np.median(rng.choice(x, size=(N_BOOT, len(x)), replace=True), axis=1)
    return np.median(meds), np.percentile(meds, 2.5), np.percentile(meds, 97.5)


resumen = []
for n in TAMANOS:
    p, sig = signif_por_n[n]
    cand = []
    for nombre, T0 in NIVELES.items():
        x = df[(df.tamano == n) & (df.nivel == nombre)].costo
        med, lo, hi = boot_mediana(x)
        cand.append((nombre, T0, med, lo, hi))
    mejor = min(cand, key=lambda c: c[2])
    resumen.append({"n": n, "p_temperatura": p, "significativo": sig,
                    "T_optima": round(mejor[1], 2), "nivel": mejor[0],
                    "mediana_boot": round(mejor[2], 3),
                    "IC95_inf": round(mejor[3], 3), "IC95_sup": round(mejor[4], 3)})
tabla = pd.DataFrame(resumen)
print("\nTabla resumen:\n", tabla.to_string(index=False))
tabla.to_csv("tabla_resumen.csv", index=False)

# ---------- Graficas ----------
orden = list(NIVELES)
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
m_t = df.groupby("nivel").costo.mean().reindex(orden)
ax[0].plot([f"{k}\n({NIVELES[k]:.1f})" for k in orden], m_t.values, "o-")
ax[0].set(title="Efecto principal: temperatura", ylabel="Costo medio")
m_n = df.groupby("tamano").costo.mean()
ax[1].plot(m_n.index.astype(str), m_n.values, "o-")
ax[1].set(title="Efecto principal: tamano (n)", xlabel="n")
plt.tight_layout(); plt.savefig("efectos_principales.png", dpi=150); plt.close()

# Interaccion (costo normalizado por la media de cada n para poder compararlas)
plt.figure(figsize=(6, 4))
for n in TAMANOS:
    m = df[df.tamano == n].groupby("nivel").costo.mean().reindex(orden)
    plt.plot(orden, m.values, "o-", label=f"n={n}")
plt.title("Interaccion temperatura x tamano"); plt.ylabel("Costo medio")
plt.legend(); plt.tight_layout(); plt.savefig("interaccion.png", dpi=150); plt.close()

# Medianas bootstrap con IC por punto de diseno
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
for a_, n in zip(ax, TAMANOS):
    for k, nombre in enumerate(orden):
        med, lo, hi = boot_mediana(df[(df.tamano == n) & (df.nivel == nombre)].costo)
        a_.errorbar(k, med, yerr=[[med - lo], [hi - med]], fmt="o", capsize=4)
    a_.set_xticks(range(3)); a_.set_xticklabels(orden); a_.set_title(f"n={n}")
ax[0].set_ylabel("Mediana bootstrap (IC 95%)")
plt.tight_layout(); plt.savefig("bootstrap_medianas.png", dpi=150); plt.close()
