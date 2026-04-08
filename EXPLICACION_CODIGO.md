# Explicación del Código: analisis_descriptivo.py

## Resumen General

Este script de Python realiza un **Análisis Exploratorio de Datos (EDA)** completo sobre un dataset de miembros de gimnasio que rastrean sus ejercicios. El análisis está diseñado para comprender la estructura, calidad y características estadísticas del dataset.

## Estructura del Código

El script está organizado en 10 secciones principales:

---

## 1. Carga de Datos (Líneas 14-29)

```python
df = pd.read_csv(os.path.join(project_dir, 'data', 'gym_members_exercise_tracking.csv'))
```

**¿Qué hace?**
- Carga el archivo CSV con los datos de los miembros del gimnasio
- Usa rutas relativas para que el script funcione desde cualquier ubicación
- Muestra las dimensiones del dataset (filas x columnas)
- Lista todas las columnas disponibles

**Conceptos clave:**
- `os.path` permite manejar rutas de archivos de forma independiente del sistema operativo
- `pd.read_csv()` es la función de Pandas para leer archivos CSV

---

## 2. Información General del Dataset (Líneas 32-45)

```python
print(df.dtypes)
print(df.head())
print(df.tail())
```

**¿Qué hace?**
- Muestra los tipos de datos de cada columna (numérico, texto, etc.)
- Presenta las primeras 5 filas (`head()`) para ver ejemplos de datos
- Presenta las últimas 5 filas (`tail()`) para verificar la estructura completa

**Por qué es importante:**
- Permite identificar si los datos se cargaron correctamente
- Ayuda a detectar problemas en el formato de los datos

---

## 3. Análisis de Calidad de Datos (Líneas 48-63)

```python
null_counts = df.isnull().sum()
null_percentages = (df.isnull().sum() / len(df) * 100).round(2)
```

**¿Qué hace?**
- Detecta valores faltantes (nulos/NaN) en cada columna
- Calcula el porcentaje de valores nulos
- Identifica filas duplicadas completas

**Por qué es importante:**
- Los valores nulos pueden afectar los análisis estadísticos
- Las filas duplicadas pueden sesgar los resultados
- Es el primer paso para evaluar la calidad del dataset

---

## 4. Clasificación de Variables (Líneas 66-91)

```python
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
```

**¿Qué hace?**
- Separa las variables en tres tipos:
  - **Numéricas continuas**: edad, peso, calorías, etc.
  - **Ordinales**: variables categóricas con orden (ej: nivel de experiencia 1, 2, 3)
  - **Categóricas nominales**: texto sin orden (ej: género, tipo de ejercicio)

**Por qué es importante:**
- Cada tipo de variable requiere técnicas de análisis diferentes
- Las variables numéricas permiten calcular medias, desviación estándar, etc.
- Las variables categóricas se analizan con frecuencias y porcentajes

---

## 5. Estadísticas Descriptivas (Líneas 94-140)

Esta es una de las secciones más importantes. Calcula múltiples medidas estadísticas:

### Medidas de Tendencia Central
```python
'Media': df[numeric_cols].mean()
'Mediana': df[numeric_cols].median()
'Moda': df[numeric_cols].mode().iloc[0]
```

**¿Qué significan?**
- **Media**: promedio aritmético (suma de todos los valores / cantidad de valores)
- **Mediana**: valor central cuando los datos están ordenados
- **Moda**: valor que más se repite

### Medidas de Dispersión
```python
'Desv. Estándar': df[numeric_cols].std()
'Varianza': df[numeric_cols].var()
'Rango': df[numeric_cols].max() - df[numeric_cols].min()
```

**¿Qué significan?**
- **Desviación Estándar**: qué tan dispersos están los datos respecto a la media
- **Varianza**: desviación estándar al cuadrado (mide variabilidad)
- **Rango**: diferencia entre el valor máximo y mínimo
- **Coeficiente de Variación**: desviación estándar relativa a la media (en porcentaje)

### Cuartiles
```python
'Q1 (25%)': df[numeric_cols].quantile(0.25)
'Q3 (75%)': df[numeric_cols].quantile(0.75)
'IQR': Q3 - Q1
```

**¿Qué significan?**
- **Q1 (Primer Cuartil)**: 25% de los datos están por debajo de este valor
- **Q2 (Segundo Cuartil/Mediana)**: 50% de los datos están por debajo
- **Q3 (Tercer Cuartil)**: 75% de los datos están por debajo
- **IQR (Rango Intercuartílico)**: diferencia entre Q3 y Q1, mide la dispersión del 50% central de los datos

