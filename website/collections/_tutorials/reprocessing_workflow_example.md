---
title: 'Example of workflow for product reprocessing'
order: 5
prerequires: [ ["Having an account","{{site.url}}/rdb.svc"], ["Having a authentification token","tutorials.html#1"],["Having POSTMAN installed","https://learning.postman.com/docs/getting-started/installation-and-updates/"], ["Knowing POSTMAN","https://learning.postman.com/docs/getting-started/introduction/"] ]
image_1: "1_accesstoken.png"
image_b: 2_bearer.png
image_5_f: 3_function.png
image_5_r: 5_DataBaseline_response.jpg
image_5_d: 5_AuxFileDownloadRequest.jpg
---
#### Introduction

This is an example for a workflow to retrieve the auxiliary files for a reprocessing activity is outlined hereafter. <br>
The workflow is described with the accesses to the Service APIs executed from a Rest API Test application like Postman, using the services showed in the previous tutorials.
A code example is given at the end, with a Python script.

#### Endpoints

The endpoint urls for the accessed services are:
 - [{{site.url}}/auxip.svc]({{site.baseurl}}/auxip.svc)
 - [{{site.url}}/rdb.svc]({{site.baseurl}}/rdb.svc)

#### Workflow Description
The activity is composed of two main steps:
1. The list of aux files to be used is retrieved using the function **getReprocessingDataBaseline** of the rdb.svc service
2. The distinct aux files are downloaded from auxip.svc service using the links contained in the response from getReprocessingDataBaseline (that specify the internal ID of the Aux FIles)

The getReprocessingDataBaseline function could be invoked both by passing a list of L0 products to be processed, or by passing a start/stop time interval:
- **getReprocessingDataBaseline**(l0_names, mission, unit, product_type)
    Query only one level 0 product name. 	
    Sample : `{{site.url}}/rdb.svc/getReprocessingDataBaseline(l0_names='S3A_OL_0_EFR____20240301T010412_20240301T010610_20240301T025430_0118_109_302______PS1_O_NR_002.SEN3.zip',mission='S3OLCI',unit='A',product_type='L2LFR')`
	
- **getReprocessingDataBaseline**(start_time, stop_time, mission, unit, product_type)
    Query level 0 products included in the specified time interval
	
    Sample : `{{site.url}}/rdb.svc/getReprocessingDataBaseline(start=2024-02-29T23:59:59Z,stop=2024-03-02T00:00:00Z,mission='S3OLCI',unit='A',product_type='L2LFR')

#### Workflow Steps using Postman
First, into the authentication tab, select a Bearer Token and fill it with your token :
![Bearer Configuration]({{"/assets/images/tutorials" | relative_url }}/{{page.image_b}}){:style="border:1px black solid"}

Then, add the function in the GET field :

![Function Call]({{"/assets/images/tutorials" | relative_url }}/{{page.image_5_f}}){:style="border:1px black solid"}

You can now send the query.
The result is shown in the dedicated window.

The Result will be a Json, listing, for each L0 file in the specified Time interval, a list of the applicable Aux Files, together with the link for retrieval.
![Function Call Result]({{"/assets/images/tutorials" | relative_url }}/{{page.image_5_r}}){:style="border:1px black solid"}
Save it to a file.

Select from the response the link for one of the Aux Files in the result.<br>
A new tab, for a new GET request will be opened.<br>
Configure again in the authentication tab the OAuth2 authentication method, and select the already retrieved bearer Token

Add the link in the GET field:

![Download Request]({{"/assets/images/tutorials" | relative_url }}/{{page.image_5_d}}){:style="border:1px black solid"}

Send the query, selecting "Send and Download".
Upon receiving the answer from the remote service, you are requested to specify the destination of the file being downloaded.




