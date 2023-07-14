#!/bin/bash

dotrim=$1
typedir=$2
dir=$3
num=$4
mtimesort=$5
remote=$6

git pull

# 指定筛选条件，使用 f 参数值
dotrimf=$dotrim
if [ "${dotrim}" = "f" ]; then
  dotrimf="[512,512,0.6,1.1]"
fi

image_path="./${typedir}/${dir}/selected_${num}"
metadata="./${typedir}/${dir}/metadata_${num}.json"

# 清空目录下的隐藏文件
rm -rf $image_path/.*

echo $metadata

# -f 参数判断 $file 是否存在
if [ ! -f "$metadata" ]; then
  echo "sh gen_metadata.sh $typedir $dir $num"
  sh gen_metadata.sh $typedir $dir $num
fi

if [ "$remote" != "remoteonly" ]; then
echo "node showMan.js '$dotrimf' $metadata $image_path 1 1 ./${typedir}/${dir}/work_${num} $mtimesort"
node showMan.js "$dotrimf" $metadata $image_path 1 1 ./${typedir}/${dir}/work_${num} $mtimesort
echo $metadata
  if [ "$remote" = "all" ]; then
    git add "$metadata"
    git commit -m"meta changed"
    git pull
    git push
  fi
echo 'local done!'
fi


if [ "$remote" = "remoteonly" ] || [ "$remote" = "all" ]; then
echo 'do remote action'

ssh 44 << remotessh
source ~/.zshrc
node --version
python --version
cd /home/admin/github/showMan
git pull
sh show_man.sh "$dotrim" $typedir $dir $num $mtimesort
git checkout -- .
exit
remotessh
echo "remote 44 done!"

fi



