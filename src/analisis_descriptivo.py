"""
Análisis Descriptivo del Dataset de Miembros de Gimnasio
=========================================================
Este script realiza un análisis exploratorio de datos (EDA) para entender
la estructura y características del dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# =============================================================================
# 1. CARGA DE DATOS
# =============================================================================
print("=" * 80)
print("1. CARGA Y ESTRUCTURA DEL DATASET")
print("=" * 80)

# Obtener directorio del script para rutas relativas
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

df = pd.read_csv(os.path.join(project_dir, 'data', 'gym_members_exercise_tracking.csv'))

print(f"\nDimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")
print(f"\nColumnas disponibles:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

# =============================================================================
# 2. INFORMACIÓN GENERAL DEL DATASET
# =============================================================================
print("\n" + "=" * 80)
print("2. INFORMACIÓN GENERAL DEL DATASET")
print("=" * 80)

print("\nTipos de datos por columna:")
print(df.dtypes)

print("\nPrimeras 5 filas del dataset:")
print(df.head())

print("\nÚltimas 5 filas del dataset:")
print(df.tail())

# =============================================================================
# 3. ANÁLISIS DE VALORES NULOS Y DUPLICADOS
# =============================================================================
print("\n" + "=" * 80)
print("3. CALIDAD DE DATOS - VALORES NULOS Y DUPLICADOS")
print("=" * 80)

print("\nValores nulos por columna:")
null_counts = df.isnull().sum()
null_percentages = (df.isnull().sum() / len(df) * 100).round(2)
null_df = pd.DataFrame({
    'Nulos': null_counts,
    'Porcentaje (%)': null_percentages
})
print(null_df[null_df['Nulos'] > 0] if null_df['Nulos'].sum() > 0 else "No hay valores nulos en el dataset")

print(f"\nFilas duplicadas: {df.duplicated().sum()}")

# =============================================================================
# 4. CLASIFICACIÓN DE VARIABLES
# =============================================================================
print("\n" + "=" * 80)
print("4. CLASIFICACIÓN DE VARIABLES")
print("=" * 80)

# Identificar variables numéricas y categóricas
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()

# Variables ordinales (categóricas con orden numérico)
ordinal_cols = ['Experience_Level']  # 1=Beginner, 2=Intermediate, 3=Expert

print(f"\nVariables Numéricas Continuas ({len(numeric_cols) - len(ordinal_cols)}):")
for col in numeric_cols:
    if col not in ordinal_cols:
        print(f"  - {col}")

print(f"\nVariables Ordinales ({len(ordinal_cols)}):")
print("  (Categóricas con orden numérico)")
for col in ordinal_cols:
    print(f"  - {col}: 1=Beginner, 2=Intermediate, 3=Expert")

print(f"\nVariables Categóricas Nominales ({len(categorical_cols)}):")
for col in categorical_cols:
    print(f"  - {col}")

# =============================================================================
# 5. ESTADÍSTICAS DESCRIPTIVAS - VARIABLES NUMÉRICAS
# =============================================================================
print("\n" + "=" * 80)
print("5. ESTADÍSTICAS DESCRIPTIVAS - VARIABLES NUMÉRICAS")
print("=" * 80)

print("\nResumen estadístico general:")
print(df[numeric_cols].describe().T)

print("\n" + "-" * 60)
print("Medidas de tendencia central y dispersión detalladas:")
print("-" * 60)

stats_detailed = pd.DataFrame({
    'Media': df[numeric_cols].mean(),
    'Mediana': df[numeric_cols].median(),
    'Moda': df[numeric_cols].mode().iloc[0],
    'Desv. Estándar': df[numeric_cols].std(),
    'Varianza': df[numeric_cols].var(),
    'Mínimo': df[numeric_cols].min(),
    'Máximo': df[numeric_cols].max(),
    'Rango': df[numeric_cols].max() - df[numeric_cols].min(),
    'Coef. Variación (%)': (df[numeric_cols].std() / df[numeric_cols].mean() * 100)
})
print(stats_detailed.round(2))

print("\n" + "-" * 60)
print("Cuartiles y Rango Intercuartílico (IQR):")
print("-" * 60)

quartiles = pd.DataFrame({
    'Q1 (25%)': df[numeric_cols].quantile(0.25),
    'Q2 (50%)': df[numeric_cols].quantile(0.50),
    'Q3 (75%)': df[numeric_cols].quantile(0.75),
    'IQR': df[numeric_cols].quantile(0.75) - df[numeric_cols].quantile(0.25)
})
print(quartiles.round(2))

print("\n" + "-" * 60)
print("Asimetría (Skewness) y Curtosis:")
print("-" * 60)

shape_stats = pd.DataFrame({
    'Asimetría (Skewness)': df[numeric_cols].skew(),
    'Curtosis': df[numeric_cols].kurtosis()
})
print(shape_stats.round(2))

# =============================================================================
# 6. ANÁLISIS DE VARIABLES CATEGÓRICAS
# =============================================================================
print("\n" + "=" * 80)
print("6. ANÁLISIS DE VARIABLES CATEGÓRICAS")
print("=" * 80)

for col in categorical_cols:
    print(f"\n--- {col} ---")
    freq_table = df[col].value_counts()
    freq_pct = df[col].value_counts(normalize=True) * 100
    
    cat_summary = pd.DataFrame({
        'Frecuencia': freq_table,
        'Porcentaje (%)': freq_pct.round(2)
    })
    print(cat_summary)
    print(f"Valores únicos: {df[col].nunique()}")

# =============================================================================
# 7. DETECCIÓN DE OUTLIERS (MÉTODO IQR)
# =============================================================================
print("\n" + "=" * 80)
print("7. DETECCIÓN DE OUTLIERS (MÉTODO IQR)")
print("=" * 80)

def detect_outliers_iqr(data, column):
    """Detecta outliers usando el método IQR"""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return len(outliers), lower_bound, upper_bound

print("\nOutliers detectados por variable numérica:")
print("-" * 60)

outlier_summary = []
for col in numeric_cols:
    n_outliers, lb, ub = detect_outliers_iqr(df, col)
    pct_outliers = (n_outliers / len(df)) * 100
    outlier_summary.append({
        'Variable': col,
        'N° Outliers': n_outliers,
        '% Outliers': round(pct_outliers, 2),
        'Límite Inferior': round(lb, 2),
        'Límite Superior': round(ub, 2)
    })

outlier_df = pd.DataFrame(outlier_summary)
print(outlier_df.to_string(index=False))

# =============================================================================
# 8. ESTADÍSTICAS POR GRUPOS (WORKOUT_TYPE Y GENDER)
# =============================================================================
print("\n" + "=" * 80)
print("8. ESTADÍSTICAS POR GRUPOS")
print("=" * 80)

print("\n--- Estadísticas por Tipo de Ejercicio (Workout_Type) ---")
workout_stats = df.groupby('Workout_Type').agg({
    'Age': ['mean', 'std'],
    'Weight (kg)': ['mean', 'std'],
    'Calories_Burned': ['mean', 'std', 'min', 'max'],
    'Session_Duration (hours)': ['mean', 'std'],
    'BMI': ['mean', 'std']
}).round(2)
print(workout_stats)

print("\n--- Estadísticas por Género ---")
gender_stats = df.groupby('Gender').agg({
    'Age': ['mean', 'std', 'count'],
    'Weight (kg)': ['mean', 'std'],
    'Height (m)': ['mean', 'std'],
    'Calories_Burned': ['mean', 'std'],
    'Fat_Percentage': ['mean', 'std'],
    'BMI': ['mean', 'std']
}).round(2)
print(gender_stats)

print("\n--- Estadísticas por Nivel de Experiencia ---")
exp_stats = df.groupby('Experience_Level').agg({
    'Age': ['mean', 'count'],
    'Calories_Burned': ['mean', 'std'],
    'Session_Duration (hours)': ['mean'],
    'Workout_Frequency (days/week)': ['mean'],
    'Fat_Percentage': ['mean']
}).round(2)
print(exp_stats)

# =============================================================================
# 9. MATRIZ DE CORRELACIÓN
# =============================================================================
print("\n" + "=" * 80)
print("9. MATRIZ DE CORRELACIÓN (PEARSON)")
print("=" * 80)

correlation_matrix = df[numeric_cols].corr()

# Crear nombres cortos para mejor visualización
short_names = {
    'Age': 'Age',
    'Weight (kg)': 'Weight',
    'Height (m)': 'Height',
    'Max_BPM': 'Max_BPM',
    'Avg_BPM': 'Avg_BPM',
    'Resting_BPM': 'Rest_BPM',
    'Session_Duration (hours)': 'Duration',
    'Calories_Burned': 'Calories',
    'Fat_Percentage': 'Fat_%',
    'Water_Intake (liters)': 'Water',
    'Workout_Frequency (days/week)': 'Freq',
    'Experience_Level': 'Exp_Lvl',
    'BMI': 'BMI'
}

# Crear matriz con nombres cortos para visualización
corr_display = correlation_matrix.copy()
corr_display.index = [short_names.get(c, c) for c in corr_display.index]
corr_display.columns = [short_names.get(c, c) for c in corr_display.columns]

# Crear directorio para gráficos si no existe
output_dir = os.path.join(project_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

# Generar heatmap de correlación
fig, ax = plt.subplots(figsize=(12, 10))

# Crear el heatmap manualmente con imshow
im = ax.imshow(corr_display.values, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)

# Configurar ejes
ax.set_xticks(range(len(corr_display.columns)))
ax.set_yticks(range(len(corr_display.index)))
ax.set_xticklabels(corr_display.columns, rotation=45, ha='right', fontsize=10)
ax.set_yticklabels(corr_display.index, fontsize=10)

# Añadir valores en cada celda
for i in range(len(corr_display.index)):
    for j in range(len(corr_display.columns)):
        value = corr_display.iloc[i, j]
        color = 'white' if abs(value) > 0.5 else 'black'
        ax.text(j, i, f'{value:.2f}', ha='center', va='center', 
                color=color, fontsize=8, fontweight='bold' if abs(value) > 0.5 else 'normal')

# Añadir barra de colores
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Coeficiente de Correlación (Pearson)', fontsize=11)

# Títulos
ax.set_title('Matriz de Correlación - Gym Members Dataset\n', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}/matriz_correlacion.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print(f"\n✓ Heatmap guardado en: {output_dir}/matriz_correlacion.png")

print("\n" + "-" * 60)
print("Correlaciones más fuertes (|r| > 0.5):")
print("-" * 60)

# Encontrar correlaciones fuertes
strong_correlations = []
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        corr_value = correlation_matrix.iloc[i, j]
        if abs(corr_value) > 0.5:
            strong_correlations.append({
                'Variable 1': correlation_matrix.columns[i],
                'Variable 2': correlation_matrix.columns[j],
                'Correlación': round(corr_value, 3)
            })

if strong_correlations:
    strong_corr_df = pd.DataFrame(strong_correlations)
    strong_corr_df = strong_corr_df.sort_values('Correlación', key=abs, ascending=False)
    print(strong_corr_df.to_string(index=False))
else:
    print("No se encontraron correlaciones con |r| > 0.5")

# =============================================================================
# 10. RESUMEN EJECUTIVO
# =============================================================================
print("\n" + "=" * 80)
print("10. RESUMEN EJECUTIVO DEL ANÁLISIS")
print("=" * 80)

print(f"""
DATASET: Gym Members Exercise Tracking
--------------------------------------
• Total de registros: {len(df)}
• Total de variables: {len(df.columns)}
  - Numéricas: {len(numeric_cols)}
  - Categóricas: {len(categorical_cols)}

CALIDAD DE DATOS:
• Valores nulos: {df.isnull().sum().sum()}
• Filas duplicadas: {df.duplicated().sum()}

VARIABLES CLAVE:
• Edad: {df['Age'].min()}-{df['Age'].max()} años (media: {df['Age'].mean():.1f})
• Peso: {df['Weight (kg)'].min()}-{df['Weight (kg)'].max()} kg (media: {df['Weight (kg)'].mean():.1f})
• BMI: {df['BMI'].min():.1f}-{df['BMI'].max():.1f} (media: {df['BMI'].mean():.1f})
• Calorías quemadas: {df['Calories_Burned'].min():.0f}-{df['Calories_Burned'].max():.0f} (media: {df['Calories_Burned'].mean():.1f})

DISTRIBUCIÓN POR GÉNERO:
{df['Gender'].value_counts().to_string()}

DISTRIBUCIÓN POR TIPO DE EJERCICIO:
{df['Workout_Type'].value_counts().to_string()}
""")