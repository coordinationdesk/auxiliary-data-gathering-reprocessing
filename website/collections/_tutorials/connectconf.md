---
title: 'How to connect to reprocessing configuration baseline'
order: 2
prerequires: [ ["Having an account","{{site.url}}/rdb.svc"], ["Having a authentification token","tutorials.html#1"], ["Having POSTMAN installed","https://learning.postman.com/docs/getting-started/installation-and-updates/"], ["Knowing POSTMAN","https://learning.postman.com/docs/getting-started/introduction/"] ]
image_b: 2_bearer.png
image: 2_function.png
---
#### Endpoint
The endpoint url for this service is [{{site.url}}/processing.svc]({{site.url}}/processing.svc)

#### Function
We will use in this sample the function GetReproBaselineListForSensing :

- **GetReproBaselineListForPeriod**(Mission, Unit, SensingTime, ProductType)

    Query the list of aux file for these particular parameters.

    Samples : 
	- `{{site.url}}/reprocessing.svc/GetReproBaselineListForPeriod(Mission='S2MSI',Unit='A',SensingTime='2018-05-02T12:00:30Z',ProductType='L1B')`
	- `{{site.url}}/reprocessing.svc/GetReproBaselineListForPeriod(Mission='S3OLCI',Unit='B',SensingTime='2024-03-01T12:00:30Z',ProductType='L2LFR')`

#### Steps
First, into the authentication tab, select a Bearer Token and fill it with your token :
![Bearer Token Configuration]({{"/assets/images/tutorials" | relative_url}}/{{page.image_b}}){:style="border:1px black solid"}


Then, add the function in the GET field :

![Processing Request]({{"/assets/images/tutorials" | relative_url}}/{{page.image}}){:style="border:1px black solid"}

You can now send the query.


