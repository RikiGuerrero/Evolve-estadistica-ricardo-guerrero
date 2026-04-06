import numpy as np
import pandas as pd

def media_evolve(lista_datos: list):
	suma = 0
	for dato in lista_datos:
		suma += dato
	return(suma/len(lista_datos))

def mediana_evolve(lista_datos: list):
	lista_ordenada = sorted(lista_datos)
	n = len(lista_ordenada)
	mitad = n // 2
	if n % 2 == 0:
		return (lista_ordenada[mitad - 1] + lista_ordenada[mitad]) / 2
	else:
		return(lista_ordenada[mitad])

def percentil_evolve(lista_datos: list, percentil: int):
	if percentil <= 0 or percentil > 100:
		return("Error: percetil debe estar entre 1 o 100")
	lista_ordenada = sorted(lista_datos)
	n = len(lista_ordenada)
	mitad = int(n * percentil / 100)
	if n % 2 == 0:
		return (lista_ordenada[mitad - 1] + lista_ordenada[mitad]) / 2
	else:
		return(lista_ordenada[mitad])

def varianza_evolve(lista_datos: list):
	n = len(lista_datos)
	media = media_evolve(lista_datos)
	suma_cuadrados = sum((x - media) ** 2 for x in lista_datos)
	return (suma_cuadrados / (n - 1))

def desviacion_evolve(lista_datos: list):
	return (varianza_evolve(lista_datos) ** 0.5)

def IQR_evolve(lista_datos: list):
	q3 = percentil_evolve(lista_datos, 75)
	q1 = percentil_evolve(lista_datos, 25)
	return (q3 - q1)

def numero_outlier_IQR(lista_datos: list):
	iqr = IQR_evolve(lista_datos)
	q3 = percentil_evolve(lista_datos, 75)
	q1 = percentil_evolve(lista_datos, 25)
	lower = q1 - 1.5 * iqr
	upper = q3 + 1.5 * iqr
	outliers = [x for x in lista_datos if x < lower or x > upper]
	return len(outliers)

def skewness_evolve(lista_datos: list):
	media = media_evolve(lista_datos)
	desviacion = desviacion_evolve(lista_datos)
	n = len(lista_datos)
	skewness = sum(((x - media) / desviacion) ** 3 for x in lista_datos)
	skewness = (1/(n-1)) * skewness
	return skewness

def kurtosis_evolve(lista_datos: list):
	media = media_evolve(lista_datos)
	desviacion = desviacion_evolve(lista_datos)
	n = len(lista_datos)
	kurtosis = sum(((x - media) / desviacion) ** 4 for x in lista_datos) / n - 3
	return kurtosis

if __name__ == "__main__":

	np.random.seed(42)
	edad = list(np.random.randint(20, 60, 100))
	salario =  list(np.random.normal(45000, 15000, 100))
	experiencia = list(np.random.randint(0, 30, 100))
	
	np.random.seed(42)

	df = pd.DataFrame({
		'edad': np.random.randint(20, 60, 100),
		'salario': np.random.normal(45000, 15000, 100),
		'experiencia': np.random.randint(0, 30, 100)
	})

	print("Resultado pandas")
	print("----------------")

	print(df.describe())
	print(df.skew())
	print(df.kurt())

	print("Resultado edades")
	print("----------------")

	print(media_evolve(edad))
	print(mediana_evolve(edad))
	print(percentil_evolve(edad, 50))
	print(varianza_evolve(edad))
	print(desviacion_evolve(edad))
	print(IQR_evolve(edad))
	print(numero_outlier_IQR(edad))
	print(skewness_evolve(edad))
	print(kurtosis_evolve(edad))

	print("Resultado salarios")
	print("----------------")

	print(media_evolve(salario))
	print(mediana_evolve(salario))
	print(percentil_evolve(salario, 50))
	print(varianza_evolve(salario))
	print(desviacion_evolve(salario))
	print(IQR_evolve(salario))
	print(numero_outlier_IQR(salario))
	print(skewness_evolve(salario))
	print(kurtosis_evolve(salario))

	print("Resultado experiencia")
	print("----------------")

	print(media_evolve(experiencia))
	print(mediana_evolve(experiencia))
	print(percentil_evolve(experiencia, 50))
	print(varianza_evolve(experiencia))
	print(desviacion_evolve(experiencia))
	print(IQR_evolve(experiencia))
	print(numero_outlier_IQR(experiencia))
	print(skewness_evolve(experiencia))
	print(kurtosis_evolve(experiencia))

