#!/bin/bash



instancename=$1
nohup=$2
trainer=$3

if [ "$instancename" = "" ]; then
  echo "instancename must not be empty!"
  exit
fi

nohupsuf=
if [ "$nohup" != "" ]; then
  nohup="nohup"
  nohupsuf="&"
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
else
  dirname="${dirname}_db"
fi


if [ "$trainer" = "train_network.py" ]; then
ssh 44 << remotessh
source ~/.zshrc
node --version
python --version
mkdir -p /home/admin/lora/train/$dirname
echo "remove train loras"
rm -rf /home/admin/lora/train/$dirname/*
exit
remotessh
else
ssh 44 << remotessh
source ~/.zshrc
node --version
python --version
mkdir -p /home/admin/models/train/$dirname
rm -rf /home/admin/models/train/$dirname/*
exit
remotessh
fi

ssh 45 << remotessh
source ~/.zshrc
node --version
python --version
conda activate dbtrain
cd ~/github/showMan/
git pull

echo "$nohup sh training/start_train.sh $instancename $trainer $nohupsuf"
$nohup sh training/start_train.sh $instancename $trainer $nohupsuf
exit
remotessh