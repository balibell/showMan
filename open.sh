#!/bin/bash

dir=$1
genmeta=$2
num=$3
remove_level=$4


SAVED='saved'
WORK='work'
METADATA='metadata'
CONFIRM_DELETE='confirmDelete.json'
CONFIRM_EDIT_MAP='confirmEditMap.json'

# 判断是否windows 用户
os=$(uname -s)
is_win=0
if [[ $os == "MINGW"* ]] || [[ $os == "MSYS"* ]] || [[ $os == "CYGWIN"* ]]; then
  is_win=1
  echo "当前操作系统为Windows"
else
  echo "当前操作系统不是Windows"
fi

git pull

if [ "$remove_level" = "" ]; then
  remove_level=0
fi

if [ "$num" = "" ]; then
  num=01
fi

if [ -d "$dir" ]; then
  curdirname=$(basename $dir)
  remotepath=/home/admin/github/showMan/$SAVED/${curdirname}/selected_${num}

  if [ "$curdirname" = "selected_${num}" ]; then
    echo "cannot do this, don't use selected_${num} directory as param. maybe you are supposed to use save/xxx?"
    exit 1
  fi

  savedir=./$SAVED/${curdirname}
  savedirnum=$savedir/selected_${num}

  issamedir=0
  if [ -d "$savedirnum" ]; then
    savereal=`realpath $savedirnum`
    dirreal=`realpath $dir/selected_${num}`

    echo "to check two dir is same dir"
    if [ "$savereal" = "$dirreal" ]; then
      issamedir=1
    fi
  fi

  echo "savedirnum: ${savedirnum} and $dir/selected_${num} issamedir: ${issamedir}  curdirname: ${curdirname}"
  

  if [ $issamedir -eq 1 ]; then
    remove_level=1

    ssh 44 << remotessh
    rm -rf $savedirnum/*
    exit
remotessh
    # 上传到远端
    echo "two dir is same, so do scp"
    scp -r $savedirnum 44:/$remotepath
  else
    echo "python pyutil/randomName.py $dir 1"
    python pyutil/randomName.py $dir 1


    if [ -d "$savedirnum" ]; then
      # 如果 saved 目录下目标文件已经存在，我们认为是新添加素材，此时的 remove_level 应该设置为 1
      remove_level=1
      echo "$savedirnum already inited, you can use cmd 'o $curdirname' to open exists dir \n or you can overwrite it as new add. overwrite? [Y/N]:" 
      read -a choice

      if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
        echo "cp -r $dir/* $savedirnum"
        cp -r $dir/* $savedirnum
        # 上传到远端
        scp -r $dir/* 44:/$remotepath

        # 清空导入路径里的图片
        rm -rf $dir/*
      fi
    else
      mkdir -p $savedirnum
      cp -r $dir/* $savedirnum

      ssh 44 << remotessh
      source ~/.zshrc
      node --version
      python --version
      cd /home/admin/github/showMan
      git pull
      mkdir -p $savedirnum
      exit
remotessh
      # 上传到远端
      scp -r $dir/* 44:/$remotepath

      # 清空导入路径里的图片
      rm -rf $dir/*
    fi
  fi

  dir=$curdirname
fi


target_html="./$SAVED/${dir}/${WORK}_${num}_0.html"
# 每次都删除重新生成 html
rm -rf $target_html

metadata="./$SAVED/${dir}/${METADATA}_${num}.json"

if [ $remove_level -gt 0 ]; then
  rm -rf $metadata
fi

scpmetadata=0
oldmd5=
if [ ! -f "$metadata" ]; then
  scpmetadata=1
else
  oldmd5=`md5sum $metadata`
fi

# -f 参数判断 $file 是否存在
echo "sh show_man.sh '1' '$genmeta' $SAVED $dir $num 0"
sh show_man.sh '1' "$genmeta" $SAVED $dir $num 0
if [ $is_win -eq 0 ]; then
  open ./$SAVED/${dir}/${WORK}_${num}_0.html
else
  # windows 下要替换路径
  dirprefix=`pwd | sed 's/\/c/C:\//'`
  echo "start /$dirprefix/$SAVED/${dir}/${WORK}_${num}_0.html"
  start /$dirprefix/$SAVED/${dir}/${WORK}_${num}_0.html
fi

# 创建训练目录
echo "sh training/inst.sh $dir"
sh training/inst.sh $dir
echo "===================training dir created to check it training/$dir"






exit



# 定义信号处理函数
function handle_interrupt {
  # 在这里添加你的自定义操作代码
  # 检查 crop 文件变化
  for item in `cat confirmCropped.txt`; do 
    cropfile="$SAVED/${dir}/selected_${num}/$item"
    echo "scp $cropfile 44:/home/admin/github/showMan/$SAVED/${dir}/selected_${num}/$item"
    scp $cropfile 44:/home/admin/github/showMan/$SAVED/${dir}/selected_${num}/$item
    echo $item;
  done;
  cat /dev/null > confirmCropped.txt

  sh show_man.sh '1' "$genmeta" $SAVED $dir $num 0

  git add $CONFIRM_DELETE
  git add $CONFIRM_EDIT_MAP
  git add $SAVED/${dir}
  git add confirmCropped.txt
  git commit -m"confirm edit or delete changed"
  git pull
  git push



  newmd5=`md5sum $metadata`

  if [ "$oldmd5" != "$newmd5" ]; then
    # 如果 metadata 文本内容发生变化
    echo '!!!!!!!!!!!!!! metadata changed !!!!!!!!!!!!!!!!'
    scpmetadata=1
  fi


  if [ $scpmetadata -eq 1 ]; then
    sh show_man.sh '1' "$genmeta" $SAVED $dir $num 0 remoteonly
  fi
}




# 监听剪贴板变化
if [ $is_win -eq 0 ]; then
  python pyutil/watchClipboardMac.py

  handle_interrupt
else
  # 设置信号处理函数
  trap handle_interrupt SIGINT
  python pyutil/watchClipboardWin32.py
fi
