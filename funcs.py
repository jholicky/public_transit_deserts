import requests
import json
from math import radians, cos, sin, asin, sqrt
import os



# To do:
# ~ Consolidate the functions getMostIsolatedHere and getMostIsolatedFile into one function that uses context to 
#   determine whether to go to the API or to a saved file.
# ~ Make better and more widespread use of safeGet.
# ~ Look into improving precision of getBorderLengths.
# ~ Make legalCoordinates criteria more sophisticated.
# ~ 





# Determines if a set of NSEW coordinates are logical or not
def legalCoordinates(coordinates):
  # N >= S, E >= W
  return float(coordinates[0]) >= float(coordinates[1]) and float(coordinates[2]) >= float(coordinates[3])







# Utility function to get values from iterables where we aren't sure if they exist or not
def safeGet(dictName, *keys):

	responseBuilder = dictName
	
	for key in keys:
		try:
			responseBuilder = responseBuilder[key]
		except (KeyError, IndexError):
			return None
			
	return responseBuilder







# Given a spherical rectangle defined by its extreme coordinates, find the lengths of the sides of the rectangle and 
# return them in a dictionary.
def getBorderLengths(north, south, east, west):

  # convert coordinate boundaries to radians
  north = radians(north)
  south = radians(south)
  east = radians(east)
  west = radians(west)
  
  # https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
  eqRadius = 6378137     # radius of earth in meters at equator
  polarRadius = 6356752   # radius of earth in meters at poles
  
  # calculate approx radius based on where we are between eq and pole
  # assuming a linear relationship between abs(latitude) and radius for simplicity
  diffRadius = eqRadius - polarRadius
  avgAbsLat = abs((north - south) / 2)
  approxRadius = (((90 - avgAbsLat) / 90) * diffRadius) + polarRadius
  
  # NW-NE edge
  dLat = north - north
  dLon = west - east
  step1 = sin(dLat / 2)**2 + cos(north) * cos(north) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  nBorder = step2 * approxRadius                                          # length of north border in meters
  
  # SW-SE edge
  dLat = south - south
  dLon = west - east
  step1 = sin(dLat / 2)**2 + cos(south) * cos(south) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  sBorder = step2 * approxRadius                                          # length of south border in meters
  
  # NE-SE edge
  dLat = north - south
  dLon = east - east
  step1 = sin(dLat / 2)**2 + cos(south) * cos(north) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  eBorder = step2 * approxRadius                                          # length of east border in meters
  
  # NW-SW edge
  dLat = north - south
  dLon = west - west
  step1 = sin(dLat / 2)**2 + cos(south) * cos(north) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  wBorder = step2 * approxRadius                                          # length of west border in meters
  
  return {"north": nBorder, "south": sBorder, "east": eBorder, "west": wBorder}
  
  
  
  
  
  
  
# Given a name, coordinates, and optional test grid size, make a .grid file where each data point is the distance 
# from the nearest public transit stop, as given by the Here API.  
def saveArea(areaName, north, south, east, west, hereParameters, testHeight = None, testWidth = None):

  # The data file areaName.grid created by this function is formatted in the following way:
  #
  #               areaName
  #               north south east west
  #               gridHeight gridWidth
  #                    g(0,0)         g(0,1)   g(0,2)   ...         g(0,gridWidth-1)
  #                    g(1,0)         g(1,1)   g(1,2)   ...         g(1,gridWidth-1)
  #                     ...            ...      ...     ...               ...
  #               g(gridHeight-1,0)    ...      ...     ...    g(gridHeight-1,gridWidth-1)
  #
  # with the elements in each row of the grid deliminated by " " (space character)

  session = requests.Session()
  here_credentials = open("credentials/here_credentials.txt", "r")
  app_id = here_credentials.readline()[:-1]
  app_code = here_credentials.readline()[:-1]
  here_credentials.close()
  request_search_url = "https://places.cit.api.here.com/places/v1/browse/pt-stops"
  
  borderLengths = getBorderLengths(north, south, east, west)
  
  gridHeight = int(borderLengths["east"] / 100) # 181 for MPLS
  gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100) # 107 for MPLS
  
  dLat = abs(north - south) / gridHeight
  dLon = abs(east - west) / gridWidth
  
  # for testing to limit calls to API
  if testHeight is not None:
    gridHeight = testHeight # use test parameter
  if testWidth is not None:
    gridWidth = testWidth # use test parameter
    
  numGridPoints = gridHeight * gridWidth
  
  at = str(north)+","+str(west)
  hereParameters.update({"at": at})
  
  i = 0
  j = 0
  grid = []
  while i < gridHeight:
    row = []
    j = 0
    while j < gridWidth:
      hereParameters.update({"at": str(north - ((i)*dLat))+","+str(west + ((j)*dLon))})
      responseJSON = session.get(request_search_url, params = hereParameters)
      responseDict = json.loads(responseJSON.text)
      distToPT = safeGet(responseDict, "results", "items", 0, "distance")
      row += [distToPT]
      j += 1
    grid += [row]
    i += 1
    
  # write data to file
  newGridFile = open("data/"+areaName+".grid", "w") # should consider changing this to "a" for production so we don't lose good data
  newGridFile.write(areaName+"\n")
  newGridFile.write(str(north)+" "+str(south)+" "+str(east)+" "+str(west)+"\n")
  newGridFile.write(str(gridHeight)+" "+str(gridWidth)+"\n")
  for i in range(gridHeight):
    for j in range(gridWidth-1):
      newGridFile.write(str(grid[i][j])+" ")
    newGridFile.write(str(grid[i][gridWidth-1])+"\n")
  newGridFile.close()
  
  return
  
  
  
  
  
  

