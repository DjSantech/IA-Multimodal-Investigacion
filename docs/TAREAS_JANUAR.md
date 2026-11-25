# Tareas de Januar

Todo se entrega por **rama propia + Pull Request** (así queda evidencia de quién hizo qué; el docente puede preguntarlo).

## Semana 1 · Fuentes (Sección C del cuaderno)
- [ ] Leer 5 fuentes de [fuentes_candidatas.md](fuentes_candidatas.md) (≥ 3 académicas, ≥ 2 de 2025–2026).
- [ ] Llenar la tabla F1–F5 en `IA_Investigacion_GrupoXX_Tema07.ipynb` (sección C): referencia, año, tipo, aporte, limitación.
- [ ] Escribir la **síntesis crítica** (1 párrafo: en qué coinciden, en qué difieren, qué examina nuestro estudio).
- [ ] Escribir la **motivación** (sección A, 3–4 líneas).
- Rama: `januar/fuentes`

## Semana 2 · Verificar la verdad de referencia
- [ ] Abrir 10 imágenes al azar de `data/imagenes/final/` (al menos 3 tablas y 1 de cada variante).
- [ ] Comparar a ojo el valor de la imagen con `respuesta_ref` en `data/referencias.csv`.
- [ ] Registrar en `docs/verificacion_referencias.md`: archivo, valor visto, valor de referencia, ¿coincide?
- Rama: `januar/verificacion`

## Semana 3 · Clasificar los fallos del modelo
- [ ] Abrir `data/etiquetas_fallos_estres.csv` (fallos de la exploración de estrés; la evaluación principal no tuvo fallos), abrir cada imagen fallida y llenar la columna `tipo_fallo` con una de estas categorías:
  `proporcion_visual` (calcula la proporción con la altura dibujada, no con los valores) · `lectura_escala` · `confusion_categoria` · `distractor` · `ocr_digito` · `formato_numero` · `sin_numero` · `otro`
- [ ] Añadir una `nota` corta cuando el fallo sea interesante (candidatos para la exposición).
- [ ] Llenar tu fila de la bitácora (sección E) y tu **reflexión individual** (sección H).
- [ ] Referencias finales en APA (sección H).
- Rama: `januar/fallos`

## Semana 4 · Exposición
- Tú presentas: **Problema**, **Fundamentos** y **Conclusión** (≈ 5 min).
- Ensayo conjunto al menos una vez con cronómetro.
