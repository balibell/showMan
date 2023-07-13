#!/bin/bash

DIRNAME='teaey'
SELECTED='selected'

prefix=$1

if [ "${prefix}" = "" ]; then
  echo "you should pass a prefix, like ~"
  exit
fi

# 将数据集拉平放在一个目录里，比如 uf1fu_02

rm -rf ${DIRNAME}*

ln -s ${prefix}/github/showMan/saled/${DIRNAME}/${SELECTED}_01 ${DIRNAME}_${SELECTED}_01
ln -s ${prefix}/github/showMan/saled/${DIRNAME}/${SELECTED}_01_lv9 ${DIRNAME}_${SELECTED}_01_lv9


current_path=`pwd`
python ${prefix}/github/sd-scripts/finetune/merge_captions_to_metadata.py --full_path $current_path $current_path/data.json --caption_extension .txt

# 找出目录下空白的txt文件
find ./ -type f -name "*.txt" -empty