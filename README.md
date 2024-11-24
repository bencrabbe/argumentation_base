# Argumentation base documentation

This repository stores argumentation data in a `json` format that is convenient for machine learning, exchange and evaluation.

A dataset is a json file. Each dataset is a list of documents and each document is a dictionary with 3 keys:

 
- `tokens` A list of paragraphs. Each paragraph is a list of tokens. A token is a dictionary of the form:
    - `idx` a unique id for the token in the document
    - `str` the token string
	- `arg` the argument span BIO annotation. This annotation is deduced from the spans.
- `spans` A list of spans. A span is an argument annotation (e.g. Claim, Premise etc.) with 
   - `start` id of the token starting the span
   - `end` id of the last token included in the span
   - `name` the type of the argument
- `rels` A list of argumentative relations between spans. A relation (e.g. attack, support) is an edge that relates two spans:
	- `src` the source span encoded as a couple `(start,end)`   
    - `tgt` the target span encoded as a couple `(start,end)` 
    - `name` the label of the relation

## Installation 

Just run the following on your machine:

```
> git clone git@github.com:bencrabbe/argumentation_base.git
> cd argumentation_base
> sh download_data.sh
```

## Viewing (todo)

The script `view_data.py` provides a pretty printing function for exploring the data


## Evaluation (todo)

- strict evaluation
- relaxed evaluation
- fuzzy evaluation


## Current datasets

Two datasets are currently provided.

- (aae) Argumentation Annotated Essays [(Stab and Gurevych 2017)](https://aclanthology.org/J17-3005.pdf)
- (abstrct) Abstracts ofRandomized Controlled Trials [(Mayer et al. 2020)](https://ecai2020.eu/papers/1470_paper.pdf)



