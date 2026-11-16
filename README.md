# Tarea-3-Algoritmia-y-Optimizaci-n
Tarea 3: Ajuste de la temperatura del Recocido Simulado (2-opt, TSP) con Diseño de Experimentos (ANOVA y bootstrap)
# Tarea 3 - Algoritmia y Optimización

## Descripción
Ajuste de la temperatura inicial del Recocido Simulado (2-opt) sobre TSP con n = 5, 10, 15,
mediante un diseño factorial completo 3x3 (Opción A), ANOVA de dos factores y bootstrap de la mediana.

## Cómo ejecutarlo
pip install numpy pandas matplotlib statsmodels reportlab
python doe_recocido.py
python make_pdf.py

## Parámetros
- Semilla de r: matrícula 2095327 (r = 0.3649)
- Rango de temperatura: [0.1, 100]
- Niveles de temperatura: 11.04, 41.01 y 70.97
- 10 réplicas por punto de diseño, 90 corridas en total

## Archivos
- doe_recocido.py: experimento completo (SA, ANOVA, bootstrap, gráficas)
- make_pdf.py: genera el reporte
- resultados.csv, anova.csv, tabla_resumen.csv: resultados
- *.png: gráficas
- DAPR_Tarea3.pdf: reporte final

## Autor
Diego Alejandro Puente Ruiz, matrícula 2095327
