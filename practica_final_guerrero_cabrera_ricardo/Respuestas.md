# Respuestas — Práctica Final: Análisis y Modelado de Datos

> Rellena cada pregunta con tu respuesta. Cuando se pida un valor numérico, incluye también una breve explicación de lo que significa.

---

## Ejercicio 1 — Análisis Estadístico Descriptivo
---
En este ejercicio se realiza un análisis descriptivo en tres niveles: primero, la caracterización estructural del dataset; segundo, el estudio univariante de las variables numéricas mediante medidas de tendencia central, dispersión y forma; y tercero, el análisis bivariante de la variable objetivo frente a variables categóricas y numéricas relevantes.

La evaluación de distribuciones se apoya en histogramas con curva KDE y en boxplots, mientras que la interpretación cuantitativa se sustenta en media, mediana, desviación típica, varianza, cuartiles e IQR. Además, se incluyen asimetría y curtosis para describir la forma de la distribución de la variable objetivo. Este enfoque permite justificar de forma estadística y transparente las decisiones posteriores de modelado.

**Subapartado: análisis de variables categóricas (frecuencias, gráficos y desbalance)**

Como complemento al análisis numérico, se evaluaron las cuatro variables categóricas detectadas mediante frecuencias absolutas/relativas y gráficos de barras, con el objetivo de comprobar si existe desbalance que pudiera condicionar la interpretación o el modelado posterior.

Resultados principales:
- **Gender:** Male 52.52% (511) y Female 47.48% (462). Distribución prácticamente equilibrada, sin categoría dominante.
- **Workout_Type:** Strength 26.52% (258), Cardio 26.21% (255), Yoga 24.56% (239), HIIT 22.71% (221). Reparto homogéneo entre tipos de entrenamiento.
- **Workout_Frequency (days/week):** 3 días 37.82% (368), 4 días 31.45% (306), 2 días 20.25% (197), 5 días 10.48% (102). Se observa mayor concentración en 3-4 días/semana, aunque sin dominancia extrema.
- **Experience_Level:** nivel 2 = 41.73% (406), nivel 1 = 38.64% (376), nivel 3 = 19.63% (191). Existe menor representación del nivel avanzado, pero dentro de un rango todavía analíticamente usable.

Interpretación de los gráficos de frecuencia:
- Los countplots confirman visualmente la ausencia de picos desproporcionados.
- No aparece ninguna categoría por encima del umbral de desbalance severo (60%), por lo que no hay evidencia de sesgo estructural fuerte.
- La ligera infrarepresentación de Experience_Level = 3 y de Workout_Frequency = 5 sugiere prudencia interpretativa en esos subgrupos, pero no justifica técnicas de corrección en esta fase descriptiva.

Conclusión del subapartado:
En conjunto, las variables categóricas presentan un comportamiento razonablemente balanceado. Por tanto, el análisis descriptivo es estable y no requiere, por ahora, estrategias de remuestreo o ponderación específicas por frecuencia de categoría.

---

**Pregunta 1.1** — ¿De qué fuente proviene el dataset y cuál es la variable objetivo (target)? ¿Por qué tiene sentido hacer regresión sobre ella?

> **Origen del dataset:**
> 
> El dataset proviene de [Kaggle: Gym Members Exercise Dataset](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset), una colección de datos reales sobre miembros de gimnasio y su actividad física. Contiene información detallada y características sobre el entrenamiento de 973 individuos.
> 
> **Características estructurales:**
>
> El dataset cumple con los requisitos especificados:
> - **Número de columnas:** 15 (requisito: 8+)
> - **Tamaño del archivo CSV:** 0.062 MB (requisito: <15 MB)
> - **Número de filas:** 973 observaciones
> - **Variables categóricas:** 4 (Gender, Workout_Type, Experience_Level, Workout_Frequency)
> - **Varibales continuas:** 7 (Weight(kg), Height(m), Session_Duration(h), Calories_Burned, Fat_Percentage, Water_Intake(l), BMI)
> - **Variable objetivo:** 1 (Calories_Burned)
> 
> **Composición de las variables:**
> 
> El dataset incluye 11 variables numéricas (de precisión continua o discreta): Age, Weight, Height, Max_BPM, Avg_BPM, Resting_BPM, Session_Duration, Fat_Percentage, Water_Intake, BMI y la variable objetivo Calories_Burned. Adicionalmente hay 4 variables categóricas:
> - **Gender (str):** Género del miembro (2 categorías)
> - **Workout_Type (str):** Tipo de entrenamiento realizado (cardio, fuerza, etc.)
> - **Experience_Level (int discreto, 1-3 niveles):** Tratada como categórica ordinal (principiante, intermedio, avanzado)
> - **Workout_Frequency (int discreto, 3-7 días/semana):** Días de entrenamiento por semana, tratada como categórica debido a su bajo número de valores únicos
> 
> **Variable objetivo (Target): Calories_Burned**
> 
> La variable objetivo es **Calories_Burned** (float64), que mide el número de calorías quemadas en cada sesión de entrenamiento. Es una variable **continua y no acotada**, lo que la hace ideal para regresión porque:
> 
> 1. **Naturaleza continua:** Puede tomar cualquier valor real positivo, no está restringida a categorías o valores discretos.
> 2. **Relación causal con características:** Existe una relación clara y lógica entre predictores (peso, duración de sesión, tipo de entrenamiento, frecuencia cardíaca) y calorías quemadas, haciendo que los coeficientes de regresión sean interpretables.
> 3. **Variabilidad capturada:** Los regresores disponibles explican una parte significativa de su varianza (especialmente Session_Duration, Weight y tipo de ejercicio).
> 4. **Aplicación práctica:** Predecir calorías quemadas es útil para el diseño de planes de entrenamiento personalizados y seguimiento de objetivos fitness.

