import argparse
import json
import os
import sys


def retrieve_aux_type_names(mission, filetypes_dir):
    filetype_names = []
    print("Retrieving aux type names for mission ", mission, " dir ", filetypes_dir, file=sys.stderr,)
    for (dirpath, dirnames, filenames) in os.walk(filetypes_dir):
        print("Curr Dir: ", dirpath, file=sys.stderr,)
        for filename in filenames:
            with open(os.path.join(filetypes_dir, filename)) as curr_file:
                filetype = json.load(curr_file)
                if mission in filetype["Mission"]:
                    filetype_names.append(filetype["LongName"])
    return filetype_names

def get_command_arguments():
    print("Called with command line: ", sys.argv, file=sys.stderr)
    parser = argparse.ArgumentParser(description="This script retrieves a list of configured Aux Types for a Mission",  # main description for help
                                     epilog='Usage samples : \n\tpython mission_aux_types.py -u mission -fd aux_types_folder \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-m", "--mission",
                        help="Single Mission to retrieve",
                        required=True)
    parser.add_argument("-fd", "--filetypes_dir",
                        help="Folder containing filetypes jsons",
                        required=True)
    return parser.parse_args()

def main():
    args = get_command_arguments()
    print(",".join(retrieve_aux_type_names(args.mission, args.filetypes_dir)))

if __name__ == "__main__":
    main()
