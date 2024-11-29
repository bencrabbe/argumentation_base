def eval_spans(pred_spans,ref_spans):
    """
    Receives two lists of spans and returns a precision, recall,
    f-score
    Args:
       pred_spans (list): a list of spans (a span is a tuple)
       ref_spans  (list): a list of spans (a span is a tuple)

    Returns:
       (P,R,F) a triple of floats
    """
    pred_spans = set(pred_spans)
    ref_spans  = set(ref_spans) 

    pred_correct = pred_spans & ref_spans
    prec  = len(pred_correct) /  len(pred_spans)
    recll = len(pred_correct) /  len(ref_spans)

    if prec + recll == 0:
        return (0,0,0)

    f1    = (2 * prec * recll) / (prec + recll)
    return (prec,recll,f1)


def eval_rels(pred_rels,ref_rels):
   
    pred_correct = pred_rels & ref_rels
    prec  = len(pred_correct) /  len(pred_rels)
    recll = len(pred_correct) /  len(ref_rels)

    if prec + recll == 0:
        return (0,0,0)
    
    f1    = (2 * prec * recll) / (prec + recll)
    return (prec,recll,f1)


def get_rels(annotations,labeled=True):
    """
    Gets the rels from the annotations and converts them to span
    Args:
       annotations (dict) : the annotation dict
    KwArgs:
       labeled     (bool) : whether the relations are labeled or not 
    Returns:
       a list of rels as tuples
    Raises:
       Exception if rels are not in the annotations
    """
    if 'rels' not in annotations:
        raise Exception('Tried to extract relations from annotation but it failed. Aborting.')
    
    if labeled:
        rels = { (tuple(rel['src']),tuple(rel['tgt']), rel['name'])  for rel in annotations['rels'] } 
    else:
        rels = { (tuple(rel['src']),tuple(rel['tgt']))  for rel in annotations['rels'] } 

    return rels


def align_rels(pred_rels,ref_rels,alpha):
    """
    Aligns the node rels in the pred with node rels in the ref
    """
    arels = [  ]
    for prel in pred_rels:
        src = False
        tgt = False
        psrc,ptgt,*plabel = prel
        psrc_tokens = set(range(psrc[0],psrc[1]+1))
        ptgt_tokens = set(range(ptgt[0],ptgt[1]+1))
        for rrel in ref_rels:
            rsrc,rtgt,*rlabel = rrel
            rsrc_tokens = set(range(rsrc[0],rsrc[1]+1))
            rtgt_tokens = set(range(rtgt[0],rtgt[1]+1))

            if len(psrc_tokens & rsrc_tokens) > (alpha*len(rsrc_tokens)):
                src = rsrc
            
            if len(ptgt_tokens & rtgt_tokens) > (alpha*len(rtgt_tokens)):
                tgt = rtgt

        if not src:
            src = psrc
        if not tgt:
            tgt = ptgt
        if plabel:
            arels.append((src,tgt,plabel[0]))
        else:
            arels.append((src,tgt))
    return set(arels)


from random import random

def get_spans(annotations,labeled=True):
     """
     Gets the spans from pred annotations in a robust manner: 
     if the spans are missing from the predicted annotations, then they are inferred from token annotations
     
     Args:
         annotations (dict) : annotations
     KwArgs:
        labeled(bool): whether the returned spans are labelled or not
     Returns:
       a set of pred spans as tuples. a set of ref spans as tuples
     """
     if 'spans' in annotations:         
         spans = annotations['spans']
     else:

         spans = [ ]
         current_lbl   = ''
         current_start = -1
            
         for paragraph in annotations['tokens']:
             for token in paragraph:
                 if token['arg'].startswith('B'):
                     current_start = token['idx']
                     current_lbl = token['arg'].split('-')[-1]
                 elif token['arg'].startswith('I'):
                     pass
                 else: 
                     if current_lbl:
                         spans.append( {'name':current_lbl,'start':current_start,'end':token['idx'] - 1 } )
                         current_lbl = ''
                         current_start = -1
             if current_lbl:
                spans.append( {'name':current_lbl,'start':current_start,'end':paragraph[-1]['idx']})
                current_lbl = ''
                current_start = -1

     if labeled:
        return { (span['start'],span['end'],span['name']) for span in spans}
     else:
        return { (span['start'],span['end']) for span in spans}


