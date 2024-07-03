---
title: 'Python sample script to access to auxip.svc'
order: 6
prerequires: []
---
This sample script contains following operations:
- Retrieve Authentication Token
- Query the Auxip Catalogue for a filename
- If the product was found, download it
<p>Download file <a href="{{site.baseurl}}/data/getBaseline.py" target="_blank">getBaseline.py</a></p>
Example of Usage:

`python getBaseline.py -u $ADG_USER -pw $ADG_PASSW -m S3OLCI -t0 2024-03-03T00:00:00Z -t1 2024-03-01T15:00:00Z -su A -d`
