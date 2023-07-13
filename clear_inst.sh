#!/bin/bash

SAVED='saved'
METADATA='metadata'
SELECTED='selected'


clearall=$1
dir=$2
num=$3
typedir=$4


echo 11
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

echo 12
image_path="./${typedir}/${dir}/${SELECTED}_${num}"
metadata_path="./${typedir}/${dir}/${METADATA}_${num}.json"


echo 13
rm -rf $metadata_path

echo "clearall is [${clearall}]"
if [ $clearall -eq 1 ]; then
  echo 'clearall'
  # 删除图和文本，clearall 全删除
  rm -rf $image_path
else
  # 仅删除文本
  rm -rf $image_path/*.txt
fi

git add $metadata_path
git commit -m"remove metadata"
git push