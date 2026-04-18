import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from pathlib import Path
from ejercicio1_descriptivo import detectar_columnas, etiqueta_target, sufijo_archivo

TARGETS = ["Calories_Burned", "Calories_Burned_Per_Hour"]
TEST_SIZE = 0.20
RANDOM_STATE = 42
REQUIRED_OUTPUTS = {
	"metricas_txt": "ej2_metricas_regresion_{target}.txt",
	"residuos_png": "ej2_residuos_{target}.png",
}

def crear_preprocesador(num_cols: list[str], cat_cols: list[str]):
	"""Construye el preprocesador para variables numéricas y categóricas.

	Parámetros:
		num_cols (list[str]): Lista de columnas numéricas a escalar con
			StandardScaler.
		cat_cols (list[str]): Lista de columnas categóricas a codificar con
			OneHotEncoder.

	Valor de retorno:
		ColumnTransformer: Objeto de preprocesamiento listo para integrarse en
			el pipeline del modelo.
	"""
	preprocessor = ColumnTransformer(
		transformers=[
			("num", StandardScaler(), num_cols),
			("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
		],
		remainder="drop",
	)
	return preprocessor


def preprocesamiento(df: pd.DataFrame, target: str):
	"""Realiza preprocesado básico y división train/test.

	Parámetros:
		df (pd.DataFrame): DataFrame completo con variables predictoras y la
			variable objetivo definida en target.
		target (str): Nombre de la variable objetivo a modelar.

	Valor de retorno:
		tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, ColumnTransformer]:
			Conjunto de entrenamiento (X_train, y_train), conjunto de prueba
			(X_test, y_test) y el preprocesador configurado.
	"""

	if target not in df.columns:
		raise ValueError(f"La variable objetivo {target} no existe en el dataset.")

	columnas_excluir = [col for col in TARGETS if col in df.columns and col != target]
	X = df.drop(columns=[target] + columnas_excluir)
	y = df[target]
	num_cols, cat_cols = detectar_columnas(X)

	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y,
		test_size=TEST_SIZE,
		random_state=RANDOM_STATE,
	)

	preprocessor = crear_preprocesador(num_cols, cat_cols)

	return X_train, X_test, y_train, y_test, preprocessor


def entrenar_modelo(X_train, y_train, preprocessor):
	"""Entrena una regresión lineal dentro de un pipeline de sklearn.

	Parámetros:
		X_train (pd.DataFrame): Variables predictoras del conjunto de
			entrenamiento.
		y_train (pd.Series): Variable objetivo del conjunto de entrenamiento.
		preprocessor (ColumnTransformer): Transformador de variables numéricas
			y categóricas previamente configurado.

	Valor de retorno:
		Pipeline: Pipeline entrenado con dos etapas, preprocesamiento y
			regresión lineal.
	"""
	model = Pipeline(
		steps=[
			("preprocess", preprocessor),
			("regressor", LinearRegression()),
		]
	)
	model.fit(X_train, y_train)
	return model


def evaluar_modelo(model, X_train, y_train, X_test, y_test):
	"""Calcula métricas de rendimiento en entrenamiento y prueba.

	Parámetros:
		model (Pipeline): Modelo entrenado que implementa el método predict.
		X_train (pd.DataFrame): Variables predictoras de entrenamiento.
		y_train (pd.Series): Objetivo real del conjunto de entrenamiento.
		X_test (pd.DataFrame): Variables predictoras de prueba.
		y_test (pd.Series): Objetivo real del conjunto de prueba.

	Valor de retorno:
		dict: Diccionario con métricas MAE, RMSE y R2 para train y test, y con
			las predicciones de test en la clave `y_pred_test`.
	"""
	# Predicciones Train
	y_pred_train = model.predict(X_train)
	mae_train = mean_absolute_error(y_train, y_pred_train)
	rmse_train = mean_squared_error(y_train, y_pred_train) ** 0.5
	r2_train = r2_score(y_train, y_pred_train)
	
	# Predicciones Test
	y_pred_test = model.predict(X_test)
	mae_test = mean_absolute_error(y_test, y_pred_test)
	rmse_test = mean_squared_error(y_test, y_pred_test) ** 0.5
	r2_test = r2_score(y_test, y_pred_test)
	
	return {
		"train": {"mae": mae_train, "rmse": rmse_train, "r2": r2_train},
		"test": {"mae": mae_test, "rmse": rmse_test, "r2": r2_test},
		"y_pred_test": y_pred_test
	}