**Pregunta 1.2** — ¿Qué distribución tienen las principales variables numéricas y has encontrado outliers? Indica en qué variables y qué has decidido hacer con ellos.

> El análisis descriptivo de las variables numéricas muestra, en términos generales, distribuciones razonablemente estables, con distinta dispersión según la naturaleza de cada variable y sin evidencia de valores extremos problemáticos en la mayoría de los casos.
>
> **1) Estadísticos descriptivos e interpretación por grupos de variables**
>
> **Edad y variables fisiológicas de BPM**
> - **Age:** media 38.6835, mediana 40, desviación típica 12.1809, IQR = 49 - 28 = 21. Se observa una dispersión moderada, con centro claro en torno a 40 años.
> - **Max_BPM:** media 179.8839, mediana 180, desviación típica 11.5257, IQR = 20.
> - **Avg_BPM:** media 143.7667, mediana 143, desviación típica 14.3451, IQR = 25.
> - **Resting_BPM:** media 62.2230, mediana 62, desviación típica 7.3271, IQR = 12.
> 
> En las cuatro variables, media y mediana son muy próximas, lo que sugiere distribuciones cercanas a simétricas y sin sesgos severos. Además, los rangos observados son coherentes con contextos de entrenamiento físico, por lo que no aparecen señales de valores anómalos estructurales.
>
> **Antropometría y composición corporal**
> - **Weight (kg):** media 73.8547, mediana 70, desviación típica 21.2075, IQR = 27.9.
> - **Height (m):** media 1.7226, mediana 1.71, desviación típica 0.1277, IQR = 0.18.
> - **BMI:** media 24.9121, mediana 24.16, desviación típica 6.6609, IQR = 8.45.
> - **Fat_Percentage:** media 24.9768, mediana 26.20, desviación típica 6.2594, IQR = 8.0.
> 
> En peso e IMC se aprecia mayor heterogeneidad entre individuos (desviaciones más altas), algo esperable en una muestra amplia de usuarios de gimnasio con perfiles distintos. Altura presenta menor variabilidad relativa, como era esperable. En grasa corporal, la mediana supera a la media, lo que sugiere un leve sesgo hacia valores bajos en parte de la muestra.
>
> **Carga de entrenamiento y resultado energético**
> - **Session_Duration (hours):** media 1.2564, mediana 1.26, desviación típica 0.3430, IQR = 0.42.
> - **Water_Intake (liters):** media 2.6266, mediana 2.60, desviación típica 0.6002, IQR = 0.90.
> - **Calories_Burned (target):** media 905.4224, mediana 893, desviación típica 272.6415, IQR = 356.
> 
> La duración de sesión y la ingesta de agua muestran variabilidad moderada. La variable objetivo presenta mayor dispersión absoluta (std alta e IQR amplio), lo cual es consistente con la combinación de perfiles físicos y rutinas diferentes.
>
> **2) Forma de la distribución de la variable objetivo**
>
> Para **Calories_Burned**:
> - **IQR:** 356.0000
> - **Asimetría (skewness):** 0.2783
> - **Curtosis:** -0.0560
>
> Interpretación:
> - La asimetría positiva es leve, por lo que la distribución está casi centrada pero con una cola derecha moderada.
> - La curtosis cercana a 0 indica forma próxima a mesocúrtica (similar a una normal en concentración y colas), sin colas extremadamente pesadas.
> - En conjunto, la variable objetivo no presenta una deformación severa y mantiene buena calidad para modelado de regresión.
>
> **3) Lectura de histogramas con KDE**
>
> Los histogramas con KDE confirman lo observado en los estadísticos:
> - **Age, BPM y Height** muestran perfiles bastante equilibrados, sin picos extremos aislados.
> - **Weight y BMI** presentan mayor extensión de la cola derecha, coherente con algunos individuos de mayor masa corporal.
> - **Session_Duration** se concentra alrededor de 1.2-1.4 h, con colas contenidas.
> - **Calories_Burned** tiene forma aproximadamente unimodal, centro alrededor de 850-950 y ligera cola a la derecha.
>
> **4) Boxplots de Calories_Burned por variables categóricas**
>
> Hallazgos más relevantes:
> - **Gender:** distribución relativamente similar entre grupos, con medianas cercanas y ligera diferencia a favor de hombres.
> - **Workout_Type:** las medianas son próximas entre tipos, con cierta ventaja de HIIT/Strength y dispersión comparable.
> - **Workout_Frequency (days/week):** patrón claramente creciente de la mediana al aumentar la frecuencia (2, 3, 4, 5 días), lo que aporta evidencia de relación positiva entre frecuencia semanal y gasto calórico.
> - **Experience_Level:** gradiente muy marcado (1 < 2 < 3) tanto en mediana como en nivel general, indicando que mayor experiencia se asocia con mayor gasto calórico por sesión.
>
> Este último punto es especialmente valioso porque sugiere señal predictiva real en variables categóricas ordinales, no solo en variables continuas.
>
> **5) Detección de outliers y decisión metodológica**
>
> A partir de la forma de las distribuciones (en general cercanas a simétricas y sin colas extremas severas), se optó por **Z-score** para la detección de outliers, ya que resulta coherente cuando la dispersión está bien representada por media y desviación típica.
>
> Resumen de outliers detectados:
> - **BMI:** 10 casos (1.03%), límites [4.9295, 44.8948]
> - **Calories_Burned:** 3 casos (0.31%), límites [87.4979, 1723.3470]
> - **Resto de variables:** 0 casos
>
> **Decisión adoptada:** no se elimina ni transforma ningún outlier.
>
> **Justificación:**
> - El porcentaje detectado es muy bajo (solo 1.03% en BMI y 0.31% en target).
> - Los valores se mantienen dentro de rangos plausibles para población activa de gimnasio.
> - Eliminar esos casos podría reducir variabilidad real y sesgar el modelo hacia perfiles medios, perdiendo capacidad de generalización en usuarios extremos pero reales.
> - Dado que no hay evidencia de error de medición ni ruptura estructural de la distribución, conservarlos aporta más valor analítico que descartarlos.

