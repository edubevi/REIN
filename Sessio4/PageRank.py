#!/usr/bin/python

import time
import sys
import codecs
import numpy as np
from operator import itemgetter


class Edge:
    def __init__(self, origin=None, destination=None):
        self.origin = origin
        self.destination = destination
        self.weight = 1  # escriviu el valor que correspongui

    def __repr__(self):
        return "edge: {0} {1} {2}".format(self.origin, self.destination, self.weight)


class Airport:
    def __init__(self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.incoming_routes = []  # Llistat de rutes entrants (amb aquest aeroport com a destinació).
        self.outgoing_routes = []  # Llistat de rutes sortints (amb aquest aeroport d'origen).
        self.routeHash = dict()  # Aeroport d'origen de rutes entrants -> outweight
        self.outweight = 0  # escriviu el valor que correspongui
        self.pageRank = 0

    def __repr__(self):
        return "{0:.8f}\t{1} - {2}".format(self.pageRank, self.code, self.name)


edgeList = []  # llista de Edge
edgeHash = dict()  # hash de edge per facilitar el matching
airportList = []  # llista d'Airport
airportHash = dict()  # hash key IATA code -> Airport
sink_airports = []  # llistat d'Aeroports aglotinadors


def readAirports(fd):
    print("+ Reading Airport file from", fd)

    airportsTxt = open(fd, "r")  # si teniu problemes amb la codificacio, fer servir la linia de baix
    # airportsTxt = codecs.open(fd, "r", encoding="cp1252", errors="ignore")

    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5:
                raise Exception('not an IATA code')
            a.name = temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code = temp[4][1:-1]
            a.index = cont
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a

    airportsTxt.close()
    # Inicialitzem els atributs pageRank de tots els Aeroports amb valor 1/n
    for a in airportList: a.pageRank = 1 / cont
    print("+ There were {0} airports with IATA code.".format(cont))


def readRoutes(fd):
    print("+ Reading Routes file from {0}".format(fd))
    # escriviu el vostre codi
    rutesTxt = open(fd, "r")
    cont = 0

    for line in rutesTxt.readlines():
        try:
            temp = line.split(',')
            origin = temp[2]
            destination = temp[4]
            # Descartem rutes amb aeroports desconeguts.
            if (origin not in airportHash) or (destination not in airportHash):
                if (len(temp[2]) != 3) or (len(temp[4]) != 3):
                    raise Exception('not an IATA code')
                else:
                    raise Exception('route with unknown airport')
        except Exception as inst:
            continue

        orgAirport = airportHash[origin]
        dstAirport = airportHash[destination]

        if (origin, destination) in edgeHash:
            e = edgeHash[(origin, destination)]
            e.weight += 1

        else:
            e = Edge(origin, destination)
            edgeHash[(origin, destination)] = e
            edgeList.append(e)
            orgAirport.outgoing_routes.append(e)
            dstAirport.incoming_routes.append(e)

        orgAirport.outweight += 1
        dstAirport.routeHash[origin] = orgAirport.outweight
        cont += 1

    rutesTxt.close()

    # afegim els aeroports aglotinadors a la llista de sink_airports
    [sink_airports.append(a) for a in airportList if a.outweight == 0]
    print("+ There were {0} valid rutes.".format(cont))
    print("+ There are {0} sink airports.".format(len(sink_airports)))

def PageRank(a):
    page_rank = 0
    if a not in sink_airports:
        for route in a.incoming_routes:
            adj_a = airportHash[route.origin]  # Aeroport d'origen de la ruta
            page_rank += adj_a.pageRank * route.weight / adj_a.outweight
    return page_rank

def computePageRanks(damping, end_type, condition):
    n = len(airportList)
    L = damping
    iterations = 0
    end_iteration = False

    while not end_iteration:
        time1 = time.time()
        Q = [0] * n  # Array on posarem els nous pageranks
        sum_newpr = conv_value = 0   # suma total dels nous pageranks i valor de convergencia respecte als anteriors.

        for i in range(0, n):
            PageRankSinks = (sum([a.pageRank for a in sink_airports])) / n #Calculem Pagerank dels aeroports aglotinadors
            Q[i] = L * PageRank(airportList[i]) + L * PageRankSinks + (1 - L) / n
            conv_value += abs(airportList[i].pageRank - Q[i])
            sum_newpr += Q[i]
        #Actualitzem els pageRanks dels aeroports amb els que s'han calculat.
        for j in range(0, n): airportList[j].pageRank = Q[j]
        iterations += 1
        #Determinem si es compleix la condicio d'acabament.
        if end_type == "iter" : end_iteration = iterations > condition
        else: end_iteration = conv_value < condition
        #Comprovem que la suma de pageranks d'aquesta iteracio sigui 1
        time2=time.time()
        print("Iteration {0}:\t{1}\t{2:.4f} sec".format(iterations, sum_newpr, time2 - time1))

    return iterations

def outputPageRanks():
    print("*******************************************************************************")
    print("****************** ( #Rank, Page rank, Airport name ) *************************")
    print("*******************************************************************************")
    sorted_list = sorted(airportList, key=lambda Airport: Airport.pageRank, reverse=True)
    for cont, airport in enumerate(sorted_list):
        print("{0}.\t\t{1}".format(cont+1, airport))
    print("*******************************************************************************")
    print()

def main(argv=None):
    print("*******************************************************************************")
    print("***************** PAGERANK ALGORITHM ON AIRPORT ROUTES ************************")
    print("*******************************************************************************")
    print()
    readAirports("airports.txt")
    readRoutes("routes.txt")
    print()
    print("*******************************************************************************")
    print("******** ( #Iteration, Sum of Page ranks, Iteration computation time ) ********")
    print("*******************************************************************************")
    time1 = time.time()
    iterations = computePageRanks(0.85, "converge", 0.0001)
    time2 = time.time()
    print()
    outputPageRanks()

    # comproveu que la suma dels page ranks us doni 1
    s = sum([a.pageRank for a in airportList])
    print("Sum of Page Rank: %s" % s)

    print("Total Iterations: {0}".format(iterations))
    print("Time of computePageRanks(): {0:.4f} sec".format(time2 - time1))

if __name__ == "__main__":
    sys.exit(main())
