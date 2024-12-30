import googlemaps
from datetime import datetime

def main():
    gmaps = googlemaps.Client(key='AIzaSyB9xZcHzm8QOnopWvcPuPbdcv5c1yxFcSM')

    #example use:
    # This code simply converts address to a geocode.
    # White House
    start = '1600 Pennsylvania Avenue, Washington, DC'
    end = '52 Railroad St., Gorham, NH'
    startGeo = gmaps.geocode(start)
    endGeo = gmaps.geocode(end)
    # geocode returns [] if the address is invalid
    # this will be how we check if the addresses are valid.
    if startGeo == []:
        print("Invalid Start Address")
        return 1
    if endGeo == []:
        print("Invalid Start Address")
        return 1
    
    # UK Prime Minister's House
    #end = '10 Downing St., London, UK'

    # do a calculation between these two addresses:
    # now allows inclusion of current conditions, 
    # otherwise it does average conditions
    now = datetime.now()

    # if mode is not specified, default is car (mode="transit" or mode="")
    directions = gmaps.directions(start, end, departure_time=now)
    if directions == []:
        print(f"No route exists between {start} and {end}")
        return
    # directions needs to be parsed more, since it gives out lots of garbage.
    # mixed with useful info.
    # luckily, we can do stuff like this to print useful directions.
    # I believe the intent is that this is results that can be given to html stuff
    #print(directions[0]['bounds']['legs'])
    # Assuming directions_result has already been fetched
    route = directions[0]

    # Parse bounds
    bounds = route['bounds']
    northeast = bounds['northeast']
    southwest = bounds['southwest']
    print(f"Bounds: Northeast: {northeast}, Southwest: {southwest}")

    # Parse leg details
    leg = route['legs'][0]
    start_address = leg['start_address']
    end_address = leg['end_address']
    distance = leg['distance']['text']
    duration = leg['duration']['text']
    print(f"Start Address: {start_address}")
    print(f"End Address: {end_address}")
    print(f"Distance: {distance}")
    print(f"Duration: {duration}")

    # Parse steps
    for step in leg['steps']:
        instruction = step['html_instructions']
        distance = step['distance']['text']
        duration = step['duration']['text']
        start_location = step['start_location']
        end_location = step['end_location']
        #polyline = step['polyline']['points']
        
        print(f"Step: {instruction}")
        print(f"Distance: {distance}, Duration: {duration}")
        print(f"Start Location: {start_location}, End Location: {end_location}")
        #print(f"Polyline Points: {polyline}")


if __name__ == "__main__":
    main()

