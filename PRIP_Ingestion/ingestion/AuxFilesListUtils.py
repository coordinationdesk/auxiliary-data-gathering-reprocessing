

def get_aux_names_from_file(filepath):
    with open(filepath) as f:
        names = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    names = [x.strip() for x in names if len(x)] 
    return names
