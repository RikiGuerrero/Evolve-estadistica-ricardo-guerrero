import math
import random
import matplotlib.pyplot as plt
import numpy as np




# Parameters:
a = 2.0
b = 1.0
xmin = 0.0
xmax = 10.0
noise = 2.0
n = 100

np.random.seed(42)

# Randomly generated problem data:
x = xmin + np.random.rand(n)*(xmax - xmin)
t = a*x + b + np.random.randn(n)*noise
	
def regresion_lineal_simple(x, t, num_iters=8, eta=0.01):
		w = np.random.randn()
		b = np.random.randn()

		xmin, xmax = x.min(), x.max()
		plt.figure(figsize=(6, 6))
		plt.plot(x, t, 'o', label='Datos')
		for i in range(num_iters):

			# Definición de la recta
			y = w * x + b

			#Cálculo del error
			error = y - t

			#Cálculo del gradiente de lo pesos b, w1
			dw = np.sum(error * x)*2/len(x)
			db = np.sum(error)*2/len(x)

			#Actualización de parametros
			w -= eta * dw
			b -= eta * db

			
			plt.plot([xmin, xmax], [w * xmin + b, w * xmax + b], color='gray', label=f'Iter {i+1}')
	
		plt.grid(True)
		plt.xlabel("x")
		plt.ylabel("t")
		plt.title(f"Iteración {i+1}")
		plt.legend()
		
		plt.savefig(f"regresion_iter_{i+1}.png")

		return w, b

def show_data():

	plt.figure(figsize=(6, 6))
	plt.plot(x, t, 'o')
	plt.plot([xmin, xmax], [a*xmin + b, a*xmax + b], 'r-')
	plt.grid(True)
	plt.xlabel("x")
	plt.ylabel("t")
	plt.savefig("data.png")

def main():
	show_data()
	w, b = regresion_lineal_simple(x, t)


if __name__ == "__main__":
	 main()