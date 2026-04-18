from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


TARGETS = ["Calories_Burned", "Calories_Burned_Per_Hour"]
TARGET_LABELS = {
	"Calories_Burned": "Calories Burned",
	"Calories_Burned_Per_Hour": "Calories Burned Per Hour"
}
REQUIRED_OUTPUTS = {
	"dataset_enriquecido_csv": "dataset_enriquecido.csv",
	"descriptivo_csv": "ej1_descriptivo.csv",
	"histogramas_png": "ej1_histogramas.png",
	"boxplots_png": "ej1_boxplots_{target}.png",
	"heatmap_png": "ej1_heatmap_correlacion.png",
	"categoricas_png": "ej1_categoricas.png",
}


def etiqueta_target(target: str):
	"""Devuelve una etiqueta legible para un target dado."""
	return TARGET_LABELS.get(target, target)


def sufijo_archivo(target: str):
	"""Convierte el nombre de una columna en un sufijo seguro para archivo."""
	return target.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")

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


def limites_zscore(serie: pd.Series, z_threshold: float):
	"""Calcula límites por Z-score y detecta outliers en una serie numérica.

	Parámetros:
		serie (pd.Series): Serie numérica sobre la que se estima la media,
			desviación estándar y la máscara de valores atípicos.
		z_threshold (float): Umbral de Z-score para considerar un
			valor como outlier.

	Valor de retorno:
		tuple[float, float, pd.Series]: Límite inferior, límite superior y
			máscara booleana con True en las observaciones clasificadas como
			outliers. Si la desviación estándar es 0 o NaN, devuelve límites
			infinitos y una máscara sin outliers.
	"""
	mu = serie.mean()
	sigma = serie.std(ddof=1)
	if sigma == 0 or np.isnan(sigma):
		li, ls = -np.inf, np.inf
		mask = pd.Series(False, index=serie.index)
	else:
		li = mu - z_threshold * sigma
		ls = mu + z_threshold * sigma
		mask = ((serie - mu).abs() / sigma) > z_threshold
	return li, ls, mask


def resumen_estructural(df: pd.DataFrame, csv_path: Path):
	"""Genera y muestra un resumen estructural básico del DataFrame.

	Parámetros:
		df (pd.DataFrame): Conjunto de datos de entrada sobre el que se calcula
			el número de filas y columnas, tipos de datos y porcentaje de
			valores nulos por columna.
		csv_path (Path): Ruta al archivo CSV original.

	Valor de retorno:
		dict: Diccionario con las claves `n_filas`, `n_cols`, `memoria_mb`,
			`dtypes` y `nulos_pct`, que contienen los principales indicadores
			estructurales del DataFrame.
	"""
	n_filas, n_cols = df.shape
	memoria_mb = csv_path.stat().st_size / (1024 ** 2)
	dtypes = df.dtypes.astype(str)
	nulos_pct = (df.isna().mean() * 100).round(2)

	return {
		"n_filas": n_filas,
		"n_cols": n_cols,
		"memoria_mb": memoria_mb,
		"dtypes": dtypes,
		"nulos_pct": nulos_pct,
	}


def estadisticos(df: pd.DataFrame, num_cols: list[str], targets: list[str]):
	"""Calcula estadísticas descriptivas de variables numéricas.

	Parámetros:
		df (pd.DataFrame): DataFrame de entrada que contiene las variables
			numéricas y las variables objetivo indicadas en targets.
		num_cols (list[str]): Lista de nombres de columnas numéricas sobre las
			que se calculan media, mediana, moda, dispersión y cuartiles.
		targets (list[str]): Lista de columnas objetivo para las que se calcula
			IQR, asimetría y curtosis.

	Valor de retorno:
		tuple[pd.DataFrame, dict[str, dict[str, float]]]:
			- DataFrame con estadísticos descriptivos de las variables numéricas.
			- Diccionario con métricas por target (`iqr`, `skewness`, `kurtosis`).
	"""
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

	indicadores_targets = {}

	for target in targets:
		if target not in df.columns:
			raise ValueError(f"La variable objetivo {target} no existe en el dataset.")

		q1_t = df[target].quantile(0.25)
		q3_t = df[target].quantile(0.75)
		iqr_target = q3_t - q1_t
		skew_target = df[target].skew()
		kurt_target = df[target].kurtosis()

		indicadores_targets[target] = {
			"iqr": float(iqr_target),
			"skewness": float(skew_target),
			"kurtosis": float(kurt_target),
		}

	return stats_df, indicadores_targets


