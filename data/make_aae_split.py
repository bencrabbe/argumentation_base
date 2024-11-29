#computes the splits for the Annotated Essays json files using the conll reference of S. Eger 

def connl2vocab(conllfilename):

    with open(conllfilename) as infile:
        vocab = []
        for line in infile:
            if line and not line.isspace():
                token = line.split()[1]
                vocab.append(token)
        return set(vocab)

def commonvocab(jsonvocab,vocab,verbose=False):
    """
    Returns the proportion of vocab in the json file found in the
    reference vocab (setwise computation)
    """
    jsonvocab = set(jsonvocab)
    vocab     = set(vocab)
    common    = jsonvocab & vocab
    if verbose:
        print('missing words',[elt for elt in (jsonvocab-vocab)])
    return len(common)/len(jsonvocab)
                
import os
import json
def get_filenames(jsondir,conllfilename,threshold=0.955):
    """
    Gets the json filenames that are part of the conllfile
    """
    selected_files = []
    other_files    = []
    vocab =  connl2vocab(conllfilename)
    for filename in os.listdir(jsondir):
        if filename.endswith('json'):
            with open(os.path.join(jsondir,filename)) as injson:
                annotations = json.loads(injson.read())
                prop = commonvocab([ token['str'] for paragraph in annotations["tokens"] for token in paragraph ],vocab)
                if prop >= threshold:
                    print("In",filename,"with",prop)
                    selected_files.append(filename)
                    #print( commonvocab([ token['str'] for paragraph in annotations["tokens"] for token in paragraph ],vocab,verbose=True) )
                    
    return selected_files

def write_split(train,dev,test,outdirname):
    
    with open(os.path.join(outdirname,'train.split'),'w') as outfile:
        outfile.write('\n'.join(list(train)))

    with open(os.path.join(outdirname,'dev.split'),'w') as outfile:
        outfile.write('\n'.join(list(dev)))
        
    with open(os.path.join(outdirname,'test.split'),'w') as outfile:
        outfile.write('\n'.join(list(test)))


if __name__ == '__main__':
    all_files   = set([filename for filename in os.listdir("aae_brat") if filename.endswith('json')])
    dev_files   = get_filenames("aae_brat","aae_split/dev.dat")
    test_files  = get_filenames("aae_brat","aae_split/test.dat")
    trainfiles = set(all_files) - set(dev_files) - set(test_files)
    print(f'split train:{len(trainfiles)}, dev:{len(dev_files)}, test:{len(test_files)}')
    write_split(trainfiles,dev_files,test_files,"aae_brat")
    
