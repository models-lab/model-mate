#! /bin/sh

mkdir -p data/dataset
cd data/dataset

wget -O modelset-lines-dedup.txt   http://models-lab.inf.um.es/files/model-mate/dataset/modelset-lines-dedup.txt
wget -O modelset-normal-dedup.json http://models-lab.inf.um.es/files/model-mate/dataset/modelset-normal-dedup.json
wget -O modelset-token-dedup.txt   http://models-lab.inf.um.es/files/model-mate/dataset/modelset-token-dedup.txt
wget -O xtext-mar-dup.txt          http://models-lab.inf.um.es/files/model-mate/dataset/xtext-mar-dup.txt
wget -O xtext-mar-dedup.txt        http://models-lab.inf.um.es/files/model-mate/dataset/xtext-mar-dedup.txt
wget -O ecore-mar-lines-dedup.txt  http://models-lab.inf.um.es/files/model-mate/dataset/ecore-mar-lines-dedup.txt
wget -O ecore-mar-token-dedup.txt  http://models-lab.inf.um.es/files/model-mate/dataset/ecore-mar-token-dedup.txt

