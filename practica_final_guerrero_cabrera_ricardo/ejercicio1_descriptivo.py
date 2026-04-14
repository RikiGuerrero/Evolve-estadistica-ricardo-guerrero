from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


TARGET = "Calories_Burned"
REQUIRED_OUTPUTS = {
	"descriptivo_csv": "ej1_descriptivo.csv",
	"histogramas_png": "ej1_histogramas.png",
	"boxplots_png": "ej1_boxplots.png",
	"heatmap_png": "ej1_heatmap_correlacion.png",
	"categoricas_png": "ej1_categoricas.png",
}


def detectar_columnas(df: pd.DataFrame):
	"""Identifica columnas numéricas y categóricas en un DataFrame.

	Parámetros:
		df (pd.DataFrame): Conjunto de datos de entrada a partir del cual se
			clasifican variables por tipo. Además, las columnas numéricas con
			10 o menos valores únicos se tratan como categóricas.

	Valor de retorno:
		tuple[list[str], list[str]]: Tupla con dos listas en este orden:
			columnas numéricas continuas y columnas categóricas detectadas.
	"""
	cat_cols = df.select_dtypes(include=["object", "category", "bool", "string"]).columns.tolist()

	# Tratar numéricas discretas con pocos niveles como categóricas (p.ej. Experience_Level)
	for col in df.select_dtypes(include=[np.number]).columns:
		if col not in cat_cols and df[col].nunique() <= 10:
			cat_cols.append(col)

	num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in cat_cols]
	return num_cols, cat_cols

def limites_iqr(serie: pd.Series):
	"""Calcula límites IQR y máscara de outliers."""
	q1 = serie.quantile(0.25)
	q3 = serie.quantile(0.75)
	iqr = q3 - q1
	li = q1 - 1.5 * iqr
	ls = q3 + 1.5 * iqr
	mask = (serie < li) | (serie > ls)
	return li, ls, mask


def resumen_estructural(df: pd.DataFrame):
	"""Genera y muestra un resumen estructural básico del DataFrame.

	Parámetros:
		df (pd.DataFrame): Conjunto de datos de entrada sobre el que se calcula
			el número de filas y columnas, uso de memoria, tipos de datos y
			porcentaje de valores nulos por columna.

	Valor de retorno:
		dict: Diccionario con las claves `n_filas`, `n_cols`, `memoria_mb`,
			`dtypes` y `nulos_pct`, que contienen los principales indicadores
			estructurales del DataFrame.
	"""
	n_filas, n_cols = df.shape
	memoria_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
	dtypes = df.dtypes.astype(str)
	nulos_pct = (df.isna().mean() * 100).round(2)

	print("=" * 70)
	print("A) RESUMEN ESTRUCTURAL")
	print("=" * 70)
	print(f"Filas: {n_filas}")
	print(f"Columnas: {n_cols}")
	print(f"Tamaño en memoria: {memoria_mb:.3f} MB")
	print("\nTipos de dato (dtypes):")
	print(dtypes)
	print("\nPorcentaje de valores nulos por columna:")
	print(nulos_pct.sort_values(ascending=False))

	return {
		"n_filas": n_filas,
		"n_cols": n_cols,
		"memoria_mb": memoria_mb,
		"dtypes": dtypes,
		"nulos_pct": nulos_pct,
	}


def estadisticos(df: pd.DataFrame, num_cols: list[str]):
	"""Calcula y muestra estadísticas descriptivas de variables numéricas.

	Parámetros:
		df (pd.DataFrame): DataFrame de entrada que contiene las variables
			numéricas y la variable objetivo definida en TARGET.
		num_cols (list[str]): Lista de nombres de columnas numéricas sobre las
			que se calculan media, mediana, moda, dispersión y cuartiles.

	Valor de retorno:
		None: La función imprime por pantalla la tabla de estadísticos
			descriptivos y las métricas de IQR, asimetría y curtosis de TARGET.
	"""
	# Estadísticos solicitados
	stats_df = pd.DataFrame({
		"media": df[num_cols].mean(),
		"mediana": df[num_cols].median(),
		"moda": df[num_cols].mode().iloc[0],
		"desv_tipica": df[num_cols].std(),
		"varianza": df[num_cols].var(),
		"minimo": df[num_cols].min(),
		"q1": df[num_cols].quantile(0.25),
		"q2": df[num_cols].quantile(0.50),
		"q3": df[num_cols].quantile(0.75),
		"maximo": df[num_cols].max(),
	}).round(4)

	q1_t = df[TARGET].quantile(0.25)
	q3_t = df[TARGET].quantile(0.75)
	iqr_target = q3_t - q1_t
	skew_target = df[TARGET].skew()
	kurt_target = df[TARGET].kurtosis()

	print("\n" + "=" * 70)
	print("B) ESTADISTICOS DESCRIPTIVOS DE VARIABLES NUMERICAS")
	print("=" * 70)
	print(stats_df)
	print(f"\nIQR de {TARGET}: {iqr_target:.4f}")
	print(f"Asimetria (skewness) de {TARGET}: {skew_target:.4f}")
	print(f"Curtosis de {TARGET}: {kurt_target:.4f}")


