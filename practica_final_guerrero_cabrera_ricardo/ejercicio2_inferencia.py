from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET = "Calories_Burned"
TEST_SIZE = 0.20
RANDOM_STATE = 42
REQUIRED_OUTPUTS = {
	"metricas_txt": "ej2_metricas_regresion.txt",
	"residuos_png": "ej2_residuos.png",
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


def preprocesamiento(df: pd.DataFrame):
	"""Realiza preprocesado básico y división train/test.

	Parámetros:
		df (pd.DataFrame): DataFrame completo con variables predictoras y la
			variable objetivo definida en TARGET.

	Valor de retorno:
		tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, ColumnTransformer]:
			Conjunto de entrenamiento (X_train, y_train), conjunto de prueba
			(X_test, y_test) y el preprocesador configurado.
	"""

	if TARGET not in df.columns:
		raise ValueError(f"La variable objetivo {TARGET} no existe en el dataset.")

	num_cols, cat_cols = detectar_columnas(df)
	X = df.drop(columns=[TARGET])
	y = df[TARGET]

	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y,
		test_size=TEST_SIZE,
		random_state=RANDOM_STATE,
	)

	print(f"Total filas: {len(df)}")
	print(f"Train: {X_train.shape[0]} filas ({100 * (1 - TEST_SIZE):.0f}%)")
	print(f"Test: {X_test.shape[0]} filas ({100 * TEST_SIZE:.0f}%)")
	print(f"Variables numericas: {len(num_cols)}")
	print(f"Variables categoricas: {len(cat_cols)}")

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


def grafico_residuos(y_test, y_pred, out_dir: Path):
	"""Genera y guarda el gráfico de residuos del modelo.

	Parámetros:
		y_test (pd.Series): Valores reales del conjunto de prueba.
		y_pred (np.ndarray | pd.Series): Valores predichos para el conjunto de
			prueba.
		out_dir (Path): Directorio donde se guarda la imagen del gráfico.

	Valor de retorno:
		None: La función guarda la figura y muestra por consola la
			ruta del archivo generado.
	"""
	residuos = y_test - y_pred

	plt.figure(figsize=(10, 6))
	plt.scatter(y_pred, residuos, alpha=0.6, color="#457b9d")
	plt.axhline(y=0, color="red", linestyle="--", linewidth=1.5)
	plt.xlabel("Valores predichos")
	plt.ylabel("Residuos (real - predicho)")
	plt.title("Grafico de residuos - Regresion Lineal")
	plt.tight_layout()
	plt.savefig(out_dir / REQUIRED_OUTPUTS["residuos_png"], dpi=180)
	print(f"Grafico de residuos guardado en: {out_dir / REQUIRED_OUTPUTS['residuos_png']}")
	plt.close()


def guardar_metricas(mae: float, rmse: float, r2: float, out_dir: Path):
	"""Guarda las métricas principales del modelo.

	Parámetros:
		mae (float): Error absoluto medio calculado en test.
		rmse (float): Raíz del error cuadrático medio calculada en test.
		r2 (float): Coeficiente de determinación calculado en test.
		out_dir (Path): Directorio de salida donde se escribe el archivo de
			métricas.

	Valor de retorno:
		None: La función crea el archivo de métricas y reporta su
			ruta por consola.
	"""
	ruta = out_dir / REQUIRED_OUTPUTS["metricas_txt"]
	with open(ruta, "w", encoding="utf-8") as f:
		f.write("Ejercicio 2 - Metricas Regresion Lineal\n")
		f.write("=" * 50 + "\n")
		f.write(f"MAE: {mae:.6f}\n")
		f.write(f"RMSE: {rmse:.6f}\n")
		f.write(f"R2: {r2:.6f}\n")
	print(f"Métricas guardadas en: {ruta}")

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
	data_path = base_dir / "data" / "gym_members_exercise_tracking.csv"
	out_dir = base_dir / "output"
	out_dir.mkdir(parents=True, exist_ok=True)
	if not data_path.exists():
		raise FileNotFoundError(f"No se encuentra el dataset en: {data_path}")
	df = pd.read_csv(data_path)

	print("=" * 70)
	print("PREPROCESAMIENTO")
	print("=" * 70)
	X_train, X_test, y_train, y_test, preprocessor = preprocesamiento(df)

	print("\n" + "=" * 70)
	print("MODELO - REGRESION LINEAL")
	print("=" * 70)
	modelo = entrenar_modelo(X_train, y_train, preprocessor)
	resultados = evaluar_modelo(modelo, X_train, y_train, X_test, y_test)
	y_pred_test = resultados["y_pred_test"]
	grafico_residuos(y_test, y_pred_test, out_dir)
	guardar_metricas(resultados['test']['mae'], resultados['test']['rmse'], resultados['test']['r2'], out_dir)

	print("\n--- METRICAS TRAIN ---")
	print(f"MAE:  {resultados['train']['mae']:.4f}")
	print(f"RMSE: {resultados['train']['rmse']:.4f}")
	print(f"R2:   {resultados['train']['r2']:.4f}")
	
	print("\n--- METRICAS TEST ---")
	print(f"MAE:  {resultados['test']['mae']:.4f}")
	print(f"RMSE: {resultados['test']['rmse']:.4f}")
	print(f"R2:   {resultados['test']['r2']:.4f}")

	influyentes = variables_mas_influyentes(modelo, top_k=10)
	print("\nVariables mas influyentes:")
	print(influyentes[["variable", "coeficiente"]].to_string(index=False))
