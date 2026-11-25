"""Consulta a Gemini con cada imagen y guarda TODAS las salidas en data/salidas.csv.

Es reanudable: si se corta (límite diario, sin internet), al volver a ejecutarlo
salta las consultas ya registradas.

Uso:
  python src/consultar_modelo.py --fase piloto --reps 1
  python src/consultar_modelo.py --fase final  --reps 3
Requiere .env con GEMINI_API_KEY (ver .env.example).
"""
import argparse
import csv
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
REFS = RAIZ / "data" / "referencias.csv"
SALIDAS = RAIZ / "data" / "salidas.csv"
CAMPOS = ["fase", "familia", "variante", "repeticion", "archivo", "modelo_pedido", "modelo_version",
          "temperatura", "respuesta_cruda", "segundos", "fecha", "error"]

PROMPT = ("Observa la imagen y responde la pregunta. {pregunta}\n"
          "Responde únicamente con el número, sin unidades, sin separadores de miles y sin explicación.")
TEMPERATURA = 1.0  # valor por defecto del servicio: se repite 3 veces para medir variación


def ya_hechas():
    if not SALIDAS.exists():
        return set()
    df = pd.read_csv(SALIDAS)
    df = df[df["error"].isna()]
    return set(zip(df.fase, df.familia, df.variante, df.repeticion))


def anexar(fila: dict):
    nuevo = not SALIDAS.exists()
    with open(SALIDAS, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        w.writerow(fila)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", choices=["piloto", "final"], required=True)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--pausa", type=float, default=7.0, help="segundos entre consultas (límite por minuto)")
    ap.add_argument("--max", type=int, default=0, help="máximo de consultas en esta ejecución (0 = todas)")
    args = ap.parse_args()

    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise SystemExit("Falta GEMINI_API_KEY en .env (copia .env.example como .env y pega tu clave).")
    modelo = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    from google import genai
    from google.genai import types
    cliente = genai.Client(api_key=clave)

    refs = pd.read_csv(REFS)
    refs = refs[refs.fase == args.fase]
    hechas = ya_hechas()
    pendientes = [(r, k) for k in range(1, args.reps + 1) for r in refs.itertuples()
                  if (r.fase, r.familia, r.variante, k) not in hechas]
    if args.max:
        pendientes = pendientes[: args.max]
    print(f"Modelo: {modelo} | pendientes: {len(pendientes)}")

    for i, (r, rep) in enumerate(pendientes, 1):
        img = (RAIZ / r.archivo).read_bytes()
        fila = dict(fase=r.fase, familia=r.familia, variante=r.variante, repeticion=rep, archivo=r.archivo,
                    modelo_pedido=modelo, temperatura=TEMPERATURA, fecha=datetime.now().isoformat(timespec="seconds"),
                    modelo_version="", respuesta_cruda="", segundos="", error="")
        for intento in range(4):
            try:
                t0 = time.perf_counter()
                resp = cliente.models.generate_content(
                    model=modelo,
                    contents=[types.Part.from_bytes(data=img, mime_type="image/png"),
                              PROMPT.format(pregunta=r.pregunta)],
                    config=types.GenerateContentConfig(temperature=TEMPERATURA),
                )
                fila["segundos"] = round(time.perf_counter() - t0, 2)
                fila["respuesta_cruda"] = (resp.text or "").strip()
                fila["modelo_version"] = getattr(resp, "model_version", "") or ""
                fila["error"] = ""
                break
            except Exception as e:  # límite de cuota u otro fallo: esperar y reintentar
                fila["error"] = f"{type(e).__name__}: {str(e)[:150]}"
                espera = 30 * (2 ** intento)
                print(f"  ! {r.familia}_{r.variante} rep{rep}: {fila['error']} -> espero {espera}s")
                if "PerDay" in str(e) or "per day" in str(e).lower():
                    anexar(fila)
                    raise SystemExit("Límite diario alcanzado. Vuelve a ejecutar mañana: el script continúa donde quedó.")
                time.sleep(espera)
        anexar(fila)
        print(f"[{i}/{len(pendientes)}] {r.familia}_{r.variante} rep{rep} -> {fila['respuesta_cruda']!r} "
              f"(ref {r.respuesta_ref})")
        time.sleep(args.pausa)


if __name__ == "__main__":
    main()
