---
title: 'Python sample script to access to rdb.svc'
order: 7
prerequires: []
---
This sample script contains following operations:
- Retrieve Authentication Token
- Retrieve the Reprocessing Data Baseline either for:
	- a L0 filename
	- a time interval (start/stop)
- Print the retrieved Baseline for each related L0 file
<p>Download file <a href="{{site.baseurl}}/data/ReprocessingDataBaseline.py" target="_blank">ReprocessingDataBaseline.py</a></p>

Example of Usage: 
	`python ReprocessingDataBaseline.py -u $ADG_USER -pw $ADG_PASSW -m S3OLCI -t0 2024-03-03T00:00:00Z -t1 2024-03-01T15:00:00Z -su A -pt L2LFR`
