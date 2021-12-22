from collections import defaultdict
import cv2 as cv
import numpy as np

datei = None  # die Datei mit dem Projektplan
vorgang = ""  # der aktuelle Vorgang
vorgangsListe = []
woerterbuchTitel = ["nr", "bezeichnung", "dauer", "vorgaenger"]
vorgangsWoerterbuch = {}

###  Pfade Rechner!
class Graph:

    def __init__(self, vertices):
        # No. of vertices
        self.V = vertices

        # default dictionary to store graph
        self.graph = defaultdict(list)
        self.paths = {}

    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)

    '''A recursive function to print all paths from 'u' to 'd'.
    visited[] keeps track of vertices in current path.
    path[] stores actual vertices and path_index is current
    index in path[]'''

    def printAllPathsUtil(self, u, d, visited, path):

        # Mark the current node as visited and store in path
        visited[u] = True
        path.append(u)
        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            self.paths[d].append(list(path))
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if not visited[i]:
                    self.printAllPathsUtil(i, d, visited, path)

        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[u] = False

    # Prints all paths from 's' to 'd'
    def printAllPaths(self, s, d):
        self.paths[d] = []
        # Mark all the vertices as not visited
        visited = [False] * (self.V)
        # Create an array to store paths
        path = []
        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path)

    def getPaths(self):
        return self.paths


## Vorgangsliste erstellen

with open("netzplan", "r", encoding="utf8") as datei:
    for vorgang in datei:
        vorgang = vorgang.strip('\n')
        vorgangsListe.append(vorgang)

for i, vorgang in enumerate(vorgangsListe):
    vorgang = vorgang.split('|')
    vorgangsWoerterbuch = {}
    for j, eintrag in enumerate(vorgang):
        if j != 3:
            vorgangsWoerterbuch[woerterbuchTitel[j]] = eintrag
        else:
            vorgangsWoerterbuch[woerterbuchTitel[j]] = eintrag.split('&')
    vorgangsListe[i] = vorgangsWoerterbuch

vorgaengerListe = []
nrListe = []

## vorgängerliste

for vorgang in vorgangsListe:
    vorgaenger = vorgang["vorgaenger"]
    nr = vorgang["nr"]
    nrListe.append(nr)
    vorgaengerListe.append(vorgaenger)

## nachfolgerliste

nachfolgerListe = []

for nr in nrListe:
    nachfolger = []
    for i, vorgaengers in enumerate(vorgaengerListe):
        for vorgaenger in vorgaengerListe[i]:
            if vorgaenger == nr:
                nachfolger.append(nrListe[i])
    nachfolgerListe.append(nachfolger)

## Vorwärtsrechnung

for i, vorgang in enumerate(vorgangsListe):
    if i == 0:
        vorgangsListe[i]["faz"] = 0
        vorgangsListe[i]["fez"] = int(vorgangsListe[i]["dauer"])
    else:
        fezListe = []
        for vorgaenger in vorgaengerListe[i]:
            indx = nrListe.index(vorgaenger)
            fezListe.append(vorgangsListe[indx]["fez"])
        vorgangsListe[i]["faz"] = max(fezListe)
        vorgangsListe[i]["fez"] = vorgangsListe[i]["faz"] + int(vorgangsListe[i]["dauer"])

## Rückwärtsrechnung

vorgangsListe.reverse()
nachfolgerListe.reverse()
nrListe.reverse()

for i, vorgang in enumerate(vorgangsListe):
    if i == 0:
        vorgangsListe[i]["saz"] = vorgangsListe[i]["faz"]
        vorgangsListe[i]["sez"] = vorgangsListe[i]["fez"]
    else:
        sazListe = []
        for nachfolger in nachfolgerListe[i]:
            indx = nrListe.index(nachfolger)
            sazListe.append(vorgangsListe[indx]["saz"])
        vorgangsListe[i]["sez"] = min(sazListe)
        vorgangsListe[i]["saz"] = vorgangsListe[i]["sez"] - int(vorgangsListe[i]["dauer"])

vorgangsListe.reverse()
nachfolgerListe.reverse()
nrListe.reverse()

## freier puffer

for i, vorgang in enumerate(vorgangsListe):
    fazListe = []
    for nachfolger in nachfolgerListe[i]:
        indx = nrListe.index(nachfolger)
        fazListe.append(vorgangsListe[indx]["faz"])
    if (len(fazListe) != 0):
        vorgangsListe[i]["fp"] = min(fazListe) - vorgangsListe[i]["fez"]
    else:
        vorgangsListe[i]["fp"] = 0

## gesamtpuffer

for i, vorgang in enumerate(vorgangsListe):
    vorgangsListe[i]["gp"] = vorgang["saz"] - vorgang["faz"]

for i, vorgang in enumerate(vorgangsListe):
    for key, entry in enumerate(vorgang):
        value = vorgangsListe[i][entry]
        if isinstance(value, int):
            vorgangsListe[i][entry] = str(vorgangsListe[i][entry])

