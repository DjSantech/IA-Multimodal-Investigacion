"""Puntúa las salidas del modelo y produce tablas + figura.

Uso:  python src/evaluar.py --fase final      (o --fase piloto)
Salida (results/<fase>/):
  puntajes.csv            una fila por consulta, con valor leído, acierto y error
  resumen_variantes.csv   aciertos/n por tipo y variante (tabla principal)
  resumen.json            cifras clave (para el cuaderno y la exposición)
  acierto_por_variante.png
y data/etiquetas_fallos.csv (plantilla para clasificar fallos a mano; no se sobrescribe).
"""
import argparse
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORDEN = ["clara", "escala", "reordenada", "distractor", "datos_cambiados"]
NOMBRES = {"clara": "Clara\n(referencia)", "escala": "Escala /\nformato", "reordenada": "Reordenada",
           "distractor": "Distractor", "datos_cambiados": "Datos\ncambiados*"}
COLOR = {"barras": "#257de0", "tabla": "#f47230"}
TIPOS_FALLO = "lectura_escala | confusion_categoria | distractor | ocr_digito | formato_numero | sin_numero | otro"


def leer_numero(texto, tipo):
    """Extrae el primer número de la respuesta. Tablas: entero (se quitan separadores)."""
    if not isinstance(texto, str):
        return None
    m = re.search(r"-?\d[\d.,]*", texto)
    if not m:
        return None
    s = m.group().rstrip(".,")
    if tipo == "tabla":
        return float(re.sub(r"[.,]", "", s))
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    s = s.replace(",", "")
    if s.count(".") > 1:
        s = s.replace(".", "")
    return float(s)


def puntuar(fase):
    refs = pd.read_csv(RAIZ / "data" / "referencias.csv")
    sal = pd.read_csv(RAIZ / "data" / "salidas.csv")
    sal = sal[(sal.fase == fase) & sal["error"].isna()]
    df = sal.merge(refs[["fase", "familia", "variante", "tipo", "pregunta", "respuesta_ref", "tolerancia",
                         "mismos_datos"]], on=["fase", "familia", "variante"], how="left")
    df["valor_leido"] = [leer_numero(t, tp) for t, tp in zip(df.respuesta_cruda, df.tipo)]
    df["error_abs"] = (df.valor_leido - df.respuesta_ref).abs()
    df["acierto"] = df.error_abs <= df.tolerancia
    return df


def resumir(df):
    g = df.groupby(["tipo", "variante"])
    res = pd.DataFrame({
        "aciertos": g.acierto.sum().astype(int),
        "n": g.size(),
        "familias": g.familia.nunique(),
        "error_abs_medio": g.error_abs.mean().round(2),
        "sin_numero": g.valor_leido.apply(lambda s: int(s.isna().sum())),
    }).reset_index()
    res["pct_acierto"] = (100 * res.aciertos / res.n).round(1)
    res["variante"] = pd.Categorical(res.variante, ORDEN, ordered=True)
    return res.sort_values(["tipo", "variante"])


def metricas_extra(df):
    m = {}
    # Estabilidad: ¿las repeticiones de la misma imagen dan el mismo valor?
    est = df.groupby(["familia", "variante"]).valor_leido.nunique(dropna=False)
    m["estabilidad_entre_repeticiones_pct"] = round(100 * (est == 1).mean(), 1)
    # Consistencia: en una repetición, ¿acierta las 4 presentaciones con los mismos datos?
    mis = df[df.mismos_datos == True]
    cons = mis.groupby(["familia", "repeticion"]).acierto.agg(["all", "size"])
    cons = cons[cons["size"] == 4]
    m["consistencia_familia_pct"] = round(100 * cons["all"].mean(), 1) if len(cons) else None
    # Control: ¿el valor leído cambia en la dirección correcta cuando los datos cambian?
    cla = df[df.variante == "clara"].set_index(["familia", "repeticion"])
    cam = df[df.variante == "datos_cambiados"].set_index(["familia", "repeticion"])
    j = cla.join(cam, lsuffix="_cla", rsuffix="_cam", how="inner").dropna(subset=["valor_leido_cla", "valor_leido_cam"])
    if len(j):
        signo_real = (j.respuesta_ref_cam - j.respuesta_ref_cla).apply(lambda x: x > 0)
        signo_leido = (j.valor_leido_cam - j.valor_leido_cla).apply(lambda x: x > 0)
        m["control_direccion_correcta_pct"] = round(100 * (signo_real == signo_leido).mean(), 1)
    m["tiempo_medio_s"] = round(df.segundos.mean(), 2)
    m["n_consultas"] = int(len(df))
    m["modelo_version"] = sorted(df.modelo_version.dropna().astype(str).unique().tolist())
    return m


def figura(res, ruta):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ancho = 0.38
    for k, tipo in enumerate(["barras", "tabla"]):
        sub = res[res.tipo == tipo].set_index("variante").reindex(ORDEN)
        xs = [i + (k - 0.5) * ancho for i in range(len(ORDEN))]
        barras = ax.bar(xs, sub.pct_acierto, width=ancho - 0.03, color=COLOR[tipo],
                        label="Gráfico de barras" if tipo == "barras" else "Tabla", zorder=3)
        for b, (a, n) in zip(barras, zip(sub.aciertos, sub.n)):
            if pd.notna(n):
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{int(a)}/{int(n)}",
                        ha="center", fontsize=8, color="#333333")
    ax.set_xticks(range(len(ORDEN)), [NOMBRES[v] for v in ORDEN], fontsize=9)
    ax.set_ylim(0, 110)
    ax.set_ylabel("Acierto (%)")
    ax.set_title("Acierto de Gemini por presentación de la misma información", loc="left", fontsize=11, pad=22)
    ax.grid(axis="y", color="#e0e0e0", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, 0.99), ncol=2, fontsize=9)
    fig.text(0.01, -0.02, "*Control: el valor preguntado sí cambia; la respuesta correcta se recalculó.",
             fontsize=8, color="#555555")
    fig.savefig(ruta, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", choices=["piloto", "final"], default="final")
    args = ap.parse_args()
    out = RAIZ / "results" / args.fase
    out.mkdir(parents=True, exist_ok=True)

    df = puntuar(args.fase)
    if df.empty:
        raise SystemExit("No hay salidas para esta fase. Ejecuta primero src/consultar_modelo.py")
    df.to_csv(out / "puntajes.csv", index=False, encoding="utf-8")
    res = resumir(df)
    res.to_csv(out / "resumen_variantes.csv", index=False, encoding="utf-8")
    m = metricas_extra(df)
    m["acierto_por_variante"] = {f"{r.tipo}/{r.variante}": f"{r.aciertos}/{r.n}" for r in res.itertuples()}
    (out / "resumen.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    figura(res, out / "acierto_por_variante.png")

    if args.fase == "final":
        etiq = RAIZ / "data" / "etiquetas_fallos.csv"
        if not etiq.exists():
            f = df[~df.acierto][["familia", "tipo", "variante", "repeticion", "archivo", "pregunta",
                                  "respuesta_ref", "respuesta_cruda"]].copy()
            f["tipo_fallo"] = ""
            f["nota"] = ""
            f.to_csv(etiq, index=False, encoding="utf-8")
            print(f"Plantilla de fallos creada ({len(f)} filas). Categorías: {TIPOS_FALLO}")

    print(res.to_string(index=False))
    print(json.dumps(m, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
