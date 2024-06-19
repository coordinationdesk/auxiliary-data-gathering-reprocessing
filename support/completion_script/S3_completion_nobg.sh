mkdir reportsS3

TOKEN=$(python3 auxip_token.py  -u $AUXIP_USER -pw $AUXIP_PASS -m prod -o completiontk.json)

echo "TOKEN:$TOKEN"

#S3
# TODO: create a associative array with type, followed by satellite/step, browse the array and build commands
python3 verify_completion.py -o reportsS3/reportS3A_AX___FRO_AX.txt -s 24 -t 'AX___FRO_AX' -m 'S3A' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3B_AX___FRO_AX.txt -s 24 -t 'AX___FRO_AX' -m 'S3B' -tk ${TOKEN}
python3 verify_completion.py -o reportsS3/reportS3__AX___MFA_AX.txt -s 6 -t 'AX___MFA_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__AX___MA1_AX.txt -s 6 -t 'AX___MA1_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__AX___MA2_AX.txt -s 6 -t 'AX___MA2_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__AX___BB2_AX.txt -s 720 -t 'AX___BB2_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3A_SR___POEPAX.txt -s 24 -t 'SR___POEPAX' -m 'S3A' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3B_SR___POEPAX.txt -s 24 -t 'SR___POEPAX' -m 'S3B' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3A_SR_1_USO_AX.txt -s 24 -t 'SR_1_USO_AX' -m 'S3A' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3B_SR_1_USO_AX.txt -s 24 -t 'SR_1_USO_AX' -m 'S3B' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__SR_2_RMO_AX.txt -s 6 -t 'SR_2_RMO_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__SR_2_POL_AX.txt -s 168 -t 'SR_2_POL_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3A_SR_2_RGI_AX.txt -s 24 -t 'SR_2_RGI_AX' -m 'S3A' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3B_SR_2_RGI_AX.txt -s 24 -t 'SR_2_RGI_AX' -m 'S3B' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__SR_2_SIC_AX.txt -s 72 -t 'SR_2_SIC_AX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3__SL_2_SSTAAX.txt -s 24 -t 'SL_2_SSTAAX' -m 'S3' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3A_SR_2_PCPPAX.txt -s 24 -t 'SR_2_PCPPAX' -m 'S3A' -tk ${TOKEN} 
python3 verify_completion.py -o reportsS3/reportS3B_SR_2_PCPPAX.txt -s 24 -t 'SR_2_PCPPAX' -m 'S3B' -tk ${TOKEN} 
echo "Done!"