def align_spans(pred_spans,ref_spans,alpha):
    """
    Align pred spans on ref spans as soon as their overlap is greater than 50%
    Args:
       pred_spans : list of tuples 
       ref_spans  : list of tuples
    Returns:
       list of tuples. The list of aligned predicted spans
    """
    aspans = [ ]
    for pspan in pred_spans:
        added = False
        pstart,pend,*plabel = pspan        
        for rspan in ref_spans:
            rstart,rend,*rlabel = rspan
            if plabel == rlabel:
                ptoks = set(range(pstart,pend+1))
                rtoks = set(range(rstart,rend+1))
                if len(rtoks & ptoks) > alpha*len(rtoks) :
                    aspans.append(rspan)
        if not added:
            aspans.append(pspan)
    return aspans




def eval_dataset(pred_annotations,ref_annotations,labeled=True,alpha=0.5):
    """
    Performs spans and relation evaluations for the given annotations dictionaries.
    At least tokens with BIO annotations are expected in all cases.
    Args:
        pred_annotations (dict): an annotation dict (possibly missing some keys)
        ref_annotations (dict) : an annotation dict (possibly missing some keys)
        labeled (bool)          : wether span labels are taken into account
        alpha (float)          : threshold for approximative span matching
    Returns dict with evaluation results
    """
    def avg_metric(score_list):
        p = 0
        r = 0
        f = 0
        N = len(score_list)
        for x,y,z in score_list:
            p += x
            r += y
            f += z
        return p/N,r/N,f/N

    strict_span_scores  = [ ]
    aligned_span_scores = [ ]
    strict_rel_scores   = [ ]
    aligned_rel_scores  = [ ]

    for pred,ref in zip(pred_annotations,ref_annotations):
                    
        if 'tokens' in pred and 'tokens' in ref:
            if len(pred['tokens']) != len(ref['tokens']):
                raise Exception('pred data length is different from test data length. Different number of paragraphs in a document. aborting')
            else:
                for paragA,paragB in zip(pred['tokens'],ref['tokens']):
                    if len(paragA) != len(paragB):
                        raise Exception('pred data length is different from test data length. Different number of tokens in a paragraph. aborting')

            pred_spans         = get_spans(pred,labeled)
            ref_spans          = get_spans(ref,labeled)
            aligned_pred_spans = align_spans(pred_spans,ref_spans,alpha)
            strict_span_scores.append( eval_spans(pred_spans,ref_spans) )
            aligned_span_scores.append( eval_spans(aligned_pred_spans,ref_spans) )
            if 'rels' in pred and 'rels' in ref:
                pred_rels = get_rels(pred,labeled)
                ref_rels  = get_rels(ref,labeled)
                aligned_pred_rels = align_rels(pred_rels,ref_rels,alpha)
                strict_rel_scores.append( eval_rels(pred_rels,ref_rels) )
                aligned_rel_scores.append( eval_rels(aligned_pred_rels,ref_rels) )
                
        else:
            raise Exception('The annotations do not contain a "tokens" field ! aborting.')
    sp,sr,sf    = avg_metric(strict_span_scores)
    asp,asr,asf = avg_metric(aligned_span_scores)
    if strict_rel_scores:
        rp,rr,rf    = avg_metric(strict_rel_scores)
        arp,arr,arf = avg_metric(aligned_rel_scores)
        return {"spans":{'strict': {'p':sp,'r':sr,'f':sf},'relaxed':{'p':asp,'r':asr,'f':asf}},
                "rels":{'strict': {'p':rp,'r':rr,'f':rf},'relaxed':{'p':arp,'r':arr,'f':arf}}}
    else:
        return {"spans":{'strict': {'p':sp,'r':sr,'f':sf},'relaxed':{'p':asp,'r':asr,'f':asf}}}


