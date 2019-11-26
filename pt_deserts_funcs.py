from requests import Session
from json import loads
from math import radians, cos, sin, asin, sqrt
from os import walk, path

def safeGet(dictName, *keys):

	responseBuilder = dictName
	
	for key in keys:
		try:
			responseBuilder = responseBuilder[key]
		except (KeyError, IndexError):
			return None
			
	return responseBuilder

def getBorderLengths(north, south, east, west):

  # convert coordinate boundaries to radians
  north = radians(north)
  south = radians(south)
  east = radians(east)
  west = radians(west)
  
  # https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
  eqRadius = 6378137     # radius of earth in meters at equator
  polarRadius = 6356752   # radius of earth in meters at poles
  
  # calculate approx radius based on where it is between eq and pole
  # assuming a linear relationship between abs(latitude) and radius
  diffRadius = eqRadius - polarRadius
  avgAbsLat = abs((north - south) / 2)
  approxRadius = (((90 - avgAbsLat) / 90) * diffRadius) + polarRadius
  
  # NW-NE border
  dLat = north - north
  dLon = west - east
  step1 = sin(dLat / 2)**2 + cos(north) * cos(north) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  nBorder = step2 * approxRadius                                          # length of north border in meters
  
  # SW-SE border
  dLat = south - south
  dLon = west - east
  step1 = sin(dLat / 2)**2 + cos(south) * cos(south) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  sBorder = step2 * approxRadius                                          # length of north border in meters
  
  # NE-SE border
  dLat = north - south
  dLon = east - east
  step1 = sin(dLat / 2)**2 + cos(south) * cos(north) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  eBorder = step2 * approxRadius                                          # length of north border in meters
  
  # NW-SW border
  dLat = north - south
  dLon = west - west
  step1 = sin(dLat / 2)**2 + cos(south) * cos(north) * sin(dLon / 2)**2   # Haversine formula
  step2 = 2 * asin(sqrt(step1))                                           # Haversine formula
  wBorder = step2 * approxRadius                                          # length of north border in meters
  
  return {"north": nBorder, "south": sBorder, "east": eBorder, "west": wBorder}
  
def cacheArea(areaName, north, south, east, west, hereParameters, testHeight = None, testWidth = None):

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

  session = Session()
  here_credentials = open("credentials/here_credentials.txt", "r")
  app_id = here_credentials.readline()[:-1]
  app_code = here_credentials.readline()[:-1]
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
      responseDict = loads(responseJSON.text)
      distToPT = safeGet(responseDict, "results", "items", 0, "distance")
      row += [distToPT]
      j += 1
    grid += [row]
    i += 1
    
  # write data to file
  newCacheFile = open("data/"+areaName+".grid", "w") # should consider changing this to "a" for production so we don't lose good data
  newCacheFile.write(areaName+"\n")
  newCacheFile.write(str(north)+" "+str(south)+" "+str(east)+" "+str(west)+"\n")
  newCacheFile.write(str(testHeight)+" "+str(testWidth)+"\n")
  for i in range(gridHeight):
    for j in range(gridWidth-1):
      newCacheFile.write(str(grid[i][j])+" ")
    newCacheFile.write(str(grid[i][gridWidth-1])+"\n")
  newCacheFile.close()
  
  return
  
def loadFromCache(areaName):

  FILE = open("data/"+areaName+".grid", "r")
  areaName = FILE.readline()[:-1]
  NSEW = FILE.readline()[:-1].split(" ")
  HxW = FILE.readline()[:-1].split(" ")
  data = []
  for row in range(int(HxW[0])):
    data += [FILE.readline()[:-1].split(" ")]
    
  return {"areaName": areaName, "NSEW": NSEW, "HxW": HxW, "data": data}
  
def cached(areaName):

  filename = [areaName+".grid"]
  path = "data"
  
  for files in walk(path, topdown = True):
    if filename in files:
      return True
      
  return False
  
