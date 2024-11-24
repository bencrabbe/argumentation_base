#computes the splits for the Annotated Essays json files using the conll reference of S. Eger 

def connl2vocab(conllfilename):

    with open(conllfilename) as infile:
        vocab = []
        for line in infile:
            if line and not line.isspace():
                token = line.split()[1]
                vocab.append(token)
        return set(vocab)

def commonvocab(jsonvocab,vocab):
    """
    Returns the proportion of vocab in the json file found in the
    reference vocab (setwise computation)
    """
    jsonvocab = set(jsonvocab)
    vocab     = set(vocab)
    #print(jsonvocab)
    #print(vocab)
    #print()
    counts    = 0
    for element in jsonvocab:
        if element in vocab:
            counts += 1
    return counts/len(jsonvocab)
                
import os
import json

def get_filenames(jsondir,conllfilename,threshold=0.95):
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
                prop = commonvocab([ token['str'] for token in annotations["tokens"] ],vocab)
                if prop >= threshold:
                    #print("In",filename,"with",prop)
                    selected_files.append(filename)
                else:
                    #print("Out",filename,"with",prop)
                    other_files.append(filename)
                    
    return selected_files,other_files


def write_split(train,dev,test,splitfilename):

    splitdict = {
                 'train':sorted(list(train)),
                 'dev'  :sorted(list(dev)),
                 'test' :sorted(list(test))
                 }
    
    with open(splitfilename,'w') as outfile:
        outfile.write(json.dumps(splitdict))
        
    


if __name__ == '__main__':
    dev_files,otherdev  = get_filenames("aae_brat","aae_split/dev.dat")
    test_files,othertest = get_filenames("aae_brat","aae_split/test.dat")
    trainfilesA = set(otherdev)-set(test_files)
    trainfilesB = set(othertest)-set(dev_files)
    assert(len(trainfilesA) == len(trainfilesB))

    write_split(trainfilesA,dev_files,test_files,"aae_brat/train_dev_test_split.json")
    
