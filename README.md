# public_transit_deserts
### Before you read further, note that you will need your own Here account (and by extension your own app_id and app_code) in order to use this program. You can make a free account at https://developer.here.com/ and then create a file named here_credentials.txt in the credentials subdirectory with the format:

\
app_id\
app_code
---
This program uses the Here API, specifically the Public Transit entrypoint of the Places API found here: 
https://developer.here.com/documentation/places/topics_api/resource-browse-pt-stops.html
\
It allows the user to save their own grids made up of 100m by 100m blocks, each having a value which corresponds to 
the distance it lies from the nearest public transit stop. Additionally, you can use the program to search for the 
point(s) in the grid that is (are) furthest away from the nearest public transit stop, i.e. the public transit 
desert(s).
\
In most cities with good public transit access, the algorithm only needs to look at about 1/4 of the locations in order to find the point that is furthest away. It does this by:
- Check if the point is less than ((current max distance) - 100*sqrt(2)) meters away from the nearest PT stop:
  if so, then we can eliminate all its neighbors (the NW, N, NE, SW, S, SE, E, and W neighbors to it).
- Otherwise, check if the point is less than ((current max distance) - 100) meters away from the nearest PT stop:
  if so, then we can eliminate its cardinal neighbors (the N, S, E, and W neighbors to it).

\
This is because of the way that a grid of squares works (100m between points on the grid, 100*sqrt(2)m betwen points
diagonal to each other). We could add more criteria, but I haven't checked the runtime differences. This would
be something really interesting to look at and I'll try to determine the optimal number of checks.
\
To run on a Unix based system, download the project, navigate to its main directory, and run 
`python3 main.py`
This program was tested in Python 3.7 and will not work in Python 2.7 or earlier without some tweaking.
\

Here are selected examples from my to-do list for this project:
- Improve documentation and commenting.
- Investigate pros/cons of adding more distance checks at each point in the main PT Desert algorithm.
- Add more error checking; the user has a lot of freedom, possibly too much.
- Consolidate the getIsolatedHere and getIsolatedCache functions into one in funcs.py.
- Look into improving the precision of the borderLengths function in funcs.py.
- Add more features, such as letting the user define non-rectangular polygon borders (since most cities are not
  nice clean rectangles).
- More bug fixes.
