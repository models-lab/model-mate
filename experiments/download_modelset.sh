#!/bin/sh

mkdir -p data
cd data
mkdir -p dataset
cd dataset

wget http://models-lab.inf.um.es/files/model-mate/dataset/modelset-lines-dedup.txt
wget http://models-lab.inf.um.es/files/model-mate/dataset/modelset-normal-dedup.json
wget http://models-lab.inf.um.es/files/model-mate/dataset/modelset-token-dedup.txt