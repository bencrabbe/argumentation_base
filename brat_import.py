# Examples are sentences or paragraphs
# each token has a unique linear order id, a form and a BIO tag
# argument nodes are contiguous spans denoted as triples (start-id,end-id,tag)
#     examples are (0,5,claim) or (7,12,premise)
# relations are triples (src node, tgt node, type)
#     examples are ( (7,12), (0,5), attack)

import re
from nltk.tokenize import TweetTokenizer
def tokenize_text(txtfile):
    """
    Splits the text into tokens and returns a list of tokens
    Args:
      txtfile (str) : path to a raw text file
    Returns:
      list of tokens. a token is a triple (charidx,charidx,idx,string)
      with begin and end char indexes in the text
    """
    tt = TweetTokenizer()
    with open(txtfile) as infile:
        rawlist = re.split(r'(\s+)', infile.read())
        toklist = [ ]
        idx     = 0
        cidx    = 0
        for elt in rawlist:
            if not elt.isspace():
                #separates punctuation from main words
                subtokens = tt.tokenize(elt)
                for subt in subtokens: 
                    subtok = (cidx,cidx+len(subt),idx,subt)
                    idx  += 1
                    toklist.append(subtok)
                    cidx += len(subt)
            else:
                cidx += len(elt)
                
        return toklist

    
def read_annotations(annfile):
    """
    Reads the annotation files into a dictionary
    Args:
       annfile (str) : the path to the annotation file
    Returns:
       dict. A dictionary storing the annotations

    @todo Stances are not taken into account
    """
    spans = []
    rels  = []
    with open(annfile) as infile:
        for line in infile:
            annID , A ,*rest = line.split('\t')
            elts = A.split()
            if elts[-1].isdigit() and elts[-2].isdigit():
                spans.append( {"ID":annID, "name":elts[0],"start":int(elts[1]),"end":int(elts[2])} )
            if ':' in elts[-1] and ':' in elts[-2]:
                rels.append({"name":elts[0],"src":elts[1].split(':')[-1],"tgt":elts[2].split(':')[-1]})
        return {"spans":spans,"rels":rels}

def char2tokens(tokens,annotations):
    """
    This replaces char indexing by token indexing in spans and in relations
    Args:
      tokens  (list of tuples)
      annotations (dictionary)
    Returns:
       dict. tokens and annotations reindexed on tokens only
    """
    #update spans
    for span in annotations["spans"]:
        start,end = span["start"],span["end"]
        newstart = -1
        newend   = -1
        for (sidx,eidx,widx,str) in tokens:
            if start >= sidx and start <= eidx:
                newstart = widx
            if end >= sidx and end <= eidx:
                newend = widx
            if newstart >= 0 and newend >= 0:
                break
        span.update({"start":newstart})
        span.update({"end" : newend})
        
    #update rels
    for rel in annotations["rels"]:
        for span in annotations["spans"]:
            if span["ID"] == rel["src"]:
                rel["src"] = (span["start"],span["end"])
            if span["ID"] == rel["tgt"]:
                rel["tgt"] = (span["start"],span["end"])

    #update tokens
    tokens = [{'idx':idx,'str':elt} for  (_,_,idx,elt) in tokens]
    annotations['tokens'] = tokens

    #cleanup spans
    for span in annotations["spans"]:
        del span["ID"]
    return annotations

def annotate_NER(annotations):
    """
    Adds NER annotations directly onto tokens
    Args:
      annotations (dict): the spans are injected onto the tokens and generate a BIO annotation
    Returns
      dict. The updated annotations
    """
    tagdict = {}
    for span in annotations['spans']:
        label,start,end = span['name'],span['start'], span['end']
        tagdict[start] = f'B-{label}'
        for idx in range(start+1,end):
            tagdict[idx] = f'I-{label}'
    
    for token in annotations['tokens']:
        idx = token['idx']
        token['arg'] = tagdict.get(idx,'O')
    
    return annotations


import os
import json
def convert_directory(dirname):
    for filename in os.listdir(dirname):
        if filename.endswith('.ann'):
            prefix,suffix = filename.split('.')
            annotations = read_annotations(os.path.join(dirname,filename))
            tokens      = tokenize_text((os.path.join(dirname,f'{prefix}.txt')))   
            annotations = char2tokens(tokens,annotations)
            annotations = annotate_NER(annotations)
            with open(f'{prefix}.json','w') as outfile:
                outfile.write(json.dumps(annotations))


#annpath  = "abstrct_brat/test/mixed_test/10526263.ann"
#textpath = "abstrct_brat/test/mixed_test/10526263.txt"
#annotations = read_annotations(annpath)
#tokens      = tokenize_text(textpath)
#annotations = char2tokens(tokens,annotations)
#annotations = annotate_NER(annotations)
#print(annotations)



if __name__ == '__main__':
    import sys
    convert_directory(sys.argv[1])
    
