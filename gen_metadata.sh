#!/bin/bash

typedir=$1
dir=$2
num=$3

METADATA='metadata'
SELECTED='selected'

image_path="./${typedir}/${dir}/${SELECTED}_${num}"
metadata="./${typedir}/${dir}/${METADATA}_${num}.json"

txt_num=$((`ls -l $image_path | grep '\.txt' | wc -l`))
image_num=$((`ls -l $image_path | grep -v '\.txt' | wc -l`))

echo "txt_num is ${txt_num} and image_num is ${image_num}"
if [ $txt_num -ne $image_num ]; then
  sh tagger.sh 0 $typedir $dir $num
fi


python pyutil/genMetadata.py $image_path $metadata
