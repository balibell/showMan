#!/usr/bin/env bash

instancename=$1
force=$2

if [ "$1" = "" ]; then
  echo "should input a instance name"
  exit
fi 


instancedir=~/github/showMan/training/${instancename}
if [ "$force" != "" ]; then
  rm -rf $instancedir
fi

if [ ! -d "$instancedir" ]; then
  cp -r ~/github/showMan/training/template $instancedir

  for file in ${instancedir}/*.toml; do 
    echo $file
    sed -i "s/\${INSTANCE}/${instancename}/g" $file
  done


  git add $instancedir
  git commit -m"copy new instance"
  git pull
  git push
fi




