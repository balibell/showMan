#!/bin/bash

instancename=$1
trainer=$2

configfile=
dirname=
if [ "$trainer" = "fine_tune.py" ]; then
  configfile='train_finetune_config.toml'
  dirname="${instancename}_finetune"
elif [ "$trainer" = "train_network.py" ]; then
  configfile='train_network_config.toml'
  dirname="${instancename}_network"
elif [ "$trainer" = "sdxl_train_network.py" ]; then
  configfile='sdxl_train_network_config.toml'
  dirname="sdxl_${instancename}_network"
else
  configfile='train_db_config.toml'
  dirname="${instancename}_db"
fi

instancedir=/home/admin/github/showMan/training/$instancename
configfilepath=$instancedir/$configfile
echo $configfilepath
cat $configfilepath


logdir="/home/admin/github/showMan/training/log/$dirname"
outputdir="/home/admin/github/showMan/training/output/$dirname"
# 创建log目录
mkdir -p $logdir
# 创建输出目录
mkdir -p $outputdir

rm -rf $logdir/*
rm -rf $outputdir/*


# 进入脚本项目
cd /home/admin/github/sd-scripts

echo "accelerate launch --num_cpu_threads_per_process=1 $trainer --config_file=$configfilepath"
accelerate launch --num_cpu_threads_per_process=1 $trainer --config_file=$configfilepath