# Checks if there is a file in ./data that is called areaName.grid and returns a boolean.  
def saved(areaName):

  filename = areaName+".grid"
  path = "data"
  
  for files in os.walk(path, topdown = True):
    if filename in files[2]:
      return True
      
  return False
  
  
  
  
  
  
  
# Given a name, loads the .grid file with that name and returns its data in a dictionary.  
def loadFromFile(areaName):

  if saved(areaName):
    FILE = open("data/"+areaName+".grid", "r")
    areaName = FILE.readline()[:-1]
    NSEW = FILE.readline()[:-1].split(" ")          # [:-1] gets rid of newline character
    HxW = FILE.readline()[:-1].split(" ")           # [:-1] gets rid of newline character
    data = []                                       # data is a list where each row is a list of elements in that row
    numRows = int(HxW[0])
    for row in range(numRows):
      data += [FILE.readline()[:-1].split(" ")]
  else:
    return 1                                        # up to the caller to handle this error or not
    
  FILE.close()
  return {"areaName": areaName, "NSEW": NSEW, "HxW": HxW, "data": data}
  
  
  
  
  
  
  
# Given a name, coordinates, and optional test grid size, goes straight to the Here API and searches for the point 
# that is furthest away from the nearest public transit stop.
def getMostIsolatedHere(areaName, coordinates, hereParameters, testHeight = None, testWidth = None):

  session = requests.Session()
  here_credentials = open("credentials/here_credentials.txt", "r")
  app_id = here_credentials.readline()[:-1]
  app_code = here_credentials.readline()[:-1]
  here_credentials.close()
  request_search_url = "https://places.cit.api.here.com/places/v1/browse/pt-stops"

  north = float(coordinates[0])
  south = float(coordinates[1])
  east = float(coordinates[2])
  west = float(coordinates[3])
  borderLengths = getBorderLengths(north, south, east, west)
  gridHeight = int(borderLengths["east"] / 100)
  gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100)
  
  dLat = abs(north - south) / gridHeight
  dLon = abs(east - west) / gridWidth
  
  if testHeight is not None:
    gridHeight = testHeight
  if testWidth is not None:
    gridWidth = testWidth
    
  numGridPoints = gridHeight * gridWidth
  
  at = str(north)+","+str(west)
  hereParameters.update({"at": at})
  
  needToCheck = []
  for i in range(gridHeight + 2):         # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridHeight
    row = []
    for j in range(gridWidth + 2):        # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridWidth
      row += [1]
    needToCheck += [row]                  # initialize every point to 1
    
  maxDist = -1
  maxDistData = [(0,0)]
  pythag = 100*sqrt(2)                    # i.e. the length of a diagonal between two points on the grid in meters
  numChecks = 0
  lostCause = False                       # this gets set to True if we start dealing with None (>2km) distance values
  i = 1
  j = 1
  
  while i <= gridHeight:
    while j <= gridWidth:
      if needToCheck[i][j]:
        numChecks += 1
        try:
          hereParameters.update({"at": str(north - ((i-1)*dLat))+","+str(west + ((j-1)*dLon))})
          responseJSON = session.get(request_search_url, params = hereParameters)
          responseDict = json.loads(responseJSON.text)
          distToPT = int(safeGet(responseDict, "results", "items", 0, "distance"))
        except (ValueError, TypeError):
          if lostCause: # we already found None (>2km) values
            maxDistData += [(i-1,j-1)]
          else: # this is our first None (>2km) value
            lostCause = True
            maxDistData = [(0,0), (i-1,j-1)]
            maxDist = ">2000" # None means that we're more than 2km away from nearest PT stop
        if not lostCause:
          if distToPT < (maxDist - pythag):
            for k in (i-1, i, i+1):
              for l in (j-1, j, j+1):
                needToCheck[k][l] = 0   # sets all neighbors and itself to 0, signifying that they're not the most isolated
            j += 2                      # since we know we can skip the E neighbor
          elif distToPT < (maxDist - 100):
            needToCheck[i][j] = 0       # not the most isolated
            needToCheck[i-1][j] = 0     # N neighbor not the most isolated
            needToCheck[i+1][j] = 0     # S neighbor ''
            needToCheck[i][j+1] = 0     # E neighbor ''
            needToCheck[i][j-1] = 0     # W neighbor ''
            j += 2                      # since we know we can skip the E neighbor
          elif distToPT >= maxDist:
            if distToPT == maxDist:
              maxDistData += [(i-1,j-1)]
            else:
              maxDist = distToPT
              maxDistData = [(0,0)]
              maxDistData += [(i-1,j-1)]
            j += 1
          else:
            needToCheck[i][j] = 0       # not the most isolated
            j += 1
        else:
          j+= 1
      else:
        j += 1
    j = 1
    i += 1
    
  newMaxDistData = []
  for e in maxDistData[1:]:
    lat = north - e[0]*dLat
    lon = west + e[1]*dLon
    newMaxDistData += [(lat, lon)]
  
  return [newMaxDistData, maxDist, numChecks, numGridPoints]
  
  
  
  
  
  
  
