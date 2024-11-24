#creates the json files in the main directories

#Argument Annotated Essays
wget https://tudatalib.ulb.tu-darmstadt.de/bitstream/handle/tudatalib/2422/ArgumentAnnotatedEssays-2.0.zip
unzip ArgumentAnnotatedEssays-2.0.zip
unzip ArgumentAnnotatedEssays-2.0/brat-project-final.zip
mv brat-project-final aae_brat

rm -f ArgumentAnnotatedEssays-2.0.zip
rm -Rf ArgumentAnnotatedEssays-2.0
rm -Rf __MACOSX

python brat_import.py aae_brat
mv essay*.json aae_brat

#split
mkdir aae_split
wget https://raw.githubusercontent.com/UKPLab/acl2017-neural_end2end_am/refs/heads/master/data/conll/Essay_Level/train.dat
wget https://raw.githubusercontent.com/UKPLab/acl2017-neural_end2end_am/refs/heads/master/data/conll/Essay_Level/dev.dat
wget https://raw.githubusercontent.com/UKPLab/acl2017-neural_end2end_am/refs/heads/master/data/conll/Essay_Level/test.dat
mv *.dat aae_split

python make_aae_split.py
rm -Rf aae_split




#AbstRCT
git clone https://gitlab.com/tomaye/abstrct.git
mv abstrct tmp
mv tmp/AbstRCT_corpus/data abstrct_brat
rm -Rf tmp

python brat_import.py abstrct_brat/train/neoplasm_train
mv *.json abstrct_brat/data/train/neoplasm_train/
python brat_import.py abstrct_brat/dev/neoplasm_dev/
mv *.json abstrct_brat/dev/neoplasm_dev/
python brat_import.py abstrct_brat/test/neoplasm_test/
mv *.json abstrct_brat/test/neoplasm_test/
python brat_import.py abstrct_brat/test/glaucoma_test/
mv *.json abstrct_brat/test/glaucoma_test/
python brat_import.py abstrct_brat/test/mixed_test/
mv *.json abstrct_brat/test/mixed_test/



