# Rocky Top Transit Link Version 2.0

## Overview

We're building a bus route planning web application using Flask. Users can view a map, plan trips, and save favorite locations.

## Setup and Installation

-  please carefully follow all the steps listed below in order.

### Prerequisites

- Python 3.12.6 (preferably have a virtual environment for each version of the app i.e. something like "v2_env")
- pip (Python package installer)

## How to Run the Project

1. **Clone the Repository**
   ```bash
   git clone https://github.com/utk-cs340-fall24/RockyTop-Transit-Link.git

2. ** Go to V2 Directory**
   ```bash
   cd path_to/v2

3. **Install Requirements**

   ```bash
   pip install -r requirements.txt

4. **Initialize Database**
   ```bash
   flask db init

5. **Migrate Database**
   ```bash
   flask db migrate

6. **Upgrade Database**
   ```bash
   flask db upgrade

7. **Run the Application**
   ```bash
   flask run

8. **Access the Application**

      Open your web browser and navigate to http://localhost:5000/
## Sprint 1 Goals

We aimed to:

- Set up the initial Flask app.
- Make the map page the homepage.
- Add login and registration features.
- Display a map with bus stops.
- Implement autocomplete for selecting stops.
- Allow users to save favorite locations.

## Completed Tasks

1. **Map Page as Homepage**
   - Set the map page as the default homepage.
   - Ensured the map displays using Leaflet.js and OpenStreetMap.

2. **User Authentication**
   - Added login and registration forms.
   - Integrated Flask-Login for user sessions.
   - Added login/register buttons when the user isn't logged in.

3. **Map Features**
   - Loaded GTFS `stops.txt` data.
   - Displayed bus stops on the map.
   - Implemented autocomplete for stop selection.

4. **Favorite Locations**
   - Created a settings page.
   - Allowed users to add and remove favorite locations.
   - Displayed favorite locations on the map page for quick selection.



## Possible Next Steps for Sprint 2

- Implement routing logic to find routes between stops.
- Display routes and directions on the map.
- Improve error handling.

## Additional Notes
Credits: GTFS data downloaded from https://www.knoxvilletn.gov/cms/One.aspx?portalId=109562&pageId=11688599