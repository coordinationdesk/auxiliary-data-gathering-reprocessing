Utility scripts to load configurations for S1 Baseline computation
Configuration refers to selection of AuxFiles based on attributes of L0 Product,
such as Mode and Polarization.
Please, be aware that no checks are performed: input rows are inserted into the database table as they are

1. Database container service port shall be exposed (from compose yml configuration)
2. CSV file containing configuration shall have rows in the form:
AuxTypeLongName,L0ParameterName,L0ParameterValue
L0ParameterName should be one of: Mode,Polarization   

To execute:
python3 baseline_auxtypel0params.py -m S1 -dbh localhost -dbn reprocessingdatabaseline -dbu reprocessingdatabaseline -dbp $REPROCESSINGDATABASELINE_POSTGRES_PASSWORD -p <DB Port> -i ./s1_auxtype_l0attributes.csv

This folder contains the files:
s1_auxtype_l0attributes.csv (all the aux type confiugration for Mode and Polarization)
s1_auxtype_mode.csv         (Only the aux type configuration for Mode)
s1_auxtype_polarization.csv         (Only the aux type configuration for Polarization)