**Pregunta 1.3** — ¿Qué tres variables numéricas tienen mayor correlación (en valor absoluto) con la variable objetivo? Indica los coeficientes.

> _Escribe aquí tu respuesta_

**Pregunta 1.4** — ¿Hay valores nulos en el dataset? ¿Qué porcentaje representan y cómo los has tratado?

> _Escribe aquí tu respuesta_

---

## Ejercicio 2 — Inferencia con Scikit-Learn

---
Añade aqui tu descripción y analisis:

---

**Pregunta 2.1** — Indica los valores de MAE, RMSE y R² de la regresión lineal sobre el test set. ¿El modelo funciona bien? ¿Por qué?

> _Escribe aquí tu respuesta_


---

## Ejercicio 3 — Regresión Lineal Múltiple en NumPy

---
Añade aqui tu descripción y analisis:

---

**Pregunta 3.1** — Explica en tus propias palabras qué hace la fórmula β = (XᵀX)⁻¹ Xᵀy y por qué es necesario añadir una columna de unos a la matriz X.

> _Escribe aquí tu respuesta_

**Pregunta 3.2** — Copia aquí los cuatro coeficientes ajustados por tu función y compáralos con los valores de referencia del enunciado.

| Parametro | Valor real | Valor ajustado |
|-----------|-----------|----------------|
| β₀        | 5.0       |                |
| β₁        | 2.0       |                |
| β₂        | -1.0      |                |
| β₃        | 0.5       |                |

> _Escribe aquí tu respuesta_

**Pregunta 3.3** — ¿Qué valores de MAE, RMSE y R² has obtenido? ¿Se aproximan a los de referencia?

> _Escribe aquí tu respuesta_

---

## Ejercicio 4 — Series Temporales
---
Añade aqui tu descripción y analisis:

---

**Pregunta 4.1** — ¿La serie presenta tendencia? Descríbela brevemente (tipo, dirección, magnitud aproximada).

> _Escribe aquí tu respuesta_

**Pregunta 4.2** — ¿Hay estacionalidad? Indica el periodo aproximado en días y la amplitud del patrón estacional.

> _Escribe aquí tu respuesta_

**Pregunta 4.3** — ¿Se aprecian ciclos de largo plazo en la serie? ¿Cómo los diferencias de la tendencia?

> _Escribe aquí tu respuesta_

**Pregunta 4.4** — ¿El residuo se ajusta a un ruido ideal? Indica la media, la desviación típica y el resultado del test de normalidad (p-value) para justificar tu respuesta.

> _Escribe aquí tu respuesta_

---

*Fin del documento de respuestas*
