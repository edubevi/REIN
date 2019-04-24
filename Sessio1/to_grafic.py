
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import csv



if __name__ == '__main__':

    # Declarem arrays on guardarem els elements del grafic de zipf
    rang = [] # Abscisa del grafic de Zipf (termes)
    freq = [] # Ordenada del grafic de Zipf (Frequencia)

    with open('irelig_bo_grafica.csv','r') as Fitxer:
        plots = csv.reader(Fitxer, delimiter=';')
        for fila in plots:
            rang.append(int(fila[0]))
            freq.append(int(fila[1]))

    # Funcio que calcula la frequencia d'un terme. (Llei zipf)
    def funcio_zipf(r, k, alfa):
        x1 = r**-alfa
        return k*x1

    popt, pcov = curve_fit(funcio_zipf, rang, freq)
    print(popt)
    plt.plot(rang, funcio_zipf(rang, *popt), '-r', label='fit: k=%5.3f, alfa=%5.3f' % tuple(popt))

