#!/bin/bash

SAVED='saved'
METADATA='metadata'
SELECTED='selected'


clearall=$1
dir=$2
num=$3
typedir=$4
runlocal=$5


if [ "$dir" = "" ]; then
  echo "dir cannot be empty!"
  exit 1
fi

if [ "$num" = "" ]; then
  num=01
fi

if [ "$typedir" = "" ]; then
  typedir=$SAVED
fi

image_path="./${typedir}/${dir}/${SELECTED}_${num}"



echo "param clearall is [${clearall}]"
if [ $clearall -eq 1 ]; then
  echo 'do clearall'
  # 删除图和文本，clearall 全删除
  rm -rf $image_path
else
  # 仅删除文本
  rm -rf $image_path/*.txt
fi






if [ "$runlocal" = "" ]; then

  metadata_path="./${typedir}/${dir}/${METADATA}_${num}.json"
  rm -rf $metadata_path
  git add $metadata_path
  git commit -m"remove metadata"
  git push

  ssh 44 << remotessh
  cd /home/admin/github/showMan
  git pull
  sh clear_inst.sh $clearall $dir $num $typedir '1'
  exit
remotessh

fi