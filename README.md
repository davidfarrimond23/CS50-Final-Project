# Placename Mapper!
#### Video Demo: https://youtu.be/Pf83apwbxrA
#### Description:

#### Overview:

This project had it's genesis way back when I was doing my Master's Degree in Digital Heritage.
I had invested an awful lot of time into ArcGIS and believed it might be a useful tool not just for heritage practitioners & archaeologists, but historians, too.
I began manually extracting places from a historical text, adding them into an SQL database, and building a map with them.
This was slow.

This was put on a backburner until I began learning Python for the CS50 introduction to Computer Science.

My project idea began, essentially, as an attempt to automate some of this process.

#### Python Scripting:

The first building block, so to speak, was the Python script that searches through the text file to find placenames.

The first step for this is the SQL database that the script will compare against.

This was acquired, firstly, from the [Ordnance Survey Open Placenames](https://www.ordnancesurvey.co.uk/business-government/products/open-map-names):
Served under the UK's Open Government License.

Initial testing revealed a need to clean this data substantially- remove duplicates, trim the data, etc- you can see this [here](placenames.db).

The testing process ended with two scripts written:
A far slower script that took 2 minutes to run through an average text, but produced less "False Positives", and a far faster script employing python's regex library that can produce false positives, but processes the same text in seconds.

Both approached the problem in a completely different direction- the first checking each line of text, the second checking each place name against the whole text. The second scales better, and has a consistent time complexity with the database being a consistent size.

This script is the function 'searchFunc' in [helpers.py](helpers.py).

With a python script accepting a file and returning a dictionary of placenames and times found, the next step was to examine how to map the results!

#### Mapping place names:

My first thought was to utilise google's Mapping API. While it is quick, and takes multiple points as a JSON object, it had two drawbacks:

    1. The basemap is not customisable.
    2. It costs money to query with a lot of data.

With my experience in GIS and a current working knowledge of QGIS, I decided to explore the possibilities of this software.

This is where [Tom Chadwin's](https://github.com/tomchadwin/qgis2web) QGIS2WEB plugin comes in. QGIS2WEB takes a map made in QGIS and converts it to a webmap.

This webmap can be embedded in a website like any other resource. I noted that the layers of the map were rendered utilising a GeoJSON; point data used a GeoJSON "point collection" object.

With this in mind, [helpers.py](helpers.py) contains two functions to build the layer file that will render our placenames:

```
stringBuilder()
```
Which accepts a placename and the amount of times found, queries our database, and returns a GeoJSON point feature to:

```
insertData()
```

Which accepts a dictionary and a filepath. It opensthe filepath provided, clears it, writes the GeoJSON feature collection opening lines, and passes each key-value pair from the dictionary into stringBuilder as arguments.

When done, it caps the GeoJSON feature collection, and closes the file.

With this done we then have a placenames layer saved that can be accessed by our map!

#### Tying it all together with Flask:

I have chosen Flask as my framework because, put simply, it's what I'm familiar with. It also has a really simple, self explanatory, way of setting up Uploads and Sessions, both utilised for this app.

[application.py](application.py) is, of course, the main app file for this app.

It sets up the upload functionality (taken from Flask's [documentation](https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/) and ensuresonly TXT files are uploaded.

It then configures the Flask Sessions, and our first function ensures the uploaded filename matches the allowed file extensions.

We then define a function that produces a random, 10 digit integer, to act as the user's session id.

When the app is started, before a request is made, it clears the file storage for session uploads and processing.

Our index route checks for a session ID or no. If there is no session ID, it creates one using the function mentioned above. Both routes (no id or existing id) render [index.html](templates/index.html) with a placeholder placenames file.

Index.html extends our layout header and footer with the map in one bootstrap column and "How to use" the webapp, with attributions, in another. It is responsive to screensize.

Following the route through, [upload.html](templates/upload.html) renders a simple upload page, with a button, that allows a user to upload a file and checks that file against our requirements.

When successful this renders [data.html](templates/data.html).

data.html allows a user to select a file, and submit it for processing. It accesses the uploaded file, calls insertData(), and dumps the resulting dict into a temporary file for the session ID.

A little javascript/css animation runs onclick of the "Process" button while this happens. Once done, we render [dataprocessed.html](templates/dataprocessed.html), which contains a list of our Key-Value pairs from our dictionary.

#### Finally:

The /mapit route sends the mapped filename and our dictionary file through as a POST request.

It creates a temporary JS file for the session id, runs our insertData function, and opens the processed file. The results of these processes are passed into [map.html](templates/map.html), which loads the newly created JS file, and the processed file.

We then have our map, and the file to compare it against!

#### Take-aways and improvements:

Firstly, I have a couple of features in the works for this somewhere down the line. The ability to select a point and "Find" it in the text on my "map.html" page is the first.

Related to this, I would like users to be able to tag places as "False positive" and act on this. You will note that in the db file there are already steps towards this (splitting duplicates into their own table).

Time complexity is important! The initial script for place-name search ran very long and while useful for my own purposes, the trade-off between accuracy and speed for this web app was an important one to make.

CSS styling can be found in [static/styles.css](static/styles.css)- this is limited, with a simple animation and bootstrap-based formatting.