## darstellung im print

nrl = 0
bzl = 0
drl = 0
fal = 0
fel = 0
sal = 0
sel = 0
gpl = 0
fpl = 0

for vorgang in vorgangsListe:
    nrl = len(vorgang["nr"]) if len(vorgang["nr"]) > nrl else nrl
    bzl = len(vorgang["bezeichnung"]) if len(vorgang["bezeichnung"]) > bzl else bzl
    drl = len(vorgang["dauer"]) if len(vorgang["dauer"]) > drl else drl
    fal = len(vorgang["faz"]) if len(vorgang["faz"]) > fal else fal
    sal = len(vorgang["saz"]) if len(vorgang["saz"]) > sal else sal
    fel = len(vorgang["fez"]) if len(vorgang["fez"]) > fel else fel
    sel = len(vorgang["sez"]) if len(vorgang["sez"]) > sel else sel
    gpl = len(vorgang["gp"]) if len(vorgang["gp"]) > gpl else gpl
    fpl = len(vorgang["fp"]) if len(vorgang["fp"]) > fpl else fpl

spalte1 = max([nrl, fal, sal]) + 2
spalte2 = max([drl, gpl]) + 2
spalte3 = fpl + 2
spalte4 = max([fel, sel]) + 2
spBez = spalte2 + spalte3 + spalte4

zeile1 = "\u250C"

for i in range(spalte1):
    zeile1 += "\u2500"
zeile1 += "\u252C"

for i in range(spBez + 2):
    zeile1 += "\u2500"
zeile1 += "\u2512"

zeile2 = "\u251E"

for i in range(spalte1):
    zeile2 += "\u2500"
zeile2 += "\u253C"
for i in range(spalte2):
    zeile2 += "\u2500"
zeile2 += "\u2530"
for i in range(spalte3):
    zeile2 += "\u2500"
zeile2 += "\u2530"
for i in range(spalte4):
    zeile2 += "\u2500"
zeile2 += "\u2524"

zeile3 = "\u251E"
for i in range(spalte1):
    zeile3 += "\u2500"
zeile3 += "\u253C"
for i in range(spalte2):
    zeile3 += "\u2500"
zeile3 += "\u253C"
for i in range(spalte3):
    zeile3 += "\u2500"
zeile3 += "\u253C"
for i in range(spalte4):
    zeile3 += "\u2500"
zeile3 += "\u2524"

zeile4 = "\u2514"
for i in range(spalte1):
    zeile4 += "\u2500"
zeile4 += "\u2534"
for i in range(spalte2):
    zeile4 += "\u2500"
zeile4 += "\u2534"
for i in range(spalte3):
    zeile4 += "\u2500"
zeile4 += "\u2534"
for i in range(spalte4):
    zeile4 += "\u2500"
zeile4 += "\u2518"
kritischerPfad = []
for i, vorgang in enumerate(vorgangsListe):
    nr = vorgang["nr"]
    bz = vorgang["bezeichnung"]
    if len(bz) > spBez:
        bz = bz[:spBez]
    fa = vorgang["faz"]
    dr = vorgang["dauer"]
    fe = vorgang["fez"]
    sa = vorgang["saz"]
    gp = vorgang["gp"]
    fp = vorgang["fp"]
    se = vorgang["sez"]
    nachfolger = ", ".join([str(nachfolger) for nachfolger in nachfolgerListe[i]])
    vorgaenger = ", ".join([str(vorgaenger) for vorgaenger in vorgaengerListe[i]])
    kritischerWeg = ""
    if int(gp) == 0 and int(fp) == 0:
        kritischerPfad.append(nr)
        kritischerWeg = "kritischer Pfad!"
    print(zeile1)
    print(f'\u2502{nr:{spalte1}}\u2502 {bz:{spBez}} \u2502')
    print(zeile2 + (
        f' {"Vorgänger":15} {vorgaenger}' if len(vorgaenger) > 0 else ""))
    print(f'\u2502{fa:{spalte1}}\u2502{dr:{spalte2}}\u2502{"":{spalte3}}\u2502{fe:{spalte4}}\u2502' + (
        f' {"Nachfolger":15} {nachfolger}' if len(nachfolger) > 0 else ""))
    print(zeile3 + " " + kritischerWeg)
    print(f'\u2502{sa:{spalte1}}\u2502{gp:{spalte2}}\u2502{fp:{spalte3}}\u2502{se:{spalte4}}\u2502')
    print(zeile4)
print("\nKritischer Pfad: ", end="")
for punkt in kritischerPfad:
    print(punkt, end=" ")
print("\n")

## finden der pfade

g = Graph(len(nrListe))

for i, nr in enumerate(nrListe):
    for vorgaenger in vorgaengerListe[i]:
        if vorgaenger != "":
            indx = nrListe.index(vorgaenger)
            g.addEdge(indx, i)