def distribuciones(df: pd.DataFrame, num_cols: list[str], cat_cols: list[str], out_dir: Path, targets: list[str]):
	"""Genera histogramas, boxplots y detección de outliers con Z-score.

	Parámetros:
		df (pd.DataFrame): DataFrame de entrada sobre el que se generan las
			distribuciones y se evalúan los outliers.
		num_cols (list[str]): Lista de columnas numéricas para dibujar los
			histogramas y aplicar la detección de outliers.
		cat_cols (list[str]): Lista de columnas categóricas usadas para crear
			boxplots de las variables objetivo.
		out_dir (Path): Directorio donde se guardan las imágenes generadas.
		targets (list[str]): Lista de variables objetivo para generar boxplots.

	Valor de retorno:
		pd.DataFrame: Resumen de outliers por variable, ordenado por
			porcentaje de outliers de mayor a menor.
	"""
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

	# Boxplots de cada target por variable categórica.
	if cat_cols:
		for target in targets:
			if target not in df.columns:
				raise ValueError(f"La variable objetivo {target} no existe en el dataset.")

			cols_plot = 2
			rows_plot = int(np.ceil(len(cat_cols) / cols_plot))
			fig, axes = plt.subplots(rows_plot, cols_plot, figsize=(cols_plot * 7, rows_plot * 4))
			axes = np.array(axes).reshape(-1)

			for i, col in enumerate(cat_cols):
				sns.boxplot(data=df, x=col, y=target, ax=axes[i], color="#e9c46a")
				axes[i].set_title(f"{etiqueta_target(target)} por {col}", fontsize=10)
				axes[i].tick_params(axis="x", rotation=25)

			for j in range(i + 1, len(axes)):
				axes[j].axis("off")

			fig.suptitle(f"Boxplots de {etiqueta_target(target)} por variables categóricas", fontsize=14)
			fig.tight_layout()
			ruta_boxplot = out_dir / REQUIRED_OUTPUTS["boxplots_png"].format(target=sufijo_archivo(target))
			fig.savefig(ruta_boxplot, dpi=180)
			plt.close(fig)

	# Detección de outliers.
	outlier_resumen = []

	for col in num_cols:
		li, ls, mask = limites_zscore(df[col], z_threshold=3.0)

		n_out = int(mask.sum())
		pct_out = 100 * n_out / len(df)

		outlier_resumen.append({
			"variable": col,
			"n_outliers": n_out,
			"pct_outliers": round(pct_out, 2),
			"limite_inferior": round(li, 4),
			"limite_superior": round(ls, 4),
		})

	resumen_df = pd.DataFrame(outlier_resumen).sort_values(by="pct_outliers", ascending=False)
	return resumen_df


def categoricas(df: pd.DataFrame, cat_cols: list[str], out_dir: Path):
	"""Analiza variables categóricas y genera sus gráficos de frecuencia.

	Parámetros:
		df (pd.DataFrame): DataFrame de entrada con las variables a analizar.
		cat_cols (list[str]): Lista de columnas categóricas para calcular
			frecuencias absolutas/relativas y crear los countplots.
		out_dir (Path): Directorio donde se guarda la imagen con los gráficos
			de variables categóricas.

	Valor de retorno:
		dict[str, pd.DataFrame]: Diccionario con tablas de frecuencias por
			variable categórica. Si no hay variables categóricas, devuelve
			un diccionario vacío.
	"""

	if not cat_cols:
		return {}

	cols_plot = 2
	rows_plot = int(np.ceil(len(cat_cols) / cols_plot))
	fig, axes = plt.subplots(rows_plot, cols_plot, figsize=(cols_plot * 7, rows_plot * 4))
	axes = np.array(axes).reshape(-1)
	tablas_frecuencia = {}

	for i, col in enumerate(cat_cols):
		abs_freq = df[col].value_counts(dropna=False)
		rel_freq = (df[col].value_counts(dropna=False, normalize=True) * 100).round(2)
		tabla = pd.DataFrame({
			"frecuencia_abs": abs_freq,
			"frecuencia_rel_pct": rel_freq,
		})
		tablas_frecuencia[col] = tabla

		dom = rel_freq.iloc[0]

		sns.countplot(data=df, x=col, ax=axes[i], color="#457b9d")
		axes[i].set_title(f"Frecuencia de {col}", fontsize=10)
		if dom > 60:
			axes[i].set_xlabel(f"{col} (posible desbalance)")
		axes[i].tick_params(axis="x", rotation=25)

	for j in range(i + 1, len(axes)):
		axes[j].axis("off")

	fig.suptitle("Frecuencia de variables categóricas", fontsize=14)
	fig.tight_layout()
	fig.savefig(out_dir / REQUIRED_OUTPUTS["categoricas_png"], dpi=180)
	plt.close(fig)

	return tablas_frecuencia


