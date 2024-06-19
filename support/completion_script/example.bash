TOKEN=$1
mkdir reportsS1
mkdir reportsS2
mkdir reportsS3

# TODO: Read from Aux type list file
# Sat type short_type, step
#S1
: <<'JUMP1'
python verify_completion.py -o reportsS1/reportS1_WND.txt -s 3 -t 'AUX_WND' -m 'S1' -tk ${TOKEN} -ss '00-00-01-00' &
python verify_completion.py -o reportsS1/reportS1_WAV.txt -s 3 -t 'AUX_WAV' -m 'S1' -tk ${TOKEN} &
python verify_completion.py -o reportsS1/reportS1_ICE.txt -s 24 -t 'AUX_ICE' -m 'S1' -tk ${TOKEN} &
python verify_completion.py -o reportsS1/reportS1A_POEORB.txt -s 24 -t 'AUX_POEORB' -m 'S1A' -tk ${TOKEN} -ss '00-00-01-00' &
python verify_completion.py -o reportsS1/reportS1B_POEORB.txt -s 24 -t 'AUX_POEORB' -m 'S1B' -tk ${TOKEN} -ss '00-00-01-00' &
JUMP1

#S2
#: <<'JUMP2'
python verify_completion.py -o reportsS2/reportS2_UT1UTC.txt -s 168 -t 'AUX_UT1UTC' -m 'S2' -tk ${TOKEN} &
python verify_completion.py -o reportsS2/reportS2_ECMWFD.txt -s 12 -t 'AUX_ECMWFD' -m 'S2' -tk ${TOKEN} &
python verify_completion.py -o reportsS2/reportS2_CAMSAN.txt -s 24 -t 'AUX_CAMSAN' -m 'S2' -tk ${TOKEN} &
python verify_completion.py -o reportsS2/reportS2_CAMSRE.txt -s 24 -t 'AUX_CAMSRE' -m 'S2' -tk ${TOKEN} &
#JUMP2

#S3
# TODO: create a associative array with type, followed by satellite/step, browse the array and build commands
: <<'JUMP3'
python verify_completion.py -o reportsS3/reportS3A_AX___FRO_AX.txt -s 24 -t 'AX___FRO_AX' -m 'S3A' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3B_AX___FRO_AX.txt -s 24 -t 'AX___FRO_AX' -m 'S3B' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__AX___MFA_AX.txt -s 6 -t 'AX___MFA_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__AX___MA1_AX.txt -s 6 -t 'AX___MA1_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__AX___MA2_AX.txt -s 6 -t 'AX___MA2_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__AX___BB2_AX.txt -s 720 -t 'AX___BB2_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3A_SR___POEPAX.txt -s 24 -t 'SR___POEPAX' -m 'S3A' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3B_SR___POEPAX.txt -s 24 -t 'SR___POEPAX' -m 'S3B' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3A_SR_1_USO_AX.txt -s 24 -t 'SR_1_USO_AX' -m 'S3A' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3B_SR_1_USO_AX.txt -s 24 -t 'SR_1_USO_AX' -m 'S3B' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__SR_2_RMO_AX.txt -s 6 -t 'SR_2_RMO_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__SR_2_POL_AX.txt -s 168 -t 'SR_2_POL_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3A_SR_2_RGI_AX.txt -s 24 -t 'SR_2_RGI_AX' -m 'S3A' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3B_SR_2_RGI_AX.txt -s 24 -t 'SR_2_RGI_AX' -m 'S3B' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__SR_2_SIC_AX.txt -s 72 -t 'SR_2_SIC_AX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3__SL_2_SSTAAX.txt -s 24 -t 'SL_2_SSTAAX' -m 'S3' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3A_SR_2_PCPPAX.txt -s 24 -t 'SR_2_PCPPAX' -m 'S3A' -tk ${TOKEN} &
python verify_completion.py -o reportsS3/reportS3B_SR_2_PCPPAX.txt -s 24 -t 'SR_2_PCPPAX' -m 'S3B' -tk ${TOKEN} &
JUMP3

wait
echo "Done!"
