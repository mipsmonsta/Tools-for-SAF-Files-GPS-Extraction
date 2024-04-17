import os
from pathlib import Path
from typing import Generator
import argparse
from dlbusstop import BusStops

# get files
def getFileName(directory: str) -> list[str]:
    return [file for file in os.listdir(directory) if Path(file).suffix=='.saf']

def main(dirFullPath: str):
    # pathdir = os.path.dirname(os.path.realpath(__file__))
    pathdir = os.path.abspath(dirFullPath)
    files = getFileName(pathdir)

    outPath = os.path.join(pathdir, "out.txt")
    for file in files:
        inPath = os.path.join(pathdir, file)
        getEvents(inPath, outPath)

    outGPSPath = os.path.join(pathdir, "outGPS.txt")
    inPath = outPath 
    convertEventsIntoGPS(inPath, outGPSPath)



def getEvents(file: str, outputfile: str):
    with open(file, 'r') as src: 
        with open(outputfile, 'w') as dest:
            start_comb = False
            for line in src:
                if line.startswith("$DATA"):
                    start_comb = True
                
                if start_comb:
                    if line.startswith("031") or line.startswith("041"):
                        dest.write(line)

# generator function for Vehicle Events
def _readEventsFromFile(file: str)->Generator["VehEvent", None, None]:
    with open(file, 'r') as src:
        for line in src:
            yield VehEvent(line)

def convertEventsIntoGPS(file: str, outfile: str):
    eventsGenerator = _readEventsFromFile(file)
    stack = []

    # Get bus stops from datamall. Workflow for download is done through 
    # running > python dlbusstop.py --forced
    busStops = BusStops()

    with open(outfile, "w") as dest:
        for event in eventsGenerator:

            if not stack:
                if event.id == "031" and event.subtype == "01": # stopzone subtype 1 (entry)
                    stack.append(event)
            elif len(stack) == 1:
                if event.id == "041" and event.subtype == "01": # door subtype 1 (release)
                    stack.append(event)
                else:
                    stack.clear()
            elif len(stack) == 2:
                if event.id == "041" and event.subtype == "02": # door subtype 2 (lock)
                    stack.append(event)
                else:
                    stack.clear()
            elif len(stack) == 3:
                if event.id == "031" and event.subtype == "02": # stopzone subtype 2 (exit)
                    stack.append(event)

                    # entry stopzone
                    entryDoorEvent = stack[1]
                    processedCoordX = int(entryDoorEvent.coordX) / 3600000
                    processedCoordY = int(entryDoorEvent.coordY) / 3600000
                    zoneEntryEvent = stack[0]
                    busStopDict = busStops.closestBusStopInfo((processedCoordY, processedCoordX))
                    dest.write(f"{processedCoordY}, {processedCoordX}, {zoneEntryEvent.busCode}, {busStopDict['BusStopCode'].strip()}, {busStopDict['Description']} \n")
                    stack.clear() # we are done and successful able to get GPS from
                                  # the set of 4 events. So clear stack to ready for
                                  # next set of 4 events
class VehEvent:
    def __init__(self, line: str):
        parts = line.split("\t")
        self.id = parts[0]
        self.subtype = parts[15]
        self.coordX = parts[9] # longtitude
        self.coordY = parts[10] # latitude
        self.busCode = parts[19] # only works for stop-zone event and it's 4 digits

    def __repr__(self):
        return f"{self.id}-{self.subtype}-{self.coordX}-{self.coordY}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Program to extract GPS coordinates from valid StopZone-Door-Door-StopZone events")
    parser.add_argument("saf_dir")
    args = parser.parse_args()
    main(args.saf_dir)