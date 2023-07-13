#!/bin/bash

# 图片素材需要提前放在 saved 目录里
SAVED='saved'

dir='3dgirl'


instance_dir=$SAVED/$dir
selected_dir=$instance_dir/selected_01


sh tagger.sh 0 $SAVED $dir 01 0 0.45

python pyutil/randomName.py ./$selected_dir 1

scp -r $instance_dir 45://home/admin/github/showMan/$instance_dir