TOKEN=$1
mkdir reportsS2

TOKEN=$(python3 auxip_token.py  -u $AUXIP_USER -pw $AUXIP_PASS -m prod -o completiontk.json)

echo "TOKEN:$TOKEN"


#S2
python3 verify_completion.py -o reportsS2/reportS2_UT1UTC.txt -s 168 -t 'AUX_UT1UTC' -m 'S2' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS2/reportS2_ECMWFD.txt -s 12 -t 'AUX_ECMWFD' -m 'S2' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS2/reportS2_CAMSAN.txt -s 24 -t 'AUX_CAMSAN' -m 'S2' -tk ${TOKEN}
python3 verify_completion.py -o reportsS2/reportS2_CAMSRE.txt -s 24 -t 'AUX_CAMSRE' -m 'S2' -tk ${TOKEN} 

echo "Done!"