def getMostIsolatedCache(areaName, testHeight = None, testWidth = None):

  # for testing
  if testHeight is not None:
    gridHeight = testHeight # default 181 for MPLS
  if testWidth is not None:
    gridWidth = testWidth # default 107 for MPLS
    
  numGridPoints = gridHeight * gridWidth
  
  needToCheck = {}
  for i in range(gridHeight + 2):         # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridHeight
    for j in range(gridWidth + 2):        # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridWidth
      needToCheck.update({(i,j): 1})      # initialize every point to 1
 
  maxDist = -1
  maxDistData = [{(0,0): -1}]
  pythag = 100*sqrt(2)               # i.e. the length of a diagonal between two points on the grid in meters
  i = 1
  j = 1
  numChecks = 0
  gridFile = loadFromCache(areaName)
  gridData = gridFile["data"]
  while i <= gridHeight:
    while j <= gridWidth:
      if needToCheck[(i,j)]:
        numChecks += 1
        distToPT = int(gridData[i-1][j-1])
        #hereParameters.update({"at": str(north - ((i-1)*dLat))+","+str(west + ((j-1)*dLon))})
        #responseJSON = session.get(request_search_url, params = hereParameters)
        #responseDict = loads(responseJSON.text)
        #distToPT = safeGet(responseDict, "results", "items", 0, "distance")
        if distToPT is None:
          # reset all non - None results but keep adding on to any existing none results if that makes sense
          maxDistData += [{(i,j): ">2km"}] # None means that we're more than 2km away from nearest PT stop
          j += 1
        else:
          if distToPT < (maxDist - pythag):
            for k in (i-1, i, i+1):
              for l in (j-1, j, j+1):
                needToCheck[(k,l)] = 0   # sets all neighbors and itself to 0, signifying that they're not the most isolated
            j += 2                       # since we know we can skip the E neighbor
          elif distToPT < (maxDist - 100):
            needToCheck[(i,j)] = 0       # not the most isolated
            needToCheck[(i-1,j)] = 0     # N neighbor not the most isolated
            needToCheck[(i+1,j)] = 0     # S neighbor ''
            needToCheck[(i,j+1)] = 0     # E neighbor ''
            needToCheck[(i,j-1)] = 0     # W neighbor ''
            j += 2                       # since we know we can skip the E neighbor
          elif distToPT >= maxDist:
            if distToPT == maxDist:
              maxDistData += [{(i,j): distToPT}]
            else:
              maxDist = distToPT
              maxDistData = maxDistData = [{(0,0): -1}]
              maxDistData += [{(i,j): distToPT}]
            j += 1
          else:
            needToCheck[(i,j)] = 0       # not the most isolated
            j += 1
      else:
        j += 1
    j = 1
    i += 1
        
  return [maxDistData[1:], numChecks, numGridPoints]
	
def getMostIsolatedHere(areaName, north, south, east, west, hereParameters, testHeight = None, testWidth = None):

  session = Session() # 250,000 per month (3rd to 2nd)
  here_credentials = open("here_credentials.txt", "r") # formatted as <app_id>\n<app_code>, see README for more details
  app_id = here_credentials.readline()[:-1] # gets rid of the newline character
  app_code = here_credentials.readline()[:-1] # gets rid of the newline character
  here_credentials.close()
  request_search_url = "https://places.cit.api.here.com/places/v1/browse/pt-stops" # only remove .cit for prod

  borderLengths = getBorderLengths(north, south, east, west)   # a dictionary of border lengths in meters
  # print(borderLengths)
  gridHeight = int(borderLengths["east"] / 100)                                    # number of 100m N-S segments
  gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100)   # number of 100m W-E segments
  
  dLat = abs(north - south) / gridHeight
  dLon = abs(east - west) / gridWidth
  
  at = str(north)+","+str(west)
  hereParameters.update({"at": at})
    
  # for testing to limit calls to API
  if testHeight is not None:
    gridHeight = testHeight # default 181 for MPLS
  if testWidth is not None:
    gridWidth = testWidth # default 107 for MPLS
    
  numGridPoints = gridHeight * gridWidth
  
  needToCheck = {}
  for i in range(gridHeight + 2):         # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridHeight
    for j in range(gridWidth + 2):        # we want dummy borders to avoid special cases, so the actual grid is in 1 to gridWidth
      needToCheck.update({(i,j): 1})      # initialize every point to 1
 
  maxDist = -1
  maxDistData = [{(0,0): -1}]
  pythag = 100*sqrt(2)               # i.e. the length of a diagonal between two points on the grid in meters
  i = 1
  j = 1
  numChecks = 0
  while i <= gridHeight:
    while j <= gridWidth:
      if needToCheck[(i,j)]:
        numChecks += 1
        hereParameters.update({"at": str(north - ((i-1)*dLat))+","+str(west + ((j-1)*dLon))})
        # print(hereParameters["at"])
        responseJSON = session.get(request_search_url, params = hereParameters)
        responseDict = loads(responseJSON.text)
        distToPT = safeGet(responseDict, "results", "items", 0, "distance")
        if distToPT is None:
          # reset all non - None results but keep adding on to any existing none results if that makes sense
          maxDistData += [{(i,j): ">2km"}] # None means that we're more than 2km away from nearest PT stop
          j += 1
        else:
          if distToPT < (maxDist - pythag):
            for k in (i-1, i, i+1):
              for l in (j-1, j, j+1):
                needToCheck[(k,l)] = 0   # sets all neighbors and itself to 0, signifying that they're not the most isolated
            j += 2                       # since we know we can skip the E neighbor
          elif distToPT < (maxDist - 100):
            needToCheck[(i,j)] = 0       # not the most isolated
            needToCheck[(i-1,j)] = 0     # N neighbor not the most isolated
            needToCheck[(i+1,j)] = 0     # S neighbor ''
            needToCheck[(i,j+1)] = 0     # E neighbor ''
            needToCheck[(i,j-1)] = 0     # W neighbor ''
            j += 2                       # since we know we can skip the E neighbor
          elif distToPT >= maxDist:
            if distToPT == maxDist:
              maxDistData += [{(i,j): distToPT}]
            else:
              maxDist = distToPT
              maxDistData = maxDistData = [{(0,0): -1}]
              maxDistData += [{(i,j): distToPT}]
            j += 1
          else:
            needToCheck[(i,j)] = 0       # not the most isolated
            j += 1
      else:
        j += 1
    j = 1
    i += 1
        
  return [maxDistData[1:], numChecks, numGridPoints]
