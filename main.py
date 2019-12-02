from funcs import saveArea, saved, getMostIsolatedFile, getMostIsolatedHere, loadFromFile, getBorderLengths, legalCoordinates
from sys import argv, exit
import os



# To do:
# ~ Improve documentation / commenting.
# ~ More error checking, right now the user has a lot of freedom to screw up.
# ~ Improve handling of weird situations in the ptdesert command.



#########################################################################################
####### Sets up credentials for the Here API, see the README for more details #######
#########################################################################################



here_credentials = open(
  "credentials/here_credentials.txt", 
  "r"
)                                                     # formatted as <app_id>\n<app_code>, see README for more details
app_id = here_credentials.readline()[:-1]             # gets rid of the line terminating character
app_code = here_credentials.readline()[:-1]           # gets rid of the line terminating character
here_credentials.close()
hereParameters = {"at": "", "app_id": app_id, "app_code": app_code}



######################################################
####### Utility functions for the main program #######
######################################################



# Prints the list of available commands, their parameters, and their descriptions.
def showCommands():

  print("Commands:")
  print("  ~ commands                : shows this list of available commands")
  print("  ~ makegrid <area name> <north> <south> <east> <west> <testHeight = None> <testWidth = None>")
  print("                            : creates a .grid file for <area name> with given coordinates")
  print("                              and OPTIONAL grid <testHeight> and <testWidth>")
  print("  ~ isgrid <area name>      : checks if there is a .grid file for <area name>")
  print("  ~ ptdeserts <area name> <testHeight = None> <testWidth = None>")
  print("                            : finds the most isolated grid point(s) from public transit")
  print("                              with OPTIONAL grid <testHeight> and <testWidth>;")
  print("                              uses existing .grid files if applicable")
  print("  ~ summary                 : prints a summary of all grid files created")
  print("  ~ info <area name>        : gives information on the .grid file for <area name> if it exists")
  print("  ~ delete <area name>      : deletes <area name>.grid")
  print("  ~ clear                   : deletes all .grid files in ./data")
  print("  ~ quit                    : quits the program")
  print("\n*******Do not use spaces in area names (i.e. use NewYork, not New York)*******")
  
  return







# Makes a .grid file based on given arguments.
def makegrid(cmd, numArgs):
  if saved(cmd[1]):
    print("  WARNING: there is already a .grid file named "+cmd[1]+".grid, do you want to overwrite it?")
    next = input("    (y)es or (n)o?   ")
    if not (next.lower() == "y" or next.lower() == "yes"):
      i = 1
      while 1:
        # this follows the typical Windows and Linux convention of adding a number to the end of a 
        # file name to avoid having two files with the same name; it keeps looping until a suitable number is found
        newname = cmd[1]+str(i)
        if not saved(newname):
          print("  Creating a new file named "+newname+".grid.\n")
          break
        i += 1
      areaname = newname
    else:
      print("  Overwriting the file "+cmd[1]+".grid.\n")
      areaname = cmd[1]
    
  else: # no file named <cmd[1]>.grid
    areaname = cmd[1]
    
  north = float(cmd[2])
  south = float(cmd[3])
  east = float(cmd[4])
  west = float(cmd[5])
    
  if numArgs == 6:
    borderLengths = getBorderLengths(north, south, east, west)
    gridHeight = int(borderLengths["east"] / 100) # units: 100m
    gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100) # units: 100m
  else: # numArgs == 8
    gridHeight = int(cmd[6])
    gridWidth = int(cmd[7])
    
  gridSize = gridHeight * gridWidth
  print("  WARNING: you are about to make a grid with "+str(gridSize)+" grid points, ")
  print("  i.e. "+str(100*gridSize)+" square meters. Are you sure you wish to proceed?")
  next = input("    (y)es or (n)o?   ")
  if next.lower() == "y" or next.lower() == "yes":
    saveArea(areaname, north, south, east, west, hereParameters, gridHeight, gridWidth)
    print("  SUCCESS: "+areaname+".grid was created.")
  else:
    print("")
    print("  Would you like to change the gridHeight and gridWidth?")
    next = input("    (y)es or (n)o?   ")
    if next.lower() == "y" or next.lower() == "yes":
      print("")
      print("  Enter the gridHeight and gridWidth as follows:")
      print("    <gridHeight> <gridWidth>")
      next = input("    ")
      next = next.split(" ")
      gridHeight = int(next[0])
      gridWidth = int(next[1])
      print("  Using a "+str(gridHeight)+" by "+str(gridWidth)+" grid.")
      saveArea(areaname, north, south, east, west, hereParameters, gridHeight, gridWidth)
      print("  SUCCESS: "+areaname+".grid was created.")
    
  return areaname
  
  
  
##################################
####### MAIN PROGRAM START #######
##################################  
  

  
print("\nPublic Transit Deserts by Jake Holicky")
print("github.com/jholicky/public_transit_deserts\n")
showCommands() # prints list of commands, their parameters, and their descriptions

