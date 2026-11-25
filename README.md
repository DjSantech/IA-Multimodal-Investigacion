# IA Multimodal · ¿Lee bien Gemini los gráficos y tablas?

Proyecto de investigación del curso de Inteligencia Artificial (Tema 07: IA multimodal).

**Pregunta:** ¿un modelo multimodal (Gemini) lee correctamente valores de gráficos de barras y tablas, y mantiene la lectura cuando solo cambia la presentación (eje truncado, orden, distractores)?

**Entregable:** [`IA_Investigacion_GrupoXX_Tema07.ipynb`](IA_Investigacion_GrupoXX_Tema07.ipynb)

## Estructura
```
src/generar_dataset.py    crea 130 imágenes con datos conocidos + data/referencias.csv
src/consultar_modelo.py   consulta a Gemini y guarda todas las salidas (reanudable)
src/evaluar.py            puntúa, tablas y figura en results/<fase>/
data/imagenes/            piloto/ (6 familias) y final/ (20 familias × 5 variantes)
docs/                     fuentes candidatas y tareas
```

## Cómo ejecutar
```bash
pip install -r requirements.txt
cp .env.example .env            # pegar GEMINI_API_KEY (https://aistudio.google.com/apikey)
python src/generar_dataset.py   # ya están generadas; regenerar da lo mismo (semilla fija)
python src/consultar_modelo.py --fase piloto --reps 1
python src/evaluar.py --fase piloto
python src/consultar_modelo.py --fase final --reps 3
python src/evaluar.py --fase final
```
La clave **nunca** se sube: `.env` está en `.gitignore`.

## Cómo colaborar (Januar)
1. Aceptar la invitación (correo o https://github.com/notifications).
2. Clonar y crear una rama por tarea:
   ```bash
   git clone https://github.com/DjSantech/IA-Multimodal-Investigacion.git
   cd IA-Multimodal-Investigacion
   git checkout -b januar/fuentes
   # ...editar...
   git add -A && git commit -m "Sección C: fuentes F1-F5"
   git push -u origin januar/fuentes
   ```
3. En GitHub, abrir un **Pull Request** hacia `main`; Santiago lo revisa y lo une.
4. Antes de empezar otra tarea: `git checkout main && git pull`.

Tareas: [docs/TAREAS_JANUAR.md](docs/TAREAS_JANUAR.md)

## División del trabajo
| Santiago | Januar |
|---|---|
| Diseño experimental, generador de imágenes, consultas al modelo, evaluación, figura, análisis (B, D, F, G) | Revisión de fuentes (C), motivación (A), verificación manual de referencias, clasificación de fallos, bitácora (E) |
| Exposición: método, resultados, demostración | Exposición: problema, fundamentos, conclusión |

## Uso de IA
Usamos Claude (Anthropic) como asistente para el diseño del protocolo, el código y borradores de redacción; todo fue revisado y ejecutado por nosotros. Gemini es el **objeto de estudio**. Detalle en la sección H del cuaderno.
