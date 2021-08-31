import json


jsonmap = json.load(open('nodes.json'))

aristas = set()
mapa = {'aristas': [], 'pesos': [], 'vertices': set()}
for v1 in jsonmap:
    mapa['vertices'].add(v1['name'])
    for v2 in v1['adyacents']:
        newSet = {v1['name'], v2}
        if newSet not in mapa['aristas']:
            mapa['aristas'].append(newSet)
            mapa['pesos'].append(v1['adyacents'][v2])


'''mapa = {
    'aristas': [{'a','b'}, {'a','c'}, {'a','i'}, {'c','d'}, {'i','d'}, {'b','f'}, {'f','d'}, {'f','h'}, {'d','e'}, {'f','g'}, {'g','e'}],
    'pesos': [7, 7, 1, 5, 6, 2, 1, 4, 1, 3, 4],
    'vertices': {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'}
}'''

def calcRoutes(vertice):
    Np = set()
    DisPre = {}

    Np.add(vertice)
    for v in mapa['vertices']:
        if v != vertice:
            if {vertice, v} in mapa['aristas']:
                indice = mapa['aristas'].index({vertice, v})
                DisPre[v] = (mapa['pesos'][indice], vertice)
            else:
                DisPre[v] = (1e300, vertice)

    while Np != mapa['vertices']:
        restantes = mapa['vertices'] - Np
        menorDist = (1e301, 'pre')
        menorV = 'act'
        for v in DisPre:
            if v in restantes:
                tupla = DisPre[v]
                if tupla[0] < menorDist[0]:
                    menorDist = tupla
                    menorV = v
        Np.add(menorV)
        restantes = mapa['vertices'] - Np
        for v in DisPre:
            if v in restantes:
                if {v, menorV} in mapa['aristas']:
                    tupla = DisPre[v]
                    indice = mapa['aristas'].index({v, menorV})
                    distancia = mapa['pesos'][indice]
                    if (distancia + menorDist[0]) < tupla[0]:
                        DisPre[v] = (distancia + menorDist[0], menorV)
    return DisPre

def calcPath(v1, v2):
    DisPre = calcRoutes(v1)
    act = v2
    Path = []
    distance = DisPre[v2][0]
    while act != v1:
        Path.insert(0, act)
        act = DisPre[act][1]
    Path.insert(0, v1)
    return Path, distance


def nextNode(v1, v2):
    return calcPath(v1, v2)[0][1]

def recipients(v1):
    vertices = mapa['vertices'] - {v1}
    return vertices