while 1:
  cmd = input("\nPTD> ")                        # signifies that a new command is ready to be accepted
  
  cmd = cmd.split(" ")                          # makes a list of the command arguments (each a string)
  
  print("")
  
  numArgs = len(cmd)                            # includes command arg
  
  
  ############################################################################################################
  ####### The following if/elif/else block is an infinite dispatcher that will keep accepting commands #######
  #######         from the user until they use the "quit" command (or until they CTRL+C out).          #######
  ############################################################################################################
  
  if cmd[0] == "commands" and numArgs == 1:
    showCommands()
  
  
  
  elif cmd[0] == "makegrid" and (numArgs == 6 or numArgs == 8):
    if legalCoordinates(cmd[2:6]): # error checking on coordinates
      makegrid(cmd, numArgs)
    else:
      print("Nonsensical coordinates given; please try again noting that <north> > <south> and <east> > <west>.")



  elif cmd[0] == "isgrid" and numArgs == 2:
    if saved(cmd[1]):
      print("  SUCCESS: there is a file named "+cmd[1]+".grid.")
    else:
      print("  FAILURE: there is no file named "+cmd[1]+".grid; use makegrid to create one.")
 
 
  
  elif cmd[0] == "ptdeserts" and numArgs == 2 or numArgs == 4:
    straightToHere = False              # keeps track of whether we need to go straight to the API or using a .grid file
    coordinates = []                    # a list of NSEW coordinates
    newcmd = []                         # needs to be reset every iteration due to the structure of this elif
    newNumArgs = 0                      # ''
    areaname = ""                       # ''
    if not saved(cmd[1]):               # if we don't have a file name cmd[1].grid
      print("  There is no existing "+cmd[1]+".grid, would you like to first make a .grid file (lots of API calls but ")
      print("  complete information), or would you like to only call the API as much as the algorithm requires (fewer ")
      print("  API calls but less complete information saved)?")
      next = input("    Make grid first, (y)es or (n)o?   ")
      if next.lower() == "y" or next.lower() == "yes":
        print("  Please enter the coordinates as follows: ")
        while 1:                                   # this loop will keep going until the user enters logical coordinates
          print("    <north> <south> <east> <west>")
          next = input("    ")
          next = next.split(" ")
          if legalCoordinates(next):
            break
          print("Nonsensical coordinates given; please try again noting that north >= south and east >= west.")
        coordinates = next
        newcmd = cmd[:2] + coordinates
        if numArgs == 4:      # if test grid height and width were given in the initial command, we need to include them
          newcmd += cmd[2:4]
          newNumArgs = 8
        else: # numArgs == 2
          newNumArgs = 6
        print("")
        areaname = makegrid(newcmd, newNumArgs) # this function returns the part of the new file name before the .grid
      else:
        print("")
        print("  Please enter the coordinates as follows: ")
        while 1:                                              # keeps going until logical coordinates given
          print("    <north> <south> <east> <west>")
          next = input("    ")
          next = next.split(" ")
          if legalCoordinates(next):
            break
          print("Nonsensical coordinates given; please try again noting that north >= south and east >= west.")
        coordinates = next
        areaname = cmd[1]
        straightToHere = True
    else:
      areaname = cmd[1]
      print("  There is an existing file named "+areaname+".grid, would you like to use the distances from that file?")
      next = input("    (y)es or (n)o?   ")
      if not (next.lower() == "y" or next.lower() == "yes"):
        print("")
        print("  Please enter the coordinates as follows: ")
        while 1:
          print("    <north> <south> <east> <west>")
          next = input("    ")
          next = next.split(" ")
          if legalCoordinates(next):
            break
          print("Nonsensical coordinates given; please try again noting that north >= south and east >= west.")
        coordinates = next
        areaname = cmd[1]
        straightToHere = True
    
    if numArgs == 2:
      if straightToHere:
        borderLengths = getBorderLengths(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]), float(coordinates[3]))
        gridHeight = int(borderLengths["east"] / 100) # units: 100m
        gridWidth = int(((borderLengths["north"] + borderLengths["south"]) / 2) / 100) # units: 100m
      else:
        FILE = loadFromFile(cmd[1])
        gridHeight = int(FILE["HxW"][0])
        gridWidth = int(FILE["HxW"][1])
    else: # numArgs == 4
      gridHeight = int(cmd[2])
      gridWidth = int(cmd[3])
      
    gridSize = gridHeight * gridWidth
      
    print("")
    print("  WARNING: you are about to search through a grid with "+str(gridSize)+" grid points, ")
    print("  i.e. "+str(100*gridSize)+" square meters. Are you sure you wish to proceed?")
    next = input("    (y)es or (n)o?   ")
    if next.lower() == "y" or next.lower() == "yes":
      if straightToHere:
        results = getMostIsolatedHere(areaname, coordinates, hereParameters, gridHeight, gridWidth)
      else: # use .grid file
        results = getMostIsolatedFile(areaname, gridHeight, gridWidth)
    
      print("")
      print("  The following grid point(s) are the furthest away from any public transit stop:")
      for e in results[0]:
        print("    "+str(e[0])+", "+str(e[1]), ":", results[1], "meters")
      print("  The algorithm had to look at", results[2], "of", results[3], "grid points to come to this solution.")
      
    else:
      print("")
      print("  Would you like to change the gridHeight and gridWidth?")
      next = input("    (y)es or (n)o?   ")
      if next.lower() == "y" or next.lower() == "yes":
        print("")
        print("  Enter the gridHeight and gridWidth as follows:")
        print("    <gridHeight> <gridWidth>")
        next = input("    ")
        next = next.split(" ")
        gridHeight = int(next[0])
        gridWidth = int(next[1])
        print("  Using a "+str(gridHeight)+" by "+str(gridWidth)+" grid.")
        if straightToHere:
          results = getMostIsolatedHere(areaname, coordinates, hereParameters, gridHeight, gridWidth)
        else: # use .grid file
          results = getMostIsolatedFile(areaname, gridHeight, gridWidth)
          
        print("")
        print("  The following grid point(s) are the furthest away from any public transit stop:")
        for e in results[0]:
          print("    "+str(e[0])+", "+str(e[1]), ":", results[1], "meters")
        print("  The algorithm had to look at", results[2], "of", results[3], "grid points to come to this solution.")

 
  
  elif cmd[0] == "summary" and numArgs == 1:
    path = "data"
    for files in os.walk(path, topdown = True):
      for e in files[2]:
        FILE = loadFromFile(str(e)[:-5])
        # don't need to check for errors here since we only grab the file if it exists in the first place
        print("  "+FILE["areaName"])
        print("    North:", FILE["NSEW"][0])
        print("    South:", FILE["NSEW"][1])
        print("    East:", FILE["NSEW"][2])
        print("    West:", FILE["NSEW"][3])
        print("    Grid Height:", FILE["HxW"][0], "("+str(100*int(FILE["HxW"][0]))+" meters)")
        print("    Grid Width:",FILE["HxW"][1], "("+str(100*int(FILE["HxW"][1]))+" meters)") 
        print("    Grid Size:", int(FILE["HxW"][0])*int(FILE["HxW"][1]), "("+str(100*int(FILE["HxW"][0])*int(FILE["HxW"][1]))+" square meters)")
        print("")
        
        
        
  elif cmd[0] == "info" and numArgs == 2:
    if saved(cmd[1]):
      FILE = loadFromFile(cmd[1])
      print("  "+FILE["areaName"])
      print("    North:", FILE["NSEW"][0])
      print("    South:", FILE["NSEW"][1])
      print("    East:", FILE["NSEW"][2])
      print("    West:", FILE["NSEW"][3])
      print("    Grid Height:", FILE["HxW"][0], "("+str(100*int(FILE["HxW"][0]))+" meters)")
      print("    Grid Width:",FILE["HxW"][1], "("+str(100*int(FILE["HxW"][1]))+" meters)") 
      print("    Grid Size:", int(FILE["HxW"][0])*int(FILE["HxW"][1]), "("+str(100*int(FILE["HxW"][0])*int(FILE["HxW"][1]))+" square meters)")
    else:
      print("  Could not find a file named "+cmd[1]+".grid, please check for spelling errors or ")
      print("  first create a new file for "+cmd[1]+" using makegrid.")
      
      
      
  elif cmd[0] == "delete" and numArgs == 2:
    if saved(cmd[1]):
      print("  Are you sure you want to delete "+cmd[1]+".grid?")
      next = input("    (y)es or (n)o: ")
      if next.lower() == "y" or next.lower() == "yes":
        os.remove("data/"+cmd[1]+".grid")
        print("  SUCCESS: "+cmd[1]+".grid was deleted.")
      else:
        print("  No action was performed.")
    else:
      print("  There is not a file named "+cmd[1]+".grid")
      print("  No action was performed.")
      
      
      
  elif cmd[0] == "clear" and numArgs == 1:
    if len(os.listdir("data")) == 0:
      print("  FAILURE: there are no .grid files to delete.")
      print("  No action was performed.")
    else:
      print("  Are you sure you want to delete all .grid files?")
      next = input("    (y)es or (n)o: ")
      if next.lower() == "y" or next.lower() == "yes":
        path = "data"
        for files in os.walk(path, topdown = True):
          for e in files[2]:
            os.remove(path+"/"+str(e))
            print("  SUCCESS: "+str(e)+" was deleted.")
        print("")
        print("  SUCCESS: all .grid files in ./data deleted.")
      else:
        print("  No action was performed.")
  
  
  
  elif cmd[0] == "quit" and numArgs == 1:
    print("  Are you sure you want to quit the program? (All existing .grid files will be saved.)")
    next = input("    (y)es or (n)o?   ")
    if next.lower() == "y" or next.lower() == "yes":
      print("  Exiting the program.\n")
      break
    else:
      print("  No action was performed.")
    
    
  else:
    print("  Unrecognized input or not the correct number of arguments, please try again using one of the supported commands.")
