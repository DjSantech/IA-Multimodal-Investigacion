"""Genera el conjunto de imágenes (gráficos de barras y tablas) con datos conocidos. Protocolo v2.

Cada "familia" tiene unos datos fijos y se dibuja en 6 presentaciones:
  clara            -> referencia (condición A): estilo por defecto, sin cuadrícula
  escala           -> barras: eje Y truncado / tablas: separador de miles y letra pequeña
  reordenada       -> categorías/filas en otro orden y otros colores
  distractor       -> línea de meta, cuadro con otros números y flecha con % sobre la barra / columna Total
  baja_resolucion  -> la versión clara guardada con ~40 % de los píxeles
  datos_cambiados  -> CONTROL: cambia el valor preguntado (la referencia se recalcula)

Las 5 primeras tienen los MISMOS datos: la respuesta correcta no debería cambiar.
v1 -> v2 (tras el piloto v1 con 30/30 aciertos, efecto techo): 7 barras sin cuadrícula y marcas cada 20,
tablas de 8x4, distractor con flecha sobre la barra objetivo y nueva variante de baja resolución.

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
DPI_NORMAL, DPI_BAJA = 110, 62
N_BARRAS, N_FILAS = 7, 8

TEMAS_BARRAS = [
    ("Ventas de frutas", "Ventas (miles de unidades)",
     ["Mango", "Banano", "Fresa", "Lulo", "Mora", "Guayaba", "Piña", "Uva", "Papaya"]),
    ("Visitantes por ciudad", "Visitantes (miles)",
     ["Pereira", "Manizales", "Armenia", "Cali", "Medellín", "Bogotá", "Ibagué", "Neiva", "Tunja"]),
    ("Uso de lenguajes", "Proyectos",
     ["Python", "Java", "C++", "JavaScript", "Go", "Rust", "Kotlin", "Swift", "PHP"]),
    ("Asistencia por deporte", "Asistentes",
     ["Fútbol", "Tenis", "Natación", "Ciclismo", "Voleibol", "Atletismo", "Ajedrez", "Rugby", "Judo"]),
    ("Consumo por electrodoméstico", "Consumo (kWh)",
     ["Nevera", "Lavadora", "Horno", "Televisor", "Ducha", "Plancha", "Microondas", "Licuadora", "Secador"]),
    ("Préstamos por facultad", "Libros prestados",
     ["Ingeniería", "Medicina", "Artes", "Educación", "Ciencias", "Economía", "Derecho", "Idiomas", "Música"]),
]
TEMAS_TABLAS = [
    ("Ventas por sede (unidades)",
     ["Centro", "Norte", "Sur", "Oriente", "Occidente", "Cuba", "Dosquebradas", "La Virginia", "Santa Rosa"],
     ["Ene", "Feb", "Mar", "Abr"]),
    ("Pasajeros por ruta",
     ["Ruta 1", "Ruta 2", "Ruta 3", "Ruta 4", "Ruta 5", "Ruta 6", "Ruta 7", "Ruta 8", "Ruta 9"],
     ["Lun", "Mar", "Mié", "Jue"]),
    ("Producción por planta (kg)",
     ["Planta A", "Planta B", "Planta C", "Planta D", "Planta E", "Planta F", "Planta G", "Planta H", "Planta I"],
     ["T1", "T2", "T3", "T4"]),
    ("Matrículas por programa",
     ["Sistemas", "Industrial", "Eléctrica", "Mecánica", "Física", "Química", "Civil", "Ambiental", "Música"],
     ["2023", "2024", "2025", "2026"]),
]

VARIANTES = ["clara", "escala", "reordenada", "distractor", "baja_resolucion", "datos_cambiados"]


def _guardar(fig, ruta: Path, variante: str):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    dpi = {"baja_resolucion": DPI_BAJA, "res_40": 40, "res_30": 30}.get(variante, DPI_NORMAL)
    fig.savefig(ruta, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------- BARRAS
def dibujar_barras(cats, vals, obj, titulo, ylabel, variante, rng, ruta):
    fig, ax = plt.subplots(figsize=(6.8, 4))
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
    ax.spines[["top", "right"]].set_visible(False)

    if variante in ("escala", "proporcion_truncada"):  # eje truncado: no empieza en 0
        inferior = max(10, (min(vals) - rng.randint(4, 9)) // 10 * 10)
        ax.set_ylim(inferior, 100)
        ax.set_yticks(range(inferior, 101, 10))
    else:
        ax.set_ylim(0, 100)
        ax.set_yticks(range(0, 101, 20))

    if variante == "distractor":
        meta = rng.choice([x for x in range(20, 92) if all(abs(x - y) >= 8 for y in vals)] or [50])
        ax.axhline(meta, ls="--", color="red", lw=1.5, zorder=4)
        ax.text(len(cats) - 0.5, meta + 1.5, f"Meta: {meta}", color="red", ha="right", fontsize=9)
        ax.text(0.02, 0.97, f"Promedio del sector: {rng.randint(15, 95)}\nAño anterior: {rng.randint(15, 95)}",
                transform=ax.transAxes, va="top", fontsize=8,
                bbox=dict(boxstyle="round", fc="lightyellow", ec="gray"))
        x_obj = orden.index(obj)
        pct = rng.choice([-1, 1]) * rng.randint(8, 35)
        ax.annotate(f"{pct:+d} %", xy=(x_obj, vals[obj]), xytext=(x_obj + 0.35, min(vals[obj] + 14, 97)),
                    fontsize=10, color="#B00020", weight="bold",
                    arrowprops=dict(arrowstyle="->", color="#B00020"))

    plt.setp(ax.get_xticklabels(), rotation=30 if variante == "reordenada" else 0, fontsize=8)
    _guardar(fig, ruta, variante)


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
        celdas = [_fmt_miles(x) for x in fila] if variante == "escala" else [str(x) for x in fila]
        if variante == "distractor":
            celdas.append(str(sum(fila)))
        cuerpo.append([f] + celdas)
    if variante == "distractor":
        encabezado.append("Total")
        prom = [round(sum(datos[(f, c)] for f in filas_o) / len(filas_o)) for c in cols_o]
        cuerpo.append(["Promedio"] + [str(p) for p in prom] + [str(sum(prom))])

    fig, ax = plt.subplots(figsize=(6.8, 0.42 * (len(cuerpo) + 2)))
    ax.axis("off")
    ax.set_title(titulo, fontsize=12)
    anchos = [0.24] + [0.76 / (len(encabezado) - 1)] * (len(encabezado) - 1)
    tabla = ax.table(cellText=cuerpo, colLabels=encabezado, colWidths=anchos, loc="center", cellLoc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(7 if variante == "escala" else 10)
    tabla.scale(1, 1.3)
    for (r, _c), celda in tabla.get_celld().items():
        if r == 0:
            celda.set_text_props(weight="bold")
            celda.set_facecolor("#DDE6F2")
        elif variante == "distractor" and r % 2 == 0:
            celda.set_facecolor("#F2F2F2")
    if variante == "distractor":
        fig.text(0.5, 0.01, f"*Meta por periodo: {_fmt_miles(rng.randint(1000, 9999))}",
                 ha="center", fontsize=8, style="italic")
    _guardar(fig, ruta, variante)


# ----------------------------------------------------------------- GENERACIÓN
def generar(fase: str, n_barras: int, n_tablas: int, rng: random.Random, inicio: int):
    registros = []
    pref = "P" if fase == "piloto" else "F"
    num = inicio
    for i in range(n_barras):
        titulo, ylabel, pool = TEMAS_BARRAS[i % len(TEMAS_BARRAS)]
        cats = rng.sample(pool, N_BARRAS)
        vals = [rng.choice([x for x in range(28, 95) if x % 10 != 0]) for _ in cats]
        obj = rng.randrange(N_BARRAS)
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
            dibujar_barras(cats, v, obj, titulo, ylabel, var, rng, ruta)
            registros.append(dict(
                fase=fase, familia=fam, tipo="barras", variante=var,
                archivo=ruta.relative_to(RAIZ).as_posix(),
                pregunta=f"En el gráfico, ¿qué valor tiene la categoría «{cats[obj]}»?",
                respuesta_ref=v[obj], tolerancia=TOLERANCIA_BARRAS,
                mismos_datos=var != "datos_cambiados"))
    for i in range(n_tablas):
        titulo, pool_f, cols = TEMAS_TABLAS[i % len(TEMAS_TABLAS)]
        filas = rng.sample(pool_f, N_FILAS)
        datos = {(f, c): rng.randint(1000, 9999) for f in filas for c in cols}
        f_obj, c_obj = rng.choice(filas[1:-1]), rng.choice(cols[1:-1])  # celda interior
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


def generar_estres(rng: random.Random, n_barras=10, n_tablas=6):
    """Exploración adicional (separada del estudio principal): busca dónde falla el modelo.
    - proporcion_clara / proporcion_truncada: '¿cuántas veces es mayor A que B?' con eje desde 0 o truncado
      (el eje truncado exagera visualmente la diferencia: engaño clásico, Tonglet et al. 2025).
    - res_40 / res_30: versión clara con resolución extrema.
    """
    registros, fase = [], "estres"
    for i in range(n_barras):
        titulo, ylabel, pool = TEMAS_BARRAS[i % len(TEMAS_BARRAS)]
        cats = rng.sample(pool, N_BARRAS)
        while True:
            vals = [rng.choice([x for x in range(28, 95) if x % 10 != 0]) for _ in cats]
            a, b = rng.sample(range(N_BARRAS), 2)
            if vals[a] < vals[b]:
                a, b = b, a
            if 1.2 <= vals[a] / vals[b] <= 2.6:
                break
        fam = f"E{i + 1:02d}"
        for var in ["proporcion_clara", "proporcion_truncada", "res_40", "res_30"]:
            ruta = DIR_IMG / fase / f"{fam}_{var}.png"
            dibujar_barras(cats, vals, a, titulo, ylabel, var, rng, ruta)
            if var.startswith("proporcion"):
                preg = f"En el gráfico, ¿cuántas veces es mayor el valor de «{cats[a]}» que el de «{cats[b]}»?"
                ref, tol = round(vals[a] / vals[b], 2), 0.1
            else:
                preg = f"En el gráfico, ¿qué valor tiene la categoría «{cats[a]}»?"
                ref, tol = vals[a], TOLERANCIA_BARRAS
            registros.append(dict(fase=fase, familia=fam, tipo="barras", variante=var,
                                  archivo=ruta.relative_to(RAIZ).as_posix(), pregunta=preg,
                                  respuesta_ref=ref, tolerancia=tol, mismos_datos=False))
    for i in range(n_tablas):
        titulo, pool_f, cols = TEMAS_TABLAS[i % len(TEMAS_TABLAS)]
        filas = rng.sample(pool_f, N_FILAS)
        datos = {(f, c): rng.randint(1000, 9999) for f in filas for c in cols}
        f_obj, c_obj = rng.choice(filas[1:-1]), rng.choice(cols[1:-1])
        fam = f"E{n_barras + i + 1:02d}"
        for var in ["res_40", "res_30"]:
            ruta = DIR_IMG / fase / f"{fam}_{var}.png"
            dibujar_tabla(filas, cols, datos, titulo, var, rng, ruta)
            registros.append(dict(fase=fase, familia=fam, tipo="tabla", variante=var,
                                  archivo=ruta.relative_to(RAIZ).as_posix(),
                                  pregunta=f"En la tabla, ¿qué valor tiene «{f_obj}» en la columna «{c_obj}»?",
                                  respuesta_ref=datos[(f_obj, c_obj)], tolerancia=0, mismos_datos=False))
    return registros


def main():
    import sys
    destino = RAIZ / "data" / "referencias.csv"
    estres = generar_estres(random.Random(SEMILLA + 1))  # generador propio: no altera el estudio principal
    if "--solo-estres" in sys.argv:
        previo = pd.read_csv(destino)
        df = pd.concat([previo[previo.fase != "estres"], pd.DataFrame(estres)], ignore_index=True)
    else:
        rng = random.Random(SEMILLA)
        regs = generar("piloto", n_barras=4, n_tablas=2, rng=rng, inicio=1)
        regs += generar("final", n_barras=12, n_tablas=8, rng=rng, inicio=1)
        df = pd.DataFrame(regs + estres)
    df.to_csv(destino, index=False, encoding="utf-8")
    print(df.groupby(["fase", "tipo"]).familia.nunique().rename("familias").to_string())
    print(f"Total imágenes: {len(df)}  ->  {DIR_IMG}")


if __name__ == "__main__":
    main()
