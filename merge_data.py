# Lerges the json files inside a directory to a single json file.
# This simply creates a document level structure. Each document is indexed separately

import os
import json


def merge_dir(dirname,outfile):

    documents = [ ]
    
    for filename in sorted(os.listdir(dirname)):
        if filename.endswith('.json'):
            with open(os.path.join(dirname,filename)) as infile:
                documents.append(json.loads(infile.read()))
            
    with open(outfile,'w') as outstream:
        outstream.write(json.dumps(documents))

            
if __name__ == '__main__':
    import sys
    merge_dir(sys.argv[1],sys.argv[2])
