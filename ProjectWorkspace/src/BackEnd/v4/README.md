# Rocky Top Transit Link Version 4.0

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
   cd path_to/v4

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


## Additional Notes
This version does the following:
- Incorperates Will's finding route logic.
- Uses Anant and Deep's home page

Credits: GTFS data downloaded from https://www.knoxvilletn.gov/cms/One.aspx?portalId=109562&pageId=11688599