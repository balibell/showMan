#!/bin/bash

typedir=$1
dir=$2
num=$3
instprompt=$4  # 如果这个字段不为空且不为 tagger，则省略掉 tagger 步骤，统一使用这个词作为所有图片的提词

METADATA='metadata'
SELECTED='selected'

image_path="./${typedir}/${dir}/${SELECTED}_${num}"
metadata="./${typedir}/${dir}/${METADATA}_${num}.json"

if [ "$instprompt" = "" ] || [ "$instprompt" = "tagger" ]; then
  txt_num=$((`ls -l $image_path | grep '\.txt' | wc -l`))
  txt_num_v=$((`ls -l $image_path | grep -v '\.txt' | wc -l`))
  image_num=$(expr "$txt_num_v" - 1)
  echo "txt_num is ${txt_num} and image_num is ${image_num}"
  if [ $txt_num -ne $image_num ]; then
    sh tagger.sh 0 $typedir $dir $num
  fi
else
  # 使用统一提词
  python pyutil/promptTxt.py -pa $image_path -pr="$instprompt" -cl=''
fi



python pyutil/genMetadata.py $image_path $metadata
