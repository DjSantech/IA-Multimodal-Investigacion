"""Genera el conjunto de imágenes (gráficos de barras y tablas) con datos conocidos.

Cada "familia" tiene unos datos fijos y se dibuja en 5 presentaciones:
  clara            -> referencia (condición A)
  escala           -> barras: eje Y truncado / tablas: separador de miles y fuente pequeña
  reordenada       -> categorías/filas en otro orden y otros colores
  distractor       -> línea de meta, textos con otros números, cuadrícula densa / columna Total
  datos_cambiados  -> CONTROL: cambia el valor preguntado (la referencia se recalcula)

Las 4 primeras tienen los MISMOS datos: la respuesta correcta no debería cambiar.
Uso:  python src/generar_dataset.py
Salida: data/imagenes/<fase>/*.png  y  data/referencias.csv
"""
from pathlib import Path
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DIR_IMG = RAIZ / "data" / "imagenes"
SEMILLA = 2026
TOLERANCIA_BARRAS = 3  # unidades del eje (escala 0-100): ±3 se considera lectura correcta

TEMAS_BARRAS = [
    ("Ventas de frutas", "Ventas (miles de unidades)", ["Mango", "Banano", "Fresa", "Lulo", "Mora", "Guayaba", "Piña"]),
    ("Visitantes por ciudad", "Visitantes (miles)", ["Pereira", "Manizales", "Armenia", "Cali", "Medellín", "Bogotá", "Ibagué"]),
    ("Uso de lenguajes", "Proyectos", ["Python", "Java", "C++", "JavaScript", "Go", "Rust", "Kotlin"]),
    ("Asistencia por deporte", "Asistentes", ["Fútbol", "Tenis", "Natación", "Ciclismo", "Voleibol", "Atletismo", "Ajedrez"]),
    ("Consumo por electrodoméstico", "Consumo (kWh)", ["Nevera", "Lavadora", "Horno", "Televisor", "Ducha", "Plancha", "Microondas"]),
    ("Préstamos por facultad", "Libros prestados", ["Ingeniería", "Medicina", "Artes", "Educación", "Ciencias", "Economía", "Derecho"]),
]
TEMAS_TABLAS = [
    ("Ventas por sede (unidades)", ["Centro", "Norte", "Sur", "Oriente", "Occidente", "Cuba", "Dosquebradas"], ["Ene", "Feb", "Mar"]),
    ("Pasajeros por ruta", ["Ruta 1", "Ruta 2", "Ruta 3", "Ruta 4", "Ruta 5", "Ruta 6", "Ruta 7"], ["Lun", "Mié", "Vie"]),
    ("Producción por planta (kg)", ["Planta A", "Planta B", "Planta C", "Planta D", "Planta E", "Planta F"], ["T1", "T2", "T3"]),
    ("Matrículas por programa", ["Sistemas", "Industrial", "Eléctrica", "Mecánica", "Física", "Química", "Civil"], ["2024", "2025", "2026"]),
]

VARIANTES = ["clara", "escala", "reordenada", "distractor", "datos_cambiados"]


