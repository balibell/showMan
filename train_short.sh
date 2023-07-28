#!/bin/bash



instancename=$1
trainer=$2

if [ "$instancename" = "" ]; then
  echo "instancename must not be empty!"
  exit
fi


if [ "$trainer" = "" ]; then
trainer="train_network.py"
fi


relativedir=./training/${instancename}
git add "$relativedir"
git commit -m"training changed"s
git pull
git push



dirname=$instancename
if [ "$trainer" = "fine_tune.py" ]; then
  dirname="${dirname}_finetune"
elif [ "$trainer" = "train_network.py" ]; then
  dirname="${dirname}_network"
elif [ "$trainer" = "sdxl_train_network.py" ]; then
  dirname="sdxl_${dirname}_network"
else
  dirname="${dirname}_db"
fi

modelpath=/home/admin/models/train/$dirname
if [ "$trainer" = "train_network.py" ]; then
  modelpath=/home/admin/lora/train/$dirname
fi


ssh 45 << remotessh
mkdir -p $modelpath
rm -rf $modelpath/*
exit
remotessh



ssh 44 << remotessh
source ~/.zshrc

echo "======================= training server =========================="
hostname
echo "=================================================================="

mkdir -p $modelpath
rm -rf $modelpath/*

conda activate dbtrain
cd /home/admin/github/showMan/
git pull
echo "sh training/start_train.sh $instancename $trainer"
sh training/start_train.sh $instancename $trainer
exit
remotessh