def correlaciones(df_tratado: pd.DataFrame, num_cols: list[str], out_dir: Path, targets: list[str]):
	"""Calcula correlaciones, genera un heatmap y resume relaciones clave.

	Parámetros:
		df_tratado (pd.DataFrame): DataFrame con variables numéricas ya
			preprocesadas.
		num_cols (list[str]): Lista de columnas numéricas usadas para construir
			la matriz de correlación de Pearson.
		out_dir (Path): Directorio donde se guarda la imagen del heatmap.
		targets (list[str]): Variables objetivo para las que se resumen las
			correlaciones más altas.

	Valor de retorno:
		tuple[dict[str, pd.Series], list[tuple[str, str, float]]]:
			- Top 3 correlaciones absolutas por variable objetivo.
			- Lista de pares con posible multicolinealidad (|r| > 0.9).
	"""
	# Calcula matriz de correlación de Pearson y genera un heatmap.
	corr = df_tratado[num_cols].corr(method="pearson")

	plt.figure(figsize=(13, 10))
	sns.heatmap(
		corr,
		cmap="RdBu_r",
		center=0,
		vmin=-1,
		vmax=1,
		annot=True,
		fmt=".2f",
		square=True,
		linewidths=0.4,
		linecolor="white",
		cbar_kws={"label": "Correlación de Pearson"},
		annot_kws={"size": 8},
	)
	plt.title("Matriz de correlación de Pearson")
	plt.xticks(rotation=45, ha="right")
	plt.yticks(rotation=0)
	plt.tight_layout()
	plt.savefig(out_dir / REQUIRED_OUTPUTS["heatmap_png"], dpi=180)
	plt.close()

	# Analiza correlaciones con cada variable objetivo.
	correlaciones_por_target = {}
	for target in targets:
		if target not in corr.columns:
			raise ValueError(f"{target} no aparece en columnas numéricas para correlación.")

		corr_target = corr[target].drop(target).abs().sort_values(ascending=False)
		top3 = corr_target.head(3)
		correlaciones_por_target[target] = top3

	pares_multicol = []
	cols_num = corr.columns.tolist()
	for i in range(len(cols_num)):
		for j in range(i + 1, len(cols_num)):
			r = corr.iloc[i, j]
			if abs(r) > 0.9:
				pares_multicol.append((cols_num[i], cols_num[j], r))

	return correlaciones_por_target, pares_multicol

if __name__ == "__main__":

	# Carga del csv y configuración de paths de entrada/salida
	base_dir = Path(__file__).resolve().parent
	data_path = base_dir / "data" / "gym_members_exercise_tracking.csv"
	out_dir = base_dir / "output"
	out_dir.mkdir(parents=True, exist_ok=True)
	if not data_path.exists():
		raise FileNotFoundError(f"No se encuentra el dataset en: {data_path}")
	df = pd.read_csv(data_path)

	# Crear variable derivada de calorías quemadas por hora y guardar dataset enriquecido.
	df["Calories_Burned_Per_Hour"] = df["Calories_Burned"] / df["Session_Duration (hours)"]
	df.to_csv(base_dir / "data" / REQUIRED_OUTPUTS["dataset_enriquecido_csv"], index=False)

	resumen_estructural(df, data_path)
	df.describe().to_csv(out_dir / REQUIRED_OUTPUTS["descriptivo_csv"], index=True)

	num_cols, cat_cols = detectar_columnas(df)
	estadisticos(df, num_cols, TARGETS)

	distribuciones(df, num_cols, cat_cols, out_dir, TARGETS)

	categoricas(df, cat_cols, out_dir)

	correlaciones(df, num_cols, out_dir, TARGETS)