def display_eval(pred_annotations,ref_annotations,alpha=0.5):
    """
    Prints on stdout the results of all the possible evaluations for the given annotations dictionaries.
    At least tokens with BIO annotations are expected in all cases.
    Args:
        pred_annotations (dict): an annotation dict (possibly missing some keys)
        ref_annotations (dict): an annotation dict (possibly missing some keys)
        alpha (float) : threshold of common tokens for approximative matching of spans 
    """
    ulabeled = eval_dataset(pred_annotations,ref_annotations,labeled=False,alpha=alpha)
    labeled  = eval_dataset(pred_annotations,ref_annotations,labeled=True,alpha=alpha)
    
    print(f"""

********************** SPANS *************************** 
   STRICT EVALUATION
    > Argument mining spans (unlabeled)
      Precision : {ulabeled['spans']['strict']['p']} 
      Recall    : {ulabeled['spans']['strict']['r']}
      F-score   : {ulabeled['spans']['strict']['f']}
    > Argument mining spans (labeled)
      Precision : {labeled['spans']['strict']['p']} 
      Recall    : {labeled['spans']['strict']['r']} 
      F-score   : {labeled['spans']['strict']['f']}

    RELAXED EVALUATION (\u03B1 = {alpha})
    > Argument mining spans (unlabeled)
      Precision : {ulabeled['spans']['relaxed']['p']} 
      Recall    : {ulabeled['spans']['relaxed']['r']}
      F-score   : {ulabeled['spans']['relaxed']['f']}
    > Argument mining spans (labeled)
      Precision : {labeled['spans']['relaxed']['p']} 
      Recall    : {labeled['spans']['relaxed']['r']} 
      F-score   : {labeled['spans']['relaxed']['f']}
""")

    if 'rels' in labeled and 'rels' in ulabeled:
        print(f"""

******************* RELATIONS *************************** 
   STRICT EVALUATION
    > Argument mining spans (unlabeled)
      Precision : {ulabeled['rels']['strict']['p']} 
      Recall    : {ulabeled['rels']['strict']['r']}
      F-score   : {ulabeled['rels']['strict']['f']}
    > Argument mining spans (labeled)
      Precision : {labeled['rels']['strict']['p']} 
      Recall    : {labeled['rels']['strict']['r']} 
      F-score   : {labeled['rels']['strict']['f']}

    RELAXED EVALUATION (\u03B1 = {alpha})
    > Argument mining spans (unlabeled)
      Precision : {ulabeled['rels']['relaxed']['p']} 
      Recall    : {ulabeled['rels']['relaxed']['r']}
      F-score   : {ulabeled['rels']['relaxed']['f']}
    > Argument mining spans (labeled)
      Precision : {labeled['rels']['relaxed']['p']} 
      Recall    : {labeled['rels']['relaxed']['r']} 
      F-score   : {labeled['rels']['relaxed']['f']}
""")       



if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(
                    prog='python evaluate.py [pred_file] [test_file]',
                    description='Computes evaluation metrics for argument mining tasks.')

    parser.add_argument('pred_file')
    parser.add_argument('ref_file')
    parser.add_argument('--alpha',default=0.5,type=float)
    #parser.add_argument('--tsv',help="outputs the evaluation results in tsv format rather than by pretty printing")
    args = parser.parse_args()

    with open(args.pred_file) as preds_in:
        with open(args.ref_file) as ref_in:

            preds = json.loads(preds_in.read())
            refs = json.loads(ref_in.read())
            
            try:
                display_eval(preds,refs,alpha=args.alpha)
            except Exception as e:
                print('[error]',e)

            

    
    