### Forma de la Distribución
```python
'Asimetría (Skewness)': df[numeric_cols].skew()
'Curtosis': df[numeric_cols].kurtosis()
```

**¿Qué significan?**
- **Asimetría (Skewness)**:
  - = 0: distribución simétrica
  - > 0: cola hacia la derecha (más valores bajos)
  - < 0: cola hacia la izquierda (más valores altos)
- **Curtosis**: qué tan "puntiaguda" o "plana" es la distribución
  - > 0: más puntiaguda que la normal (más valores extremos)
  - < 0: más plana que la normal

---

## 6. Análisis de Variables Categóricas (Líneas 143-159)

```python
freq_table = df[col].value_counts()
freq_pct = df[col].value_counts(normalize=True) * 100
```

**¿Qué hace?**
- Cuenta cuántas veces aparece cada categoría
- Calcula el porcentaje de cada categoría
- Identifica cuántos valores únicos hay

**Ejemplo:**
Si `Gender` tiene:
- Male: 500 (50%)
- Female: 500 (50%)

---

## 7. Detección de Outliers (Líneas 162-194)

```python
def detect_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
```

**¿Qué son los outliers?**
- Valores atípicos o extremos que se alejan significativamente del resto de los datos
- Pueden ser errores de medición o casos especiales reales

**Método IQR (Rango Intercuartílico):**
- Si un valor es menor que `Q1 - 1.5 × IQR` → outlier inferior
- Si un valor es mayor que `Q3 + 1.5 × IQR` → outlier superior

**¿Por qué 1.5?**
- Es una regla empírica estándar en estadística
- Identifica aproximadamente el 0.7% de los datos más extremos en una distribución normal

---

## 8. Estadísticas por Grupos (Líneas 197-232)

```python
workout_stats = df.groupby('Workout_Type').agg({
    'Age': ['mean', 'std'],
    'Calories_Burned': ['mean', 'std', 'min', 'max']
})
```

**¿Qué hace?**
- Agrupa los datos por categorías (tipo de ejercicio, género, nivel de experiencia)
- Calcula estadísticas para cada grupo
- Permite comparar diferentes subgrupos del dataset

**Ejemplo de análisis:**
- ¿Las personas que hacen cardio queman más calorías que las que hacen yoga?
- ¿Los hombres y mujeres tienen diferente IMC promedio?
- ¿Los principiantes entrenan con menor frecuencia que los expertos?

---

## 9. Matriz de Correlación (Líneas 235-324)

```python
correlation_matrix = df[numeric_cols].corr()
```

**¿Qué es la correlación?**
- Mide la relación lineal entre dos variables numéricas
- Rango: -1 a +1
  - **+1**: correlación positiva perfecta (cuando una sube, la otra también)
  - **0**: no hay correlación lineal
  - **-1**: correlación negativa perfecta (cuando una sube, la otra baja)

**Interpretación:**
- |r| > 0.7: correlación fuerte
- 0.4 < |r| < 0.7: correlación moderada
- |r| < 0.4: correlación débil

**Visualización:**
- Crea un mapa de calor (heatmap) con colores:
  - Rojo: correlación positiva
  - Azul: correlación negativa
  - Blanco: sin correlación

**Ejemplo de correlaciones esperadas:**
- Peso y calorías quemadas (positiva)
- Edad y nivel de experiencia (positiva)
- Porcentaje de grasa y duración del ejercicio (negativa)

---

## 10. Resumen Ejecutivo (Líneas 327-356)

**¿Qué hace?**
- Presenta un resumen consolidado de todo el análisis
- Incluye las métricas más importantes
- Proporciona una vista rápida del dataset sin entrar en detalles técnicos

---

## Bibliotecas Utilizadas

### 1. Pandas (`import pandas as pd`)
- Biblioteca principal para análisis de datos
- Proporciona la estructura DataFrame (tabla de datos)
- Funciones para leer, manipular y analizar datos

### 2. NumPy (`import numpy as np`)
- Biblioteca para computación numérica
- Base para Pandas
- Operaciones matemáticas eficientes

### 3. Matplotlib (`import matplotlib.pyplot as plt`)
- Biblioteca para crear visualizaciones y gráficos
- Se usa para generar el heatmap de correlación

### 4. OS (`import os`)
- Módulo para interactuar con el sistema operativo
- Manejo de rutas de archivos y directorios

---

## Flujo del Análisis

