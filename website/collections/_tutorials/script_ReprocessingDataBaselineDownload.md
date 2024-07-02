---
title: 'Python sample script for reprocessing baseline auxiliary files download'
order: 9
prerequires: []
---
This sample script contains following operations:
- Retrieve Authentication Token
- Retrieve the Reprocessing Data Baseline either for:
	- a L0 filename
	- a time interval (start/stop)
- Print the retrieved Baseline for each related L0 file
- if requested (-d True specified on the command line), download the files for the baseline in the a folder named based on the execution parameters.
<p>Download file <a href="https://{{site.baseurl}}/data/ReprocessingDataBaselineDownload.py" target="_blank">ReprocessingDataBaselineDownload.py</a></p>

Example of Usage: 
	`python ReprocessingDataBaselineDownload.py -u $ADG_USER -pw $ADG_PASSW -m S3OLCI -t0 2024-03-03T00:00:00Z -t1 2024-03-01T15:00:00Z -su A -pt L2LFR -d TRUE `