def _guardar(fig, ruta: Path):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------- BARRAS
def dibujar_barras(cats, vals, titulo, ylabel, variante, rng, ruta):
    fig, ax = plt.subplots(figsize=(6.4, 4))
    orden = list(range(len(cats)))
    colores = ["#4C72B0"] * len(cats)
    if variante == "reordenada":
        while orden == list(range(len(cats))):
            rng.shuffle(orden)
        colores = [plt.cm.tab10(i) for i in range(len(cats))]
    c = [cats[i] for i in orden]
    v = [vals[i] for i in orden]
    ax.bar(c, v, color=colores, edgecolor="black", linewidth=0.5, zorder=3)
    ax.set_title(titulo, fontsize=12)
    ax.set_ylabel(ylabel)

    if variante == "escala":
        inferior = max(0, (min(vals) - rng.randint(4, 9)) // 5 * 5)
        ax.set_ylim(inferior, max(vals) + 6)
        ax.set_yticks(range(inferior, int(max(vals)) + 7, 5))
    else:
        ax.set_ylim(0, 100)
        ax.set_yticks(range(0, 101, 10))
    ax.grid(axis="y", alpha=0.4, zorder=0)

    if variante == "distractor":
        ax.set_yticks(range(0, 101, 2), minor=True)
        ax.grid(axis="y", which="minor", alpha=0.25, zorder=0)
        meta = rng.choice([x for x in range(20, 92) if all(abs(x - y) >= 8 for y in vals)] or [50])
        ax.axhline(meta, ls="--", color="red", lw=1.5, zorder=4)
        ax.text(len(cats) - 0.5, meta + 1.5, f"Meta: {meta}", color="red", ha="right", fontsize=9)
        prom_sector = rng.randint(15, 95)
        ax.text(0.02, 0.97, f"Promedio del sector: {prom_sector}\nAño anterior: {rng.randint(15, 95)}",
                transform=ax.transAxes, va="top", fontsize=8,
                bbox=dict(boxstyle="round", fc="lightyellow", ec="gray"))

    plt.setp(ax.get_xticklabels(), rotation=30 if variante == "reordenada" else 0, fontsize=9)
    _guardar(fig, ruta)


# ----------------------------------------------------------------- TABLAS
def _fmt_miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def dibujar_tabla(filas, cols, datos, titulo, variante, rng, ruta):
    filas_o, cols_o = list(filas), list(cols)
    if variante == "reordenada":
        while filas_o == list(filas):
            rng.shuffle(filas_o)
        cols_o = cols_o[::-1]
    cuerpo, encabezado = [], ["Categoría"] + cols_o
    for f in filas_o:
        fila = [datos[(f, c)] for c in cols_o]
        if variante == "escala":
            celdas = [_fmt_miles(x) for x in fila]
        else:
            celdas = [str(x) for x in fila]
        if variante == "distractor":
            celdas.append(str(sum(fila)))
        cuerpo.append([f] + celdas)
    if variante == "distractor":
        encabezado.append("Total")
        prom = [round(sum(datos[(f, c)] for f in filas_o) / len(filas_o)) for c in cols_o]
        cuerpo.append(["Promedio"] + [str(p) for p in prom] + [str(sum(prom))])

    fig, ax = plt.subplots(figsize=(6.4, 0.45 * (len(cuerpo) + 2)))
    ax.axis("off")
    ax.set_title(titulo, fontsize=12)
    anchos = [0.26] + [0.74 / (len(encabezado) - 1)] * (len(encabezado) - 1)
    tabla = ax.table(cellText=cuerpo, colLabels=encabezado, colWidths=anchos, loc="center", cellLoc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(7 if variante == "escala" else 10)
    tabla.scale(1, 1.35)
    for (r, _c), celda in tabla.get_celld().items():
        if r == 0:
            celda.set_text_props(weight="bold")
            celda.set_facecolor("#DDE6F2")
        elif variante == "distractor" and r % 2 == 0:
            celda.set_facecolor("#F2F2F2")
    if variante == "distractor":
        fig.text(0.5, 0.02, f"*Meta trimestral por sede: {_fmt_miles(rng.randint(1000, 9999))}",
                 ha="center", fontsize=8, style="italic")
    _guardar(fig, ruta)


# ----------------------------------------------------------------- GENERACIÓN
def generar(fase: str, n_barras: int, n_tablas: int, rng: random.Random, inicio: int):
    registros = []
    pref = "P" if fase == "piloto" else "F"
    num = inicio
    for i in range(n_barras):
        titulo, ylabel, pool = TEMAS_BARRAS[i % len(TEMAS_BARRAS)]
        cats = rng.sample(pool, 5)
        vals = [rng.choice([x for x in range(28, 95) if x % 10 != 0]) for _ in cats]
        obj = rng.randrange(5)
        fam = f"{pref}{num:02d}"
        num += 1
        for var in VARIANTES:
            v = list(vals)
            if var == "datos_cambiados":
                delta = rng.choice([-1, 1]) * rng.randint(12, 20)
                if not 5 <= v[obj] + delta <= 98:
                    delta = -delta
                v[obj] += delta
            ruta = DIR_IMG / fase / f"{fam}_{var}.png"
            dibujar_barras(cats, v, titulo, ylabel, var, rng, ruta)
            registros.append(dict(
                fase=fase, familia=fam, tipo="barras", variante=var,
                archivo=ruta.relative_to(RAIZ).as_posix(),
                pregunta=f"En el gráfico, ¿qué valor tiene la categoría «{cats[obj]}»?",
                respuesta_ref=v[obj], tolerancia=TOLERANCIA_BARRAS,
                mismos_datos=var != "datos_cambiados"))
    for i in range(n_tablas):
        titulo, pool_f, cols = TEMAS_TABLAS[i % len(TEMAS_TABLAS)]
        filas = rng.sample(pool_f, 5)
        datos = {(f, c): rng.randint(1000, 9999) for f in filas for c in cols}
        f_obj, c_obj = rng.choice(filas), rng.choice(cols)
        fam = f"{pref}{num:02d}"
        num += 1
        for var in VARIANTES:
            d = dict(datos)
            if var == "datos_cambiados":
                delta = rng.choice([-1, 1]) * rng.randint(300, 900)
                if not 1000 <= d[(f_obj, c_obj)] + delta <= 9999:
                    delta = -delta
                d[(f_obj, c_obj)] += delta
            ruta = DIR_IMG / fase / f"{fam}_{var}.png"
            dibujar_tabla(filas, cols, d, titulo, var, rng, ruta)
            registros.append(dict(
                fase=fase, familia=fam, tipo="tabla", variante=var,
                archivo=ruta.relative_to(RAIZ).as_posix(),
                pregunta=f"En la tabla, ¿qué valor tiene «{f_obj}» en la columna «{c_obj}»?",
                respuesta_ref=d[(f_obj, c_obj)], tolerancia=0,
                mismos_datos=var != "datos_cambiados"))
    return registros


def main():
    rng = random.Random(SEMILLA)
    regs = generar("piloto", n_barras=4, n_tablas=2, rng=rng, inicio=1)
    regs += generar("final", n_barras=12, n_tablas=8, rng=rng, inicio=1)
    df = pd.DataFrame(regs)
    df.to_csv(RAIZ / "data" / "referencias.csv", index=False, encoding="utf-8")
    print(df.groupby(["fase", "tipo"]).familia.nunique().rename("familias").to_string())
    print(f"Total imágenes: {len(df)}  ->  {DIR_IMG}")


if __name__ == "__main__":
    main()
