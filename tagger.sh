#!/bin/bash

doCopy=$1
typedir=$2
dir=$3
num=$4
level=$5
threshold=$6
remote=$7

if [ "$level" = "" ]; then
  level=0
fi

if [ "$threshold" = "" ]; then
  threshold=0.45
fi


current_path=`pwd`
imgdir="$current_path/$typedir/$dir/selected_$num"
echo "imgdir in tagger is ${imgdir}"

doTagger() {
  echo "in doTagger doCopy:[$doCopy] and level:[$level]"
  if [ $doCopy -eq 1 ] && [ $level -gt 0 ]; then
    # 拷贝按 level
    newdir="${imgdir}_lv${level}"
    rm -rf $newdir
    cp -r $imgdir $newdir
    imgdir=$newdir
  fi
  # 给目录下的图片打上tag，生成对应的txt 文件
  echo "python tagger/tagger.py -da="${imgdir}" -th=$threshold -lv=$level -ig"
  python tagger/tagger.py -da="${imgdir}" -th=$threshold -lv=$level -ig
}


if [ "$remote" != "remoteonly" ]; then
  doTagger
fi




if [ "$remote" = "remoteonly" ] || [ "$remote" = "all" ]; then
echo 'do remote action'

ssh 44 << remotessh
source ~/.zshrc
node --version
python --version
cd /home/admin/github/showMan
git pull
sh tagger.sh $doCopy $typedir $dir $num $level $threshold
exit
remotessh
echo "remote 44 done!"
fi

