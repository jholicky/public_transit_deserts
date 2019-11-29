from requests import Session
from json import loads
from pt_deserts_funcs import safeGet, cacheArea, cached, getMostIsolatedHere, getMostIsolatedCache, loadFromCache
from sys import argv, exit
from os import walk, path

here_credentials = open(
  "credentials/here_credentials.txt", 
  "r"
) # formatted as <app_id>\n<app_code>, see README for more details
app_id = here_credentials.readline()[:-1] # gets rid of the newline character
app_code = here_credentials.readline()[:-1] # gets rid of the newline character
hereParameters = {"at": "", "app_id": app_id, "app_code": app_code}

print("Public Transit Deserts by Jake Holicky")
print("github.com/jholicky/public_transit_deserts")
print("Commands:")
print("  ~ cache <area name> <north> <south> <east> <west> <testHeight = None> <testWidth = None>")
print("                            : saves an area named area name with given coordinates")
print("                              and optional grid testHeight and testWidth")
print("  ~ iscached <area name>    : checks if the user has cached a given area name")
print("  ~ ptdeserts <area name>   : uses a cached area to find the most isolated grid point(s) from public transit")
print("  ~ summary                 : prints a summary of all cache files created")
print("  ~ info <area name>        : gives information on a cached file if it exists")
print("  ~ quit                    : quits the program")

while 1:
  cmd = input("PTD> ")
  
  cmd = cmd.split(" ")
  
  numArgs = len(cmd) # includes command arg
  
  if cmd[0] == "cache" and (numArgs == 6 or numArgs == 8):
    if cached(cmd[1]):
      print("WARNING: there is already a .grid file named "+cmd[1]+".grid, do you want to overwrite it?")
    else: # not cached yet
      print("There is not a .grid file with this area name, do you wish to create one?")
    next = input("(y)es or (n)o: ")
    while 1:
      if next.lower() == "y" or next.lower() == "yes":
        print("You have chosen to overwrite "+cmd[1]+".grid")
        cmd[2] = float(cmd[2])
        cmd[3] = float(cmd[3])
        cmd[4] = float(cmd[4])
        cmd[5] = float(cmd[5])
        if numArgs == 6:
          borderLengths = getBorderLengths(cmd[2], cmd[3], cmd[4], cmd[5])
          gridHeight = int(borderLengths["east"] / 100) # 181 for MPLS
          gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100) # 107 for MPLS
          print("WARNING: you are about to cache an area with "+str(gridHeight*gridWidth)+" grid points, ")
          print("         i.e. "+str(gridHeight*gridWidth*100)+" square meters. Are you sure you wish to proceed?")
          next = input("(y)es or (n)o: ")
########### implement estimate of number of API calls
          if next.lower() == "y" or next.lower() == "yes":
            cacheArea(cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], hereParameters)
          elif next.lower() == "n" or next.lower() == "no":
            print("You have chosen to not overwrite "+cmd[1]+".grid")
            break
          else:
            print("unrecognized input, will not overwirte "+cmd[1]+".grid")
            break
        else: # numArgs == 8:
          gridHeight = int(cmd[6])
          gridWidth = int(cmd[7])
          print("WARNING: you are about to cache an area with "+str(gridHeight*gridWidth)+" grid points, ")
          print("         i.e. "+str(gridHeight*gridWidth*100)+" square meters. Are you sure you wish to proceed?")
          next = input("(y)es or (n)o: ")
########### implement estimate of number of API calls
          if next.lower() == "y" or next.lower() == "yes":
            cacheArea(cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], hereParameters, int(cmd[6]), int(cmd[7]))
          elif next.lower() == "n" or next.lower() == "no":
            print("You have chosen to not overwrite "+cmd[1]+".grid")
            break
          else:
            print("unrecognized input, will not overwirte "+cmd[1]+".grid")
            break
        break;
        
      elif next.lower() == "n" or next.lower() == "no":
        print("You have chosen to not overwrite "+cmd[1]+".grid")
        break;
        
      else:
        next = input("please respond with (y)es or (n)o")      
  
  elif cmd[0] == "iscached" and numArgs == 2:
    if cached(cmd[1]):
      print("Yes, there is a file named "+cmd[1]+".grid in ./data")
    else:
      print("No, there is not a file for that area name, use cache to create one")
  
  elif cmd[0] == "ptdeserts" and numArgs == 2:
########################################################################################################################
    print("")
  
  elif cmd[0] == "summary" and numArgs == 1:
    path = "data"
    for files in walk(path, topdown = True):
      for e in files[2]:
        FILE = loadFromCache(str(e)[:-5])
        # don't need to check for errors here since we only grab the file if it exists in the first place
        print(FILE["areaName"])
        print("  North:", FILE["NSEW"][0])
        print("  South:", FILE["NSEW"][1])
        print("  East:", FILE["NSEW"][2])
        print("  West:", FILE["NSEW"][3])
        print("  Grid Height:", FILE["HxW"][0], "("+str(100*int(FILE["HxW"][0]))+" meters)")
        print("  Grid Width:",FILE["HxW"][1], "("+str(100*int(FILE["HxW"][1]))+" meters)") 
        print("  Grid Size:", int(FILE["HxW"][0])*int(FILE["HxW"][1]), "("+str(100*int(FILE["HxW"][0])*int(FILE["HxW"][1]))+" square meters)")
        
  elif cmd[0] == "info" and numArgs == 2:
    if cached(cmd[1]):
      FILE = loadFromCache(cmd[1])
      print(FILE["areaName"])
      print("  North:", FILE["NSEW"][0])
      print("  South:", FILE["NSEW"][1])
      print("  East:", FILE["NSEW"][2])
      print("  West:", FILE["NSEW"][3])
      print("  Grid Height:", FILE["HxW"][0], "("+str(100*int(FILE["HxW"][0]))+" meters)")
      print("  Grid Width:",FILE["HxW"][1], "("+str(100*int(FILE["HxW"][1]))+" meters)") 
      print("  Grid Size:", int(FILE["HxW"][0])*int(FILE["HxW"][1]), "("+str(100*int(FILE["HxW"][0])*int(FILE["HxW"][1]))+" square meters)")
    else:
      print("Could not find a .grid file with that name, please check for spelling errors or ")
      print("first create a new file for that area name using cache")
  
  elif cmd[0] == "quit" and numArgs == 1:
    break;
    
  else:
    print("unrecognized input or not the correct number of arguments, please try again using one of the supported commands")