```
1. Cargar datos → 2. Inspeccionar estructura → 3. Verificar calidad
                                                          ↓
10. Resumen ← 9. Correlaciones ← 8. Grupos ← 7. Outliers ← 6. Categóricas ← 5. Numéricas
                                                                                    ↓
                                                                           4. Clasificar variables
```

---

## Conceptos Estadísticos Clave

### Dataset
Una colección estructurada de datos organizados en filas y columnas:
- **Filas**: observaciones o registros individuales (cada miembro del gym)
- **Columnas**: variables o características (edad, peso, etc.)

### Variable
Una característica que puede variar entre observaciones:
- **Cuantitativa**: valores numéricos (peso, edad)
- **Cualitativa**: categorías (género, tipo de ejercicio)

### Población vs Muestra
- **Población**: todos los miembros posibles del gimnasio
- **Muestra**: los datos que tenemos (subset de la población)

### Estadística Descriptiva vs Inferencial
- **Descriptiva**: resume y describe los datos (lo que hace este script)
- **Inferencial**: hace predicciones sobre la población basándose en la muestra

---

## Interpretación de Resultados

### Ejemplo Práctico
Si el script muestra:
```
Age:
  Media: 35.5
  Desv. Estándar: 8.2
  Rango: 18-65
```

**Interpretación:**
- La edad promedio de los miembros es 35.5 años
- La mayoría de los miembros tiene entre 27.3 y 43.7 años (media ± 1 desv. estándar)
- El miembro más joven tiene 18 años y el mayor 65 años

---

## Casos de Uso

Este análisis es útil para:

1. **Gestión del gimnasio**: entender el perfil de los miembros
2. **Personalización**: adaptar programas según características comunes
3. **Marketing**: identificar segmentos de clientes
4. **Investigación**: estudiar patrones de ejercicio y salud
5. **Calidad de datos**: detectar errores antes de análisis más avanzados

---

## Próximos Pasos Sugeridos

Después de este análisis descriptivo, se podría:

1. **Visualizaciones**: crear gráficos de distribuciones, boxplots
2. **Pruebas de hipótesis**: verificar si las diferencias entre grupos son significativas
3. **Modelos predictivos**: predecir calorías quemadas basándose en otras variables
4. **Clustering**: agrupar miembros con características similares
5. **Series temporales**: analizar tendencias a lo largo del tiempo

---

## Buenas Prácticas Implementadas

1. **Organización clara**: el código está dividido en secciones lógicas
2. **Comentarios descriptivos**: cada sección tiene un título explicativo
3. **Rutas relativas**: el código funciona desde cualquier ubicación
4. **Manejo de errores**: verifica si hay valores nulos antes de procesarlos
5. **Salida legible**: formatea los resultados con separadores y títulos
6. **Guardado de resultados**: exporta el heatmap como imagen

---

## Salidas Generadas

### En Consola
- Tablas con estadísticas descriptivas
- Resúmenes de variables categóricas
- Detección de outliers
- Matriz de correlación

### Archivos
- `output/matriz_correlacion.png`: visualización de correlaciones

---

## Limitaciones del Análisis

1. **No maneja valores nulos**: asume que los datos están completos
2. **No valida tipos de datos**: confía en que el CSV está bien formado
3. **No hace limpieza de datos**: no corrige outliers ni errores
4. **Solo análisis univariado y bivariado**: no explora interacciones entre 3+ variables
5. **Correlación ≠ Causalidad**: las correlaciones no implican causa-efecto

---

## Glosario de Términos

- **DataFrame**: estructura de datos tabular de Pandas
- **EDA**: Exploratory Data Analysis (Análisis Exploratorio de Datos)
- **IQR**: Interquartile Range (Rango Intercuartílico)
- **BMI**: Body Mass Index (Índice de Masa Corporal)
- **BPM**: Beats Per Minute (Pulsaciones Por Minuto)
- **CSV**: Comma-Separated Values (Valores Separados por Comas)
- **NaN**: Not a Number (valor faltante o no válido)

---

## Resumen Final

Este script es una herramienta completa de análisis descriptivo que:
- ✅ Carga y valida datos
- ✅ Calcula estadísticas fundamentales
- ✅ Detecta problemas de calidad
- ✅ Identifica patrones y relaciones
- ✅ Genera visualizaciones
- ✅ Produce un resumen ejecutivo

Es la base esencial para cualquier análisis de datos posterior y proporciona una comprensión profunda del dataset de miembros del gimnasio.
