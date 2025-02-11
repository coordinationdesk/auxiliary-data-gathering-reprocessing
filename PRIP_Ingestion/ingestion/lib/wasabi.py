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

def download_from_wasabi(path_to_mc,bucket,auxiliary_file,uuid,target_folder,mode="dev"):
    '''
    '''
    try:
        auxiliary_data_file = os.path.join(target_folder, auxiliary_file)
        download_command = [path_to_mc ,
                            "cp", bucket+"/%s/%s" % (uuid,auxiliary_file),
                            auxiliary_data_file]
        if mode == "dev" :
            print( "mc command => %s \n" % download_command )
            return 0
        else:
            process = subprocess.run( download_command)
            process.check_returncode()
            return 0
    except Exception as e:
        print(e)
        return 1

# remove auxiliaray data file from wasabi
def remove_from_wasabi(path_to_mc,bucket,file_name,uuid,mode="dev"):
    try:
        remove_command = [path_to_mc ,
                          "rm",
                          bucket+"/%s/%s" % (uuid,file_name)]
        if mode == "dev" :
            print( "mc command => %s \n" % remove_command )
            return 0
        else:
            process = subprocess.run( remove_command)
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

