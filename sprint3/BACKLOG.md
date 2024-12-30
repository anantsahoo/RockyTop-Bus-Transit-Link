BE = Back End
FE = Front End

Current bugs:
- The Login button on the home page's hover functionality prematurely hides the input fields. (FE)
- When using the names of bus stops as the start/end location, an error occurs when finding route. (BE)
- On the home page, sometimes you'll need to click "Favorites" or "History" twice to make them show up. (BE)
- When adding a location to the favorites tab, if there are commas in the location name, it will split and make multiple locations split at the comma. (BE)

Things that could be changed:
- Add a different color pin or icon on the map to indicate current location. (FE)
- Add a way to get back to the home page from other pages. (FE)
- Add "Register Account" and possibly "Settings" to the homepage's navbar. (FE)
- Update settings page (Remove "Add Favorite Location" and "Your Favorite Locations"). (FE)
- Make sure all pages have the same nav bar (Right now the home page's is different). (FE)
- Add a key/legend to clarify what pins represent. (FE)
- Add footers to pages that could use them. (FE)
- Add toggle switches for pins to control whether they are displayed or not. (BE)
- More detailed route calculation (need to show route on map: one from the user to the first bus stop, another one from first bus stop to final bus stop, and one from final bus stop to destination) (Also needs to account times, so use the current time to figure out when bus will be at the first bus stop) (Can use my work in v3 as a start). (BE)
- When a user finds a route, we need to save the route details so that we can display it in the history tab. (BE)
- Add existing favorite locations so that they show up in the favorites tab on the home page. (BE)
- Update the "Add" button in the favorites list on the home page so that it adds to the user's database. (Need to account for if the user is not logged in and they add a location on the home page, it needs to be accessible from the map page's "favorite locations" tab).
- Update the home page to display relevant information. (Possibly remove Routes and Schedules tab in nav bar. Possibly replace "Plan Your Journey" with a default map). (BE)
- Update Stop Details page to show more relevant information. (BE)
- Update settings page (Allow user to change password). (BE)




