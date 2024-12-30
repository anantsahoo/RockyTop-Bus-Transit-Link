# Sprint2

**Name**: William Douglass

**GitHub ID**: wdouglass078

**Group Name**: Rocky Top Transit Link

## What I Planned to Do

- Create /find_route endpoint (Issue #34) [https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/34]
- Calculate Route from User to Bus Stop (Issue #33) [https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/33]
- Calculate Route from Bus Stop to Final Destination (Issue #32) [https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/33]

## What I Did Not Do

- All of my tasks were complete, but I think I could have added a few extra features, especially for the route calculation. For example, I would have like to have added options for typing in stop_ids for the bus stops or an autocorrect feature (not an autofill) that would correct misspellings of bus stops to the closest name (perhaps a levenshtein distance could be useful here).
- Also, we wanted to have this all integrated together into one cohesive piece, but the departure of one of our teammates, who was responsible for integrating the frontend and the backend, made this unfeasible at the current time.

## What Problems I Encountered

- Most of the problems I encountered came from displaying the information I found to a website. This necessitated some changes to the formatting of the information before sending it off as a JSON object, and some changes to the map.html file.

## Issues I Worked On

- (Issue #32: Calculate Route From Bus Stop to Final Destination) [https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/32]
- (Issue #33: Calculate Route From User to Bus Stop) [https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/33]
- (Issue #34: Create /find_route endpoint) [https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/34]

## Files I Worked On

* `RockyTop-Transit-Link/ProjectWorkspace/src/Backend/app/routes.py`
* `RockyTop-Transit-Link/ProjectWorkspace/src/Backend/app/templates/map.html`
* `RockyTop-Transit-Link/ProjectWorkspace/src/Backend/gtfs/stops.txt`
* `RockyTop-Transit-Link/sprint2/wdougla4/wdougla4.commits.txt`
* `RockyTop-Transit-Link/sprint2/wdougla4/wdougla4.md`

## What I Accomplished

- For issue 32, I used the Haversine formula to calculate the distance between a given address and a KAT bus stop, saving the closest one to the user's final destination. This calculation was only done if the user's final destination was not a bus stop.
- For issue 33, I used the Haversine formula to calculate the distance between a given address and a KAT bus stop, saving the closest one to the user's final destination. This calculation was only done if the user's final destination was not a bus stop.
- For issue 34, I took the above issues and merged them together to find the route between two addresses using the KAT system as much as possible. If the addresses were valid KAT stops, then the Google Maps API would simply take the stops's associated geocodes and find a route, otherwise, it would find the closest distance KAT stop to either or both of the initial and end locations and calculate from there.