# Given a name, coordinates, and optional test grid size, goes to the relevant file in ./data and searches for 
# the point that is furthest away from the nearest public transit stop.
def getMostIsolatedFile(areaName, testHeight = None, testWidth = None):
  
  gridFile = loadFromFile(areaName)
  
  borderLengths = getBorderLengths(float(gridFile["NSEW"][0]), float(gridFile["NSEW"][1]), 
                                   float(gridFile["NSEW"][2]), float(gridFile["NSEW"][3]))   # a dictionary of border lengths in meters
  gridHeight = int(borderLengths["east"] / 100)                                    # number of 100m N-S segments
  gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100)   # number of 100m W-E segments
  
  dLat = abs(float(gridFile["NSEW"][0]) - float(gridFile["NSEW"][1])) / gridHeight
  dLon = abs(float(gridFile["NSEW"][2]) - float(gridFile["NSEW"][3])) / gridWidth
  

  gridHeight = int(gridFile["HxW"][0])
  gridWidth = int(gridFile["HxW"][1])
  gridData = gridFile["data"]

  # for testing
  if testHeight is not None:
    gridHeight = testHeight # default 181 for MPLS
  if testWidth is not None:
    gridWidth = testWidth # default 107 for MPLS
    
  numGridPoints = gridHeight * gridWidth
  
  needToCheck = []
  for i in range(gridHeight + 2):         # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridHeight
    row = []
    for j in range(gridWidth + 2):        # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridWidth
      row += [1]
    needToCheck += [row]                  # initialize every point to 1
  
  maxDist = -1
  maxDistData = [(0,0)]
  pythag = 100*sqrt(2)                    # i.e. the length of a diagonal between two points on the grid in meters
  numChecks = 0
  lostCause = False                       # this gets set to True if we start dealing with None (>2km) distance values
  i = 1
  j = 1
  
  while i <= gridHeight:
    while j <= gridWidth:
      if needToCheck[i][j]:
        numChecks += 1
        try:
          distToPT = int(gridData[i-1][j-1])
        except ValueError:
          if lostCause: # we already found None (>2km) values
            maxDistData += [(i-1,j-1)]
          else: # this is our first None (>2km) value
            lostCause = True
            maxDistData = [(0,0), (i-1,j-1)]
            maxDist = ">2000" # None means that we're more than 2km away from nearest PT stop
        if not lostCause:
          if distToPT < (maxDist - pythag):
            for k in (i-1, i, i+1):
              for l in (j-1, j, j+1):
                needToCheck[k][l] = 0   # sets all neighbors and itself to 0, signifying that they're not the most isolated
            j += 2                      # since we know we can skip the E neighbor
          elif distToPT < (maxDist - 100):
            needToCheck[i][j] = 0       # not the most isolated
            needToCheck[i-1][j] = 0     # N neighbor not the most isolated
            needToCheck[i+1][j] = 0     # S neighbor ''
            needToCheck[i][j+1] = 0     # E neighbor ''
            needToCheck[i][j-1] = 0     # W neighbor ''
            j += 2                      # since we know we can skip the E neighbor
          elif distToPT >= maxDist:
            if distToPT == maxDist:
              maxDistData += [(i-1,j-1)]
            else:
              maxDist = distToPT
              maxDistData = [(0,0)]
              maxDistData += [(i-1,j-1)]
            j += 1
          else:
            needToCheck[i][j] = 0       # not the most isolated
            j += 1
        else:
          j+= 1
      else:
        j += 1
    j = 1
    i += 1
    
  newMaxDistData = []
  for e in maxDistData[1:]:
    lat = float(gridFile["NSEW"][0]) - e[0]*dLat
    lon = float(gridFile["NSEW"][3]) + e[1]*dLon
    newMaxDistData += [(lat, lon)]
  
  return [newMaxDistData, maxDist, numChecks, numGridPoints]
  
  
  
