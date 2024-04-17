import requests
from scipy.spatial import KDTree
import pathlib
import argparse
import json
import logging

# Global constants
JSONFILE = "busstop.json"
APIKEY = None # Datamall key can be placed here or in the apikey.txt in same directory as __name__ file


class BusStops:
    def __init__(self):
        assert self._hasBusStops()
        self.busStops = None
        self.KDTree = None
        self.tupleCoordsDict = None # format {(lat, long), index}
        self._convertJSONIntoBusStops()

    def _hasBusStops(self)-> bool:
        return pathlib.Path(JSONFILE).is_file()
    
    def _convertJSONIntoBusStops(self):
        with open(JSONFILE, "r") as file:
            json_data = file.read()

            self.busStops = json.loads(json_data)
            
            self.tupleCoordArray = [(int(busStop['Latitude'] * 360000), int(busStop['Longitude'] * 360000)) \
                               for busStop in (self.busStops)]
            
            self.KDTree = KDTree(self.tupleCoordArray)

    def queryCoordinates(self, latLong: tuple[float, float]) -> list[tuple[int, int]]:
        return self.KDTree.query((int(latLong[0]*360000), int(latLong[1]*360000)))
    
    def closestBusStopInfo(self, latLong)->dict:
        results = self.queryCoordinates(latLong)
        if results:
            _, index = results
            return self.busStops[index]
            

def donwloadBusFileFromDataMAll(apiKey: str):

    headers = {"AccountKey": apiKey}
    url = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"

    
    with open("busstop.json", "w") as outFile:
        
        array = []
        # download bus stops in batch of 500
        # put them into an array
        
        for i in range(0, 6001, 500):
            params = {"$skip": i}
            response = requests.get(url, headers=headers, params=params)
            try:
                arrayData = json.loads(response.text)['value']
                array += arrayData

            except Exception as e:
                print(e)

        # store it as json array
        outFile.write(json.dumps(array))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Program to download Bus Stops from Datamall")
    parser.add_argument("--forced", action="store_true") # flag for forcing download of bus stop lists
    args = parser.parse_args()

    # Get APIKEY or if none, from ./apikey.txt
    if not APIKEY:
        if pathlib.Path('apikey.txt').is_file():
            with open("apikey.txt", "r") as keyFile:
                APIKEY = keyFile.read().strip()

    if args.forced or pathlib.Path(JSONFILE).is_file() == False:
        donwloadBusFileFromDataMAll(APIKEY)
    
    print("Test matching of bus stops using test coordinates")
    busStops = BusStops()
    coords = (1.333899, 103.76040)
    busStopDict = busStops.closestBusStopInfo(coords)
    print(busStopDict)

    coords = (1.356939, 103.828911)
    busStopDict = busStops.closestBusStopInfo(coords)
    print(busStopDict)

    coords = (1.359492, 103.837602)
    busStopDict = busStops.closestBusStopInfo(coords)
    print(busStopDict)

    coords = (1.407805, 103.898044)
    busStopDict = busStops.closestBusStopInfo(coords)
    print(busStopDict)