def distribuciones(df: pd.DataFrame, num_cols: list[str], cat_cols: list[str], out_dir: Path):
	# Histogramas de variables numéricas
	n_num = len(num_cols)
	cols_plot = 3
	rows_plot = int(np.ceil(n_num / cols_plot))

	fig, axes = plt.subplots(rows_plot, cols_plot, figsize=(cols_plot * 5, rows_plot * 3.8))
	axes = np.array(axes).reshape(-1)

	for i, col in enumerate(num_cols):
		sns.histplot(df[col], kde=True, bins=25, ax=axes[i], color="#2a9d8f")
		axes[i].set_title(col, fontsize=10)

	for j in range(i + 1, len(axes)):
		axes[j].axis("off")

	fig.suptitle("Histogramas de variables numéricas", fontsize=14)
	fig.tight_layout()
	fig.savefig(out_dir / REQUIRED_OUTPUTS["histogramas_png"], dpi=180)
	plt.close(fig)

	# Boxplots del target por cada categórica
	if not cat_cols:
		print("\nNo hay variables categóricas detectadas para boxplots.")
	else:
		cols_plot = 2
		rows_plot = int(np.ceil(len(cat_cols) / cols_plot))
		fig, axes = plt.subplots(rows_plot, cols_plot, figsize=(cols_plot * 7, rows_plot * 4))
		axes = np.array(axes).reshape(-1)

		for i, col in enumerate(cat_cols):
			sns.boxplot(data=df, x=col, y=TARGET, ax=axes[i], color="#e9c46a")
			axes[i].set_title(f"{TARGET} por {col}", fontsize=10)
			axes[i].tick_params(axis="x", rotation=25)

		for j in range(i + 1, len(axes)):
			axes[j].axis("off")

		fig.suptitle("Boxplots de la variable objetivo por variables categóricas", fontsize=14)
		fig.tight_layout()
		fig.savefig(out_dir / REQUIRED_OUTPUTS["boxplots_png"], dpi=180)
		plt.close(fig)

	# Detección y tratamiento de outliers por IQR (winsorización por clipping)
	outlier_resumen = []
	df_tratado = df.copy()

	for col in num_cols:
		li, ls, mask = limites_iqr(df[col])
		n_out = int(mask.sum())
		pct_out = 100 * n_out / len(df)

		outlier_resumen.append({
			"variable": col,
			"n_outliers": n_out,
			"pct_outliers": round(pct_out, 2),
			"limite_inferior": round(li, 4),
			"limite_superior": round(ls, 4),
		})

		df_tratado[col] = df_tratado[col].clip(lower=li, upper=ls)

	outlier_df = pd.DataFrame(outlier_resumen).sort_values("pct_outliers", ascending=False)

	print("\n" + "=" * 70)
	print("C) OUTLIERS (MÉTODO IQR) Y TRATAMIENTO")
	print("=" * 70)
	print(outlier_df)

	return df_tratado


