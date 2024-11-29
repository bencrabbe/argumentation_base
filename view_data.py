#This script pretty prints the json data files for manual inspection




def view_dataset(annotations):
    for document in annotations:
        for parag in document['tokens']:
            for token in parag:
                print(f"{token['idx']}\t{token['str']}\t{token['arg']}")
            print()
        for rel in document['rels']:
            print(f"{tuple(rel['src'])}\t{rel['name']}\t{tuple(rel['tgt'])}")
        print()

def view_stats(annotations):
    ndocs   = len(annotations)
    nparags = 0
    ntokens = 0
    for document in annotations:
        nparags += len(document)
        for parag in document['tokens']:
            ntokens += len(parag)
    print(f"""
    num tokens     = {ntokens}
    num parags     = {nparags}
    num documents  = {ndocs}
""")

        
if __name__ == '__main__':
    import json
    import sys

    with open(sys.argv[1]) as infile:
        annotations = json.loads(infile.read())
        view_dataset(annotations)
        print('-'*80)
        view_stats(annotations)
        
