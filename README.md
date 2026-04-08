# Evolve-estadistica-ricardo-guerrero

Proyecto de análisis estadístico de datos de miembros de gimnasio, desarrollado en Python.

---

## Estructura del proyecto

```
├── data/
│   └── gym_members_exercise_tracking.csv   # Dataset de miembros del gimnasio
├── output/
│   └── matriz_correlacion.png              # Gráfico generado por el script
├── src/
│   ├── analisis_descriptivo.py             # Script principal de análisis
│   └── medidas.py                          # Funciones estadísticas propias
└── requirements.txt                        # Dependencias del proyecto
```

---

## Explicación de `src/analisis_descriptivo.py`

Este script realiza un **Análisis Exploratorio de Datos (EDA)** completo sobre el dataset
`gym_members_exercise_tracking.csv`. A continuación se explica cada sección:

---

### Sección 1 – Carga de datos

```python
df = pd.read_csv(os.path.join(project_dir, 'data', 'gym_members_exercise_tracking.csv'))
```

Carga el archivo CSV en un *DataFrame* de pandas. Primero calcula la ruta absoluta al
archivo usando `__file__` para que el script funcione desde cualquier directorio.
Luego imprime las dimensiones (`filas x columnas`) y los nombres de todas las columnas.

---

### Sección 2 – Información general del dataset

Muestra información básica sobre el contenido del dataset:

- **Tipos de datos** de cada columna (enteros, flotantes, cadenas de texto).
- **Primeras y últimas 5 filas** del dataset para una vista previa rápida.

---

### Sección 3 – Calidad de datos

Evalúa la calidad del dataset buscando:

- **Valores nulos**: cuenta cuántos valores faltan en cada columna y su porcentaje sobre
  el total de filas.
- **Filas duplicadas**: cuenta cuántas filas son copias exactas de otra fila.

Un dataset de buena calidad debe tener cero nulos y cero duplicados.

---

### Sección 4 – Clasificación de variables

Clasifica automáticamente las columnas del dataset en tres categorías:

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Numéricas continuas** | Valores numéricos que pueden tomar cualquier valor real | `Age`, `Weight (kg)`, `Calories_Burned` |
| **Ordinales** | Numéricas con un orden significativo y número reducido de valores | `Experience_Level` (1=Beginner, 2=Intermediate, 3=Expert) |
| **Categóricas nominales** | Texto sin orden inherente | `Gender`, `Workout_Type` |

---

### Sección 5 – Estadísticas descriptivas de variables numéricas

Calcula las medidas estadísticas más importantes para cada variable numérica:

| Medida | Significado |
|--------|-------------|
| **Media** | Promedio aritmético de los valores |
| **Mediana** | Valor que divide los datos en dos mitades iguales |
| **Moda** | Valor que aparece con mayor frecuencia |
| **Desviación estándar** | Qué tan dispersos están los datos respecto a la media |
| **Varianza** | Cuadrado de la desviación estándar |
| **Mínimo / Máximo** | Valor menor y mayor observado |
| **Rango** | Diferencia entre el máximo y el mínimo |
| **Coef. de variación** | Dispersión relativa en porcentaje (`std / media × 100`) |
| **Q1, Q2, Q3** | Primer, segundo y tercer cuartil (percentiles 25, 50, 75) |
| **IQR** | Rango intercuartílico (`Q3 - Q1`): zona del 50 % central de los datos |
| **Asimetría (Skewness)** | Indica si la distribución es simétrica, sesgada a la derecha (+) o a la izquierda (−) |
| **Curtosis (Kurtosis)** | Mide qué tan "puntiaguda" es la distribución respecto a una normal |

---

### Sección 6 – Análisis de variables categóricas

Para cada variable categórica (`Gender`, `Workout_Type`) calcula una **tabla de
frecuencias** con:

- Número de apariciones de cada categoría (**frecuencia absoluta**).
- Porcentaje que representa sobre el total (**frecuencia relativa**).
- Número de **valores únicos** presentes.

---

### Sección 7 – Detección de outliers (método IQR)

Define y aplica la función `detect_outliers_iqr` que detecta valores atípicos usando
el **método de la cerca de Tukey**:

```
Límite inferior = Q1 − 1.5 × IQR
Límite superior = Q3 + 1.5 × IQR
```

Cualquier valor que caiga **fuera de esos límites** se considera un *outlier*. Para cada
variable numérica se reporta el número de outliers, su porcentaje y los límites calculados.

---

### Sección 8 – Estadísticas por grupos

Genera tablas resumen agrupando los datos según variables categóricas clave:

- **Por tipo de ejercicio** (`Workout_Type`): compara la edad, peso, calorías quemadas,
  duración de sesión y BMI entre los distintos tipos de entrenamiento.
- **Por género** (`Gender`): compara edad, peso, altura, calorías, porcentaje de grasa
  y BMI entre hombres y mujeres.
- **Por nivel de experiencia** (`Experience_Level`): analiza cómo varían las calorías,
  duración, frecuencia y porcentaje de grasa según la experiencia del miembro.

---

### Sección 9 – Matriz de correlación

Calcula la **correlación de Pearson** entre todas las variables numéricas. Este coeficiente
varía entre −1 y +1:

- **+1**: correlación positiva perfecta (ambas variables crecen juntas).
- **0**: sin correlación lineal.
- **−1**: correlación negativa perfecta (una sube cuando la otra baja).

Luego genera y guarda un **mapa de calor (heatmap)** en `output/matriz_correlacion.png`
que facilita la lectura visual de las correlaciones. También lista las parejas de variables
con correlaciones fuertes (`|r| > 0.5`).

---

### Sección 10 – Resumen ejecutivo

Imprime un resumen conciso con los hallazgos principales:

- Número total de registros y variables.
- Conteo de nulos y duplicados.
- Rangos y medias de las variables más relevantes.
- Distribución de miembros por género y tipo de ejercicio.

---

## Cómo ejecutar el script

1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar el análisis:
   ```bash
   python src/analisis_descriptivo.py
   ```

El script imprimirá todos los resultados en consola y guardará el heatmap de correlación
en la carpeta `output/`.