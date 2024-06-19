#!/bin/bash

mkdir reportsS1

# Extract from json
# Read Token
TOKEN=$(python3 auxip_token.py  -u $AUXIP_USER -pw $AUXIP_PASS -m prod -o completiontk.json)

echo "TOKEN:$TOKEN"


# Perform completion for each S1 aux type
#S1
: <<'JUMP1'
python3 verify_completion.py -o reportsS1/reportS1_WND.txt -s 3 -t 'AUX_WND' -m 'S1' -tk ${TOKEN} -ss '00-00-01-00' 
python3 verify_completion.py -o reportsS1/reportS1_WAV.txt -s 3 -t 'AUX_WAV' -m 'S1' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS1/reportS1_ICE.txt -s 24 -t 'AUX_ICE' -m 'S1' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS1/reportS1A_POEORB.txt -s 24 -t 'AUX_POEORB' -m 'S1A' -tk ${TOKEN} -ss '00-00-01-00' 
python3 verify_completion.py -o reportsS1/reportS1B_POEORB.txt -s 24 -t 'AUX_POEORB' -m 'S1B' -tk ${TOKEN} -ss '00-00-01-00' 
#pids+=" $!"
JUMP1

#wait
#wait $pids || { echo "There were errors" >&2 ; exit 1; }
echo "DONE!"
