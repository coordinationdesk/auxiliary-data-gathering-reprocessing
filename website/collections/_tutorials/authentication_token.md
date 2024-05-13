---
title: 'How to get authentication token to use with API'
order: 1
prerequires: [ ["Having an account","https://auxiliary.copernicus.eu/rdb.svc"], ["Having POSTMAN installed","https://learning.postman.com/docs/getting-started/installation-and-updates/"], ["Knowing POSTMAN","https://learning.postman.com/docs/getting-started/introduction/"] ]
---
#### Access Token

To get the AUXIP API token for a client, an HTTP POST request should be sent to the following Token resource: [https://auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token](https://auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token)

In the post body, username and password are specified in JSON format, and the response body contains a token key with an actual API Token as the value. The token should be used in an HTTP Authorization header while communicating with the AUXIP service.

It is necessary to get a token using a tool (a browser or any other application that can send http requests). Depending on the client that is used, there are different ways to send HTTP headers.

#### Steps
In this tutorial, we will use POSTMAN :

![Getting New Access Token via Postman](1_accesstoken.png){:style="border:1px black solid"}

To be able to send requests via Postman, one should configure the authorization settings first, as showing in the above steps:

- choose authorization via OAuth 2.0
- Set values :
    - Access Token URL : set the the resource where to post for the accessToken,
    - Client ID : should be set to “reprocessing-preparation”
    - Username and Password : Client credentials from the registration.
    - Scope : openid
- Get New Access Token

See [Reprocessing Data Baseline API User Manual]({{ site.baseurl }}/data/docs/RPP-API-0013-CS_Reprocessing_Data_Baseline_API_User_Manual/RPP-API-0013-CS_Reprocessing_Data_Baseline_API_User_Manual.html){:target="_blank"} for more information