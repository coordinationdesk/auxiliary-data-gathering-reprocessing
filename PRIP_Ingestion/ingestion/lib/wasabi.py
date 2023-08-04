import os
import subprocess


# upload auxiliaray data file to wasabi
def upload_to_wasabi(path_to_mc,bucket,auxiliary_data_file,uuid,mode="dev"):
    try:
        file_name = os.path.basename(auxiliary_data_file)
        upload_command = [path_to_mc ,
                          "cp",
                          auxiliary_data_file, bucket+"/%s/%s" % (uuid,file_name)]
        if mode == "dev" :
            print( "mc command => %s \n" % upload_command )
            return 0
        else:
            process = subprocess.run( upload_command)
            process.check_returncode()
            return 0
    except Exception as e:
        print(e)
        return 1


# Generate a listing of already uploaded files
def generate_wasabi_listing(path_to_mc,bucket):
    upload_command = [path_to_mc,
                      "ls",
                      "--recursive", bucket]

    process = subprocess.run( upload_command, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    if process.returncode != 0:
        raise Exception("Error getting S3 listing")
    text_listing = process.stdout
    print(text_listing)
    listing = text_listing.split('\n')
    wasabi_listing = []

    for line in listing:
        if '.txt' not in line:
            try:
                file_name = line.split('B ')[1].split('/')[1].split('\n')[0].strip()
                wasabi_listing.append(file_name)
            except Exception as e:
                print(e)

    return wasabi_listing