from requests import Session
from json import loads
from pt_deserts_funcs import safeGet, cacheArea, cached, getMostIsolatedHere, getMostIsolatedCache, loadFromCache
from sys import argv, exit







# To do:
#   - Implement caching so that we don't have to call the API more than once per grid point per program run
#     - caching process complete
#     - able to check if a city/area is cached (user must spell correctly)
#     - need to implement using cache vs here if available
#   - Better printing for the most isolated points
#   - I/O for parameters (i.e. maximum calls to API allowed, city coordinates, test size)
#   - Find a way to get city boundaries without asking the user (for major cities)
#   - Wrap everything in a C I/O loop





        
# Minneapolis city limits (simplified):
north = 45.053031
south = 44.889767
east = -93.193761
west = -93.330048
# About 18.17km north to south, about 10.72-10.75km east to west.
# We can just divide the city into 100m by 100m squares and find the max distance, but we shouldn't have to 
# check each point:
#   Theory: If a point is less than (max - 100)m away from the nearest PT stop, then its neighbors are also not the max.
#   Answer: Yes, this allows us to rule out its 4 neighbors (N,S,E,W), but not its other 4 neighbors (NE,SE,SW,NW). 
#            Because we don't know which direction the nearest stop is in, we need to have 1 criteria that 
#            allows us to exclude all 8 of its neighbors.
#   Theory: If a point is less than (max - 100sqrt2)m away from the nearest PT stop, then all 8 of its neighbors 
#           are also not the max.
#   Answer: Yes, this allows us to rule out all 8 neighbors (N,S,E,W,NE,SE,SW,NW). This could really cut down on 
#           the number of comparisons and calls to the API.

#session = Session() # 250,000 per month (3rd to 2nd)
here_credentials = open(
  "credentials/here_credentials.txt", 
  "r"
) # formatted as <app_id>\n<app_code>, see README for more details
app_id = here_credentials.readline()[:-1] # gets rid of the newline character
app_code = here_credentials.readline()[:-1] # gets rid of the newline character
request_search_url = "https://places.cit.api.here.com/places/v1/browse/pt-stops" # only remove .cit for prod

#at = "45.147045,-93.123926"
    
hereParameters = {"at": "", "app_id": app_id, "app_code": app_code}
#responseJSON = session.get(request_search_url, params = hereParameters)
#responseDict = loads(responseJSON.text)

#print(safeGet(responseDict, "results", "items", 0, "distance")) # the distance from at to the closest PT stop

areaName = argv[1]
testHeight = int(argv[2])
testWidth = int(argv[3])

# check to make sure I don't actualy waste a bunch of API calls during testing, 
# remove or make much larger for production build
if testHeight * testWidth >= 500:
  print("Test limit exceeded")
  exit()

#print("Number of arguments "+str(len(argv)))
print("Grid Size: "+str(testHeight)+"x"+str(testWidth))

print(cached(areaName))

cacheArea(areaName, north, south, east, west, hereParameters, testHeight, testWidth)

#exit()

if not cached(areaName):
  print("not cached")
  exit()
  results = getMostIsolatedHere(areaName, north, south, east, west, hereParameters, testHeight, testWidth)
else:
  print("cached")
  print(loadFromCache(areaName))
  results = getMostIsolatedCache(areaName, testHeight, testWidth)
  
print("Most Isolated Grid Point(s) (Public Transit Desert(s)):")
print(results[0]) # print this is a more user-friendly way, i.e. with actual lat/lon instead of grid coordinates
print("Number of grid points checked: "+str(results[1])+" out of "+str(results[2]))