for i, nr in enumerate(nrListe):
    s = 0
    g.printAllPaths(s, i)

paths = g.getPaths()

lenList = {}

#längsten pfad pro vorgang finden

for i in range(len(paths)):
    maxlen = 0
    print(paths)
    for path in paths[i]:
        if len(path) > maxlen:
            maxlen = len(path)
    # if len(lenList) > 0:
    #     a = max(lenList.values())
    # else:
    #     a = 0
    lenList[i] = maxlen
sizeList = []

fieldList=[]

for i in range(1, max(lenList.values()) + 1):
    field = []
    counter=0
    for k, l in enumerate(lenList.values()):
        if l == i:
            counter+=1
            fieldList.append(k)
    sizeList.append(counter)

print(fieldList)

## darstellung in opencv2

blank = np.ones((1080, 1920, 3), dtype="uint8") * 200
widthEbene = 1536 // len(sizeList)
heightHalf = 648 // (max(sizeList) * 2)

oldpt = [192, 540]
zeroPosListe = []

for i, size in enumerate(sizeList):
    x1 = 192 + widthEbene * i
    x2 = 192 + widthEbene * (i + 1)
    j = sizeList[i]
    for j in range(sizeList[i], -sizeList[i], -2):
        y1 = 540 - (j) * heightHalf
        zeroPosListe.append([x1, y1])

for i in range(len(kritischerPfad)):
    kritischerPfad[i] = nrListe.index(kritischerPfad[i]) + 1

widthEbene2 = int(widthEbene * 0.9)
heightEbene = int(heightHalf * 1.8)
widthCell = widthEbene2 // 4
heightCell = heightEbene // 3

for i, pos in enumerate(zeroPosListe):
    feld = fieldList[i]
    x1 = pos[0] + int(.05 * widthEbene)
    y1 = pos[1] + int(.1 * heightHalf)
    zeroPosListe[i] = [x1, y1]
    x2 = x1 + int(0.9 * widthEbene)
    y2 = y1 + int(1.8 * heightHalf)
    colorK = (0, 0, 0)
    if feld+1 in kritischerPfad:
        colorK = (0, 0, 255)
    else:
        colorK = (0, 0, 0)
    # cv.rectangle(blank, (x1, y1), (x2, y2), colorK, thickness=2)
    x = zeroPosListe[feld][0]
    y = zeroPosListe[feld][1]
    dotList = []
    for j in range(0, 4):
        for k in range(0, 5):
            if not ((k == 2 and j == 0) or (k == 3 and j == 0)):
                dotList.append([x + k * widthCell, y + j * heightCell, j * 4 + k])

    for k, dot in enumerate(dotList):
        for dot2 in dotList:
            if (dot[0] == dot2[0] or dot[1] == dot2[1]):
                cv.line(blank, dot[:2], dot2[:2], colorK, thickness=4)

    cellList = []

    for j in range(0, 3):
        for k in range(0, 4):
            if not ((k == 2 and j == 0) or (k == 3 and j == 0)):
                zelle = j * 4 + k - 2 if j * 4 + k >= 4 else j * 4 + k
                cellList.append([x + k * widthCell, y + j * heightCell])
                # cv.putText(blank, str(zelle), (x + k * widthCell, y + j * heightCell), cv.FONT_HERSHEY_PLAIN, 0.8,
                # colorK)

    vorgang = vorgangsListe[feld]
    textListe = [vorgang["nr"], vorgang["bezeichnung"], vorgang["faz"], vorgang["dauer"], "", vorgang["fez"],
                 vorgang["saz"], vorgang["gp"], vorgang["fp"], vorgang["sez"]]
    for k, posi in enumerate(cellList):
        x = int(posi[0] + .5 * widthCell - 5)
        y = int(posi[1] + .5 * heightCell + 5)
        cv.putText(blank, textListe[k], (x, y), cv.FONT_HERSHEY_PLAIN, 1.3, colorK, thickness=2)

    for vorgaenger in vorgaengerListe[feld]:
        if vorgaenger != "":
            indx = nrListe.index(vorgaenger)
            x1 = zeroPosListe[feld][0]
            y1 = zeroPosListe[feld][1]
            x2 = zeroPosListe[indx][0]
            y2 = zeroPosListe[indx][1]
            if indx + 1 in kritischerPfad and feld + 1 in kritischerPfad:
                colorK = (0, 0, 255)
            else:
                colorK = (0, 0, 0)
            cv.line(blank, (x1, int(y1 + .5 * heightEbene)), (x2 + widthEbene2, int(y2 + .5 * heightEbene)), colorK,
                    thickness=4)

cv.namedWindow("Netzplan")  # Create a named window
cv.moveWindow("Netzplan", 0, 0)  # Move it to (40,30)
cv.imshow("Netzplan", blank)
cv.waitKey(0)
