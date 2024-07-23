#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import requests
from requests.auth import HTTPBasicAuth
from calendar import monthrange

#lta_baseurl = "lta.cloudferro.copernicus.eu"
lta_baseurl = "aip.acri-st.fr"
coreURL = f"https://{lta_baseurl}/odata/v1/Products?$filter=ContentDate/Start gt %04d-%02d-%02dT00:00:00.000000Z and ContentDate/Start lt %04d-%02d-%02dT23:59:59.999999Z and contains(Name,'_RAW__0S')&$top=200"

nbRequestsMaxTries = 5

def getL0(year, month, ltaUsr, ltaPwd):
    headers = {'Content-type': 'application/json'}
    days_in_month = monthrange(year,month)[1]
    names = set()
    authentification = HTTPBasicAuth(ltaUsr, ltaPwd)
    with open("S1_L0_names_%02d_%04d.txt" % (month,year) ,"w") as l0_names:

        previousNbDays = 0
        for nb_days in [10,20,days_in_month]:
            # On découpe le mois en plusieurs sections pour éviter un traitement trop long pour LTA
            start_day = nb_days - (nb_days - previousNbDays) + 1
            previousNbDays = nb_days

            #Construction de la requête
            request = (coreURL + "&$count=true") % (year,month,start_day,year,month,nb_days)
            print(request)

            resp = None
            requestTriesLeft = nbRequestsMaxTries

            while ((resp is None) or (resp.status_code != 200)) and (requestTriesLeft > 0):
                requestTriesLeft -= 1
                print('Sending request try : [%s/%s]' % (nbRequestsMaxTries - requestTriesLeft, nbRequestsMaxTries))
                resp = requests.get(request, auth=authentification,headers=headers)

            if resp.status_code == 200:
                count = int(resp.json()["@odata.count"])
                nb_steps = int(count/200)
                
                for aux in resp.json()["value"]:
                    name = aux['Name']
                    names.add(name)

                for step in range( nb_steps ):
                    # On boucle sur toutes les pages de 200 fichiers L0

                    # Mise à jour de la requete
                    request = (coreURL + "&$skip=%d") % (year,month,start_day,year,month,nb_days,(step+1)*200)
                    print(request)

                    resp = None
                    requestTriesLeft = nbRequestsMaxTries

                    while ((resp is None) or (resp.status_code != 200)) and (requestTriesLeft > 0):
                        requestTriesLeft -= 1
                        print('Sending request try : [%s/%s]' % (nbRequestsMaxTries - requestTriesLeft, nbRequestsMaxTries))
                        resp = requests.get(request, auth=authentification,headers=headers)

                    if resp.status_code == 200:
                        for aux in resp.json()["value"]:
                            name = aux['Name']
                            names.add(name)
                    else:
                        raise Exception("Bad return code for request: "+request)
            else:
                raise Exception("Bad return code for request: "+request)

        names = sorted(names)
        for aux in names:
            print(aux)
            l0_names.write(str(aux) + '\n')

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="This script allows you to get the S1 level 0 product names from LTA CloudFerro for a given month and year",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-y", "--year",
                        help="Year",
                        required=True)
    parser.add_argument("-m", "--month",
                        help="Month",
                        default="all",
                        required=False)
    parser.add_argument("-u", "--user",
                        help="LTA user",
                        required=True)
    parser.add_argument("-pwd", "--password",
                        help="LTA password",
                        required=True)

    args = parser.parse_args()
    year = int(args.year)

    if args.month == "all":
        for m in range(12):
            getL0(year, int(m+1), args.user, args.password)
    else :
        month = int(args.month)
        getL0(year, month, args.user, args.password)