def apartado_d_categoricas(df: pd.DataFrame, cat_cols: list[str], out_dir: Path):
	print("\n" + "=" * 70)
	print("D) VARIABLES CATEGÓRICAS")
	print("=" * 70)

	if not cat_cols:
		print("No hay variables categóricas detectadas.")
		return

	cols_plot = 2
	rows_plot = int(np.ceil(len(cat_cols) / cols_plot))
	fig, axes = plt.subplots(rows_plot, cols_plot, figsize=(cols_plot * 7, rows_plot * 4))
	axes = np.array(axes).reshape(-1)

	for i, col in enumerate(cat_cols):
		abs_freq = df[col].value_counts(dropna=False)
		rel_freq = (df[col].value_counts(dropna=False, normalize=True) * 100).round(2)
		tabla = pd.DataFrame({
			"frecuencia_abs": abs_freq,
			"frecuencia_rel_pct": rel_freq,
		})

		print(f"\nFrecuencias en {col}:")
		print(tabla)

		dom = rel_freq.iloc[0]
		if dom > 60:
			print(f"Posible desbalance: categoría dominante en {col} ({dom:.2f}%).")
		else:
			print(f"Sin dominio extremo en {col} (máximo {dom:.2f}%).")

		sns.countplot(data=df, x=col, ax=axes[i], color="#457b9d")
		axes[i].set_title(f"Frecuencia de {col}", fontsize=10)
		axes[i].tick_params(axis="x", rotation=25)

	for j in range(i + 1, len(axes)):
		axes[j].axis("off")

	fig.suptitle("Frecuencia de variables categóricas", fontsize=14)
	fig.tight_layout()
	fig.savefig(out_dir / REQUIRED_OUTPUTS["categoricas_png"], dpi=180)
	plt.close(fig)


def apartado_e_correlaciones(df_tratado: pd.DataFrame, num_cols: list[str], out_dir: Path):
	corr = df_tratado[num_cols].corr(method="pearson")

	plt.figure(figsize=(12, 9))
	sns.heatmap(corr, cmap="RdBu_r", center=0, vmin=-1, vmax=1, annot=False, square=True)
	plt.title("Matriz de correlación de Pearson")
	plt.tight_layout()
	plt.savefig(out_dir / REQUIRED_OUTPUTS["heatmap_png"], dpi=180)
	plt.close()

	if TARGET not in corr.columns:
		raise ValueError(f"{TARGET} no aparece en columnas numéricas para correlación.")

	corr_target = corr[TARGET].drop(TARGET).abs().sort_values(ascending=False)
	top3 = corr_target.head(3)

	pares_multicol = []
	cols_num = corr.columns.tolist()
	for i in range(len(cols_num)):
		for j in range(i + 1, len(cols_num)):
			r = corr.iloc[i, j]
			if abs(r) > 0.9:
				pares_multicol.append((cols_num[i], cols_num[j], r))

	print("\n" + "=" * 70)
	print("E) CORRELACIONES")
	print("=" * 70)
	print("Top 3 correlaciones absolutas con la variable objetivo:")
	for var, r in top3.items():
		print(f"  - {var}: {r:.4f}")

	if not pares_multicol:
		print("\nNo se detectaron pares con multicolinealidad fuerte (|r| > 0.9).")
	else:
		print("\nPares con posible multicolinealidad (|r| > 0.9):")
		for v1, v2, r in pares_multicol:
			print(f"  - {v1} vs {v2}: r = {r:.4f}")

	return top3, pares_multicol

if __name__ == "__main__":

	print("=" * 70)
	print("EJERCICIO 1 — Análisis Estadístico Descriptivo")
	print("=" * 70)

	#--------------------------------------------------------------------------------
	# Carga del csv y configuración de paths de entrada/salida
	#--------------------------------------------------------------------------------
	base_dir = Path(__file__).resolve().parent
	data_path = base_dir / "data" / "gym_members_exercise_tracking.csv"
	out_dir = base_dir / "output"
	out_dir.mkdir(parents=True, exist_ok=True)
	if not data_path.exists():
		raise FileNotFoundError(f"No se encuentra el dataset en: {data_path}")
	df = pd.read_csv(data_path)

	resumen_estructural(df)

	num_cols, cat_cols = detectar_columnas(df)
	estadisticos(df, num_cols)

	df_tratado = distribuciones(df, num_cols, cat_cols, out_dir)

	# D) Categóricas
	apartado_d_categoricas(df, cat_cols, out_dir)

	# E) Correlaciones
	apartado_e_correlaciones(df_tratado, num_cols, out_dir)

	df.describe().to_csv(out_dir / REQUIRED_OUTPUTS["descriptivo_csv"], index=True)

	print("\nArchivos generados en output/:")
	print(f"  - {REQUIRED_OUTPUTS['descriptivo_csv']}")
	print(f"  - {REQUIRED_OUTPUTS['histogramas_png']}")
	print(f"  - {REQUIRED_OUTPUTS['boxplots_png']}")
	print(f"  - {REQUIRED_OUTPUTS['heatmap_png']}")
	print(f"  - {REQUIRED_OUTPUTS['categoricas_png']}")