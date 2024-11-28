def eval_spans(pred_spans,ref_spans):
    """
    Receives two lists of spans and returns a precision, recall,
    f-score
    Args:
       pred_spans (list): a list of spans (a span is a dictionary)
       ref_spans  (list): a list of spans (a span is a dictionary)
    KwArgs:
      labeled: whether the span labels are take into account in the evaluation
    Returns:
       (P,R,F) a triple of floats
    """
    pred_spans = set(pred_spans)
    ref_spans  = set(ref_spans) 

    pred_correct = pred_spans & ref_spans
    prec  = len(pred_correct) /  len(pred_spans)
    recll = len(pred_correct) /  len(ref_spans)
    f1    = (2 * prec * recll) / (prec + recll)
    return (prec,recll,f1)


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
                 if token['arg'].startswith['B']:
                     current_start = token['idx']
                     current_lbl = token['arg'].split('-')[-1]
                 elif token['arg'].startswith['I']:
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


def align_spans(pred_spans,ref_spans):
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
                if len(rtoks & ptoks) > len(rtoks)/2:
                    aspans.append(rspan)
        if not added:
            aspans.append(pspan)
    return aspans


def eval_dataset(pred_annotations,ref_annotations,labeled=True):
    """
    Performs spans and relation evaluations for the given annotations dictionaries.
    At least tokens with BIO annotations are expected in all cases.
    Args:
        pred_annotations (dict): an annotation dict (possibly missing some keys)
        ref_annotations (dict) : an annotation dict (possibly missing some keys)
        labeled (bool)          : wether span labels are taken into account 
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

    strict_scores  = [ ]
    aligned_scores = [ ]
    for pred,ref in zip(pred_annotations,ref_annotations):
        if 'tokens' in pred and 'tokens' in ref:
            pred_spans         = get_spans(pred,labeled)
            ref_spans          = get_spans(ref,labeled)
            aligned_pred_spans = align_spans(pred_spans,ref_spans)
            strict_scores.append( eval_spans(pred_spans,ref_spans) )
            aligned_scores.append( eval_spans(aligned_pred_spans,ref_spans) )
        else:
            raise Exception('The annotations do not contain a "tokens" field ! aborting.')
    p,r,f    = avg_metric(strict_scores)
    ap,ar,af = avg_metric(aligned_scores)
    return {"spans":{'strict': {'p':p,'r':r,'f':f},'relaxed':{'p':ap,'r':ar,'f':af}}}


def display_eval(pred_annotations,ref_annotations):
    """
    Prints on stdout the results of all the possible evaluations for the given annotations dictionaries.
    At least tokens with BIO annotations are expected in all cases.
    Args:
        pred_annotations (dict): an annotation dict (possibly missing some keys)
        ref_annotations (dict): an annotation dict (possibly missing some keys)
    """
    labeled  = eval_dataset(pred_annotations,ref_annotations,labeled=True)
    ulabeled = eval_dataset(pred_annotations,ref_annotations,labeled=False)
    
    print(f"""

    STRICT EVALUATION
    > Argument mining spans (unlabeled)
      Precision : {ulabeled['spans']['strict']['p']} 
      Recall    : {ulabeled['spans']['strict']['r']}
      F-score   : {ulabeled['spans']['strict']['f']}
    > Argument mining spans (labeled)
      Precision : {labeled['spans']['strict']['p']} 
      Recall    : {labeled['spans']['strict']['r']} 
      F-score   : {labeled['spans']['strict']['f']}

    RELAXED EVALUATION
    > Argument mining spans (unlabeled)
      Precision : {ulabeled['spans']['relaxed']['p']} 
      Recall    : {ulabeled['spans']['relaxed']['r']}
      F-score   : {ulabeled['spans']['relaxed']['f']}
    > Argument mining spans (labeled)
      Precision : {labeled['spans']['relaxed']['p']} 
      Recall    : {labeled['spans']['relaxed']['r']} 
      F-score   : {labeled['spans']['relaxed']['f']}
""")
       



if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(
                    prog='python evaluate.py [pred_file] [test_file]',
                    description='Computes evaluation metrics for argument mining tasks.')

    parser.add_argument('pred_file')
    parser.add_argument('ref_file')
    parser.add_argument('--tsv',help="outputs the evaluation results in tsv format rather than by pretty printing") 
    args = parser.parse_args()

    with open(args.pred_file) as preds_in:
        with open(args.ref_file) as ref_in:
            preds = json.loads(preds_in.read())
            refs = json.loads(ref_in.read())
            #try:
            display_eval(preds,refs)
            #except Exception as e:
            #    print('*',e)

            

    
    
