# Fire-Dashboard

https://user-images.githubusercontent.com/93783235/153659788-30fcdc68-a3ae-41fb-aa76-3897e6b6efdd.mp4


## Final Deliverable

This code was written for the Utah Division of Oil, Gas, and Mining to increase awareness of fire hazards near mining and drilling sites during the busy fire season of 2021. It is still in use today. 

This code creates feature layers that are used into an Esri. This dashboard can be used by division staff and management to make data-driven decisions. This allows a quick way for management to get information related to division assets. This information can be provided to other agencies such as BLM, USFS, mine operators, etc. Both the dashboard and web application employ the use of pop-ups to provide quick information about the division assets. The pop-ups, lists, and indicators in the dashboard are customized using Esri's Arcade programming language.

## About the Code

This code:
* Pulls in federal fire perimeter information from AGOL
* Filters for the state of Utah
* Creates .1 mile, 1 mile, and 5 mile buffers around perimeters
* Pulls in Utah's Division of Oil, Gas, and Mining asset locations from AGOL
* Spatially joins asset layers to fire perimeter layer
* Updates existing feature layers with updated joins on AGOL
* Creates CSVs for endangered assets within .1 mile and within fire perimeters (included fire incident name)
* Emails interested parties with CSVs attached

Estimated completion time: ~ 1 minute

## Usage recommendations
Create an executable from the python script then use Windows Task Scheduler to set the code to run as often as you choose. [Here](https://datatofish.com/python-script-windows-scheduler/) is a great walkthrough of this process. Make a determination based on how often the fire perimeter layer is updated. In Utah, they are updated often so I set the code to run every day. Windows Task Scheduler is not always reliable so it may be worth looking into other scheduling software or scheduling libraries. I have not strayed beyond Windows Task Scheduler. 

### Room for Improvement
* Use webhooks to run code automatically whenever there is change in fire perimeter size or status
* The append tool can be kind of slow. It might be worth using a different method to update the data, though I don't know of another way
* Filter assets sent to management by priority, asset types, etc. 
