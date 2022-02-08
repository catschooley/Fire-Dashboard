# Fire-Dashboard

https://user-images.githubusercontent.com/93783235/150437986-e7e71c20-a792-4c5d-a34a-a1f4aae2e031.mp4

## Final Deliverable

This code was written for the Utah Division of Oil, Gas, and Mining to increase awareness of fire hazards near mining and drilling sites during the busy fire season of 2021. It is still in use today. 

This code creates feature layers that are used in an Esri Dashboard and Esri Web Application. This dashboard can be used by division staff and management to make data-driven decisions. This allows a quick way for management to get information related to division assets. The Esri Web Application allows managers and staff to quickly download a csv file of all assets within a chosen distance of the fire perimeters. This information is provided to other agencies such as BLM, USFS, mine operators, etc. Both the dashboard and web application employ the use of pop-ups to provide quick information about the division assets

## About the Code

This code:
* Pulls in federal fire perimeter information from AGOL
* Filters for the state of Utah
* Creates .1 mile, 1 mile, and 5 mile buffers around perimeters
* Pulls in Utah's Division of Oil, Gas, and Mining asset locations from AGOL
* Spatially joins asset layers to fire perimeter layer
* Updates existing feature layers with updated joins on AGOL
* Creates CSVs for endangered assets within .1 mile and within fire perimeters
* Emails interested parties with CSVs attached

Estimated completion time: less than one minute

## Usage recommendations
Create an executable from the python script then use Windows Task Scheduler to set the code to run as often as you choose. [Here](https://datatofish.com/python-script-windows-scheduler/) is a great walkthrough of this process. Make a determination based on how often the fire perimeter layer is updated. In Utah, they are updated often so I set the code to run every day. Windows Task Scheduler is not always reliable so it may be worth looking into other scheduling software or scheduling libraries. I have not strayed beyond Windows Task Scheduler. 

### Room for Improvement
* Use webhooks to run code automatically whenever there is change in fire perimeter size or status
* The append tool can be kind of slow. It might be worth using a different method to update the data, though I don't know of another way
* Filter assets sent to management by priority, asset types, etc. 
