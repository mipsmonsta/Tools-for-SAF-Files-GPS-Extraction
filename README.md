## Scripts to work with SAF for Extraction of GPS coordinates

### Introduction
For every bus fitted with the IDR device by Trapze Group, SAF files are generated for the bus 
that will log the events. To retrace the locations visited by the bus, the door 
and stopzone events would need to be processed. The SAF file would consists of many
different events, but of interests are the StopZone events and door events.

### When the bus enters the bus bay

A total of 4 events will be generated:
1. Stopzone Entry Event 
2. Door Released Event
3. Door Locked Event
4. Stopzone Exit Event.

These 4 events are interspersed among other events, but will always for one bus stop, be in
sequence as these are logged over time. Only when the 4 events are collected as a set, then the 
bus locations in lat/long can be extracted from the Door Released Event.

### Scripts and project structure

There are two scripts - `extractor.py` and `dlbusstop.py`.

These should be downloaded into a folder project. The folder will have the following structure.

```
project folder_ _ .
              |__ extractor.py 
              |__ dlbusstop.py
              |__ README.md <this file that you are reading>
              |__ .gitignore <for git tool purpose>
        
```

### First Script `dlbusstop.py` - to download the bus stops dynamic data from LTA Datamall

As the bus stop code in stopzone events from the SAF file are recorded in 4 digits bus stop code,
lat/long recorded are matched with the 5000 plus bus stops residing in [LTA Data Mall] to recover
the 5 digits bus stop code. This matching (for the geek in you) is done using the `KDTree` data structure of the [scipy] library.

The `dlbusstop.py` is responsible to save the 5000 bus stops into a `busstop.json` file into the 
project folder. You run the code like this:

```
python dlbusstop.py
```

If you need to update the json file as bus stops may be added to the datamall over time, you can re-run
with the `--forced` flag.

```
python dlbusstop.py --forced
```

Also, ensure your LTA Datamall [apikey] is either stored in a `apikey.txt` file in the project 
directory or in the global variable `APIKEY= <key here>` part of the python script. This will grant you access to the API. Note also that the scripts now allow downloading of not more than 6000 bus stops. If 
one day, Singapore has more than 6000 bus stops, edit the script section as shown below:

```python
with open("busstop.json", "w") as outFile:
        
        array = []
        # download bus stops in batch of 500
        # put them into an array
        
        for i in range(0, 6001, 500): # <----edit 6001 to say 6501 or 7001 bus stops
            params = {"$skip": i}
            response = requests.get(url, headers=headers, params=params)
```

### Second Script `extractor.py`

Running the first scripts and successful downloading of `busstop.json` allows you to import *dlbusstop* as a library. The class `BusStops` will not now be ready to use by the `extractor.py` script. A KDTree structure will be initated when the BusStops class is instantiated.

To run the script do this:

```
python extractor.py "<folder path string with SAF File>"

e.g. 

python extractor.y "C:\...\SAF files for sv26 D1 on 17Jan24"
```

If successful with no errors, two files will be outputted.

The first file in the *SAF file folder* (not the project folder!), will be `out.txt`. It contains 
only the Stopzone and door events that are extracted, and their order are stable.

The other `outGPS.txt` file is where the GPS coordinates for the bus stops are extracted for the bus.
The format per line is

```
lat, long, Bus Stop Code (4 digits from SAF), Bus Stop Code from Datamall, Bus Stop Description from Datamall
```
in CSV format.


*Happy Coding,
17 Apr 2024*

[LTA Data Mall]: https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html
[scipy]: https://docs.scipy.org/doc/scipy/reference/spatial.html
[apikey]: https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html

