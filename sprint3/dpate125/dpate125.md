# Sprint 3

Name: Deep Patel

GitHubID: Deep0320

Group Name: Rocky Top Transit Link

### What I planned to do
* Issue #41: Mark the user's location on the map [Link to Issue 41](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/41)
* Issue #42: Add a legend for the map [Link to Issue 42](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/42)
* Issue #43: Add favorite location pins to the map [Link to Issue 43](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/43)
* Issue #57: Add a map on the welcome page [Link to Issue 57](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/57)
* Issue #58: Add autocomplete to the favorites list [Link to Issue 58](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/58)
* Issue #59: Fix the home page banners [Link to Issue 59](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/59)

### What I did not do
* Everything I was assigned for sprint 3 was completed.

### What problems I encountered
* First time working with the map: It was my first time working with the leaflet map interface, and it took me a while to get used to how they do things, but eventually I got the hang of it and was able to finish my issues.

### Issues I worked on
* [#41](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/41) Mark Current Location
* [#42](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/42) Add Key/Legend
* [#43](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/43) Favorite Location Pins
* [#57](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/57) Add blank map on welcome page
* [#58](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/58) Add auto complete for the favorites list
* [#59](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/59) Fix home page banner

### Files I worked on
* `ProjectWorkspace/src/BackEnd/v4/app/templates/base.html`
* `ProjectWorkspace/src/BackEnd/v4/app/templates/home.html`
* `ProjectWorkspace/src/BackEnd/v4/app/routes.py`
* `ProjectWorkspace/src/BackEnd/v4/app/static/CSS/sprint2.css`
* `ProjectWorkspace/src/BackEnd/v4/app/static/js/sprint2.js`
* `ProjectWorkspace/src/BackEnd/v4/app/templates/map.html`

### What I accomplished

* **Added current location and favorites markers to the map**: I added logic to add the favorites place and current location pins on the map with their own colors.
* **Added a legend to the map**: I added a legend to the map which showed what the different color of pins represent, one for each of favorites places, current location, and the bus stops.
* **Added auto complete to the favorites list**: I added the autocomplete feature so that we could connect the locations that the users add to the data that we have set up in the backend, allowing us to plot them on the map.
* **Fixed banners in the home page and added a map**: I fixed the banner that wasn't showing up in the home page that welcomed the user. I also added a banner for the footer. I also added a map for users to get a feel of how the website will work once they decide to use it.