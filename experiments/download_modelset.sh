#!/bin/sh

mkdir -p data
cd data
mkdir -p dataset
cd dataset

wget -O modelset-lines-dedup.txt   http://models-lab.inf.um.es/files/model-mate/dataset/modelset-lines-dedup.txt
wget -O modelset-normal-dedup.json http://models-lab.inf.um.es/files/model-mate/dataset/modelset-normal-dedup.json
wget -O modelset-token-dedup.txt   http://models-lab.inf.um.es/files/model-mate/dataset/modelset-token-dedup.txt
wget -O xtext-mar-dups.txt         http://models-lab.inf.um.es/files/model-mate/dataset/xtext-mar-dups.txt