def grafico_residuos(y_test, y_pred, out_dir: Path, target: str):
	"""Genera y guarda el gráfico de residuos del modelo.

	Parámetros:
		y_test (pd.Series): Valores reales del conjunto de prueba.
		y_pred (np.ndarray | pd.Series): Valores predichos para el conjunto de
			prueba.
		out_dir (Path): Directorio donde se guarda la imagen del gráfico.
		target (str): Variable objetivo para incorporar su nombre en la salida.

	Valor de retorno:
		Path: Ruta del archivo de imagen generado.
	"""
	residuos = y_test - y_pred

	plt.figure(figsize=(10, 6))
	plt.scatter(y_pred, residuos, alpha=0.6, color="#457b9d")
	plt.axhline(y=0, color="red", linestyle="--", linewidth=1.5)
	plt.xlabel("Valores predichos")
	plt.ylabel("Residuos (real - predicho)")
	plt.title(f"Grafico de residuos - Regresion Lineal ({etiqueta_target(target)})")
	plt.tight_layout()
	ruta = out_dir / REQUIRED_OUTPUTS["residuos_png"].format(target=sufijo_archivo(target))
	plt.savefig(ruta, dpi=180)
	plt.close()
	return ruta


def guardar_metricas(mae: float, rmse: float, r2: float, out_dir: Path, target: str):
	"""Guarda las métricas principales del modelo.

	Parámetros:
		mae (float): Error absoluto medio calculado en test.
		rmse (float): Raíz del error cuadrático medio calculada en test.
		r2 (float): Coeficiente de determinación calculado en test.
		out_dir (Path): Directorio de salida donde se escribe el archivo de
			métricas.
		target (str): Variable objetivo para incorporar su nombre en la salida.

	Valor de retorno:
		Path: Ruta del archivo de métricas creado.
	"""
	ruta = out_dir / REQUIRED_OUTPUTS["metricas_txt"].format(target=sufijo_archivo(target))
	with open(ruta, "w", encoding="utf-8") as f:
		f.write(f"Ejercicio 2 - Metricas Regresion Lineal ({etiqueta_target(target)})\n")
		f.write("=" * 50 + "\n")
		f.write(f"MAE: {mae:.6f}\n")
		f.write(f"RMSE: {rmse:.6f}\n")
		f.write(f"R2: {r2:.6f}\n")
	return ruta

def variables_mas_influyentes(model, top_k: int = 10):
	"""Obtiene las variables con mayor influencia según los coeficientes.

	Parámetros:
		model (Pipeline): Pipeline entrenado con etapas `preprocess` y
			`regressor`.
		top_k (int, opcional): Número de variables a devolver ordenadas por
			valor absoluto del coeficiente. Por defecto es 10.

	Valor de retorno:
		pd.DataFrame: Tabla con columnas `variable`, `coeficiente` y `abs_coef`,
			ordenada de mayor a menor importancia y limitada a `top_k` filas.
	"""
	feature_names = model.named_steps["preprocess"].get_feature_names_out()
	coefs = model.named_steps["regressor"].coef_

	importancia = pd.DataFrame(
		{
			"variable": feature_names,
			"coeficiente": coefs,
			"abs_coef": np.abs(coefs),
		}
	).sort_values("abs_coef", ascending=False)

	return importancia.head(top_k)

if __name__ == "__main__":

	# Carga del csv y configuración de paths de entrada/salida
	base_dir = Path(__file__).resolve().parent
	data_path = base_dir / "data" / "dataset_enriquecido.csv"
	out_dir = base_dir / "output"
	out_dir.mkdir(parents=True, exist_ok=True)
	if not data_path.exists():
		raise FileNotFoundError(f"No se encuentra el dataset en: {data_path}")
	df = pd.read_csv(data_path)

	for target in TARGETS:
		X_train, X_test, y_train, y_test, preprocessor = preprocesamiento(df, target)
		modelo = entrenar_modelo(X_train, y_train, preprocessor)
		resultados = evaluar_modelo(modelo, X_train, y_train, X_test, y_test)
		y_pred_test = resultados["y_pred_test"]
		grafico_residuos(y_test, y_pred_test, out_dir, target)
		guardar_metricas(resultados['test']['mae'], resultados['test']['rmse'], resultados['test']['r2'], out_dir, target)

		influyentes = variables_mas_influyentes(modelo, top_k=10)
