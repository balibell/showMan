#!/bin/bash


ASIANBOY='asianboy'
ASIANGIRL='asiangirl'
SELECTED='selected'



ASIANBOY_01=${ASIANBOY}/${SELECTED}_01
ASIANBOY_02=${ASIANBOY}/${SELECTED}_02

ASIANGIRL_01=${ASIANGIRL}/${SELECTED}_01
ASIANGIRL_80=${ASIANGIRL}/${SELECTED}_80
ASIANGIRL_90=${ASIANGIRL}/${SELECTED}_90



# stat saled
echo '-------------------------'
echo 'saled stat:'
echo "${ASIANBOY_01}   "
ls -l ./saled/${ASIANBOY_01} | wc -l
echo "${ASIANBOY_02}_lv9   "
ls -l ./saled/${ASIANBOY_02}_lv9 | wc -l

echo "${ASIANGIRL_01}   "
ls -l ./saled/${ASIANGIRL_01} | wc -l
echo "${ASIANGIRL_80}   "
ls -l ./saled/${ASIANGIRL_80} | wc -l
echo "${ASIANGIRL_90}   "
ls -l ./saled/${ASIANGIRL_90} | wc -l
echo "${ASIANGIRL_01}_lv9   "
ls -l ./saled/${ASIANGIRL_01}_lv9 | wc -l
echo "${ASIANGIRL_80}_lv9   "
ls -l ./saled/${ASIANGIRL_80}_lv9 | wc -l
echo "${ASIANGIRL_90}_lv9   "
ls -l ./saled/${ASIANGIRL_90}_lv9 | wc -l


echo '-------------------------'
echo 'saved stat:'
echo "${ASIANBOY_01}   "
ls -l ./saved/${ASIANBOY}/${SELECTED}_01 | wc -l
echo "${ASIANBOY_02}   "
ls -l ./saved/${ASIANBOY}/${SELECTED}_02 | wc -l
echo "${ASIANGIRL_01}   "
ls -l ./saved/${ASIANGIRL}/${SELECTED}_01 | wc -l
echo "${ASIANGIRL_80}   "
ls -l ./saved/${ASIANGIRL}/${SELECTED}_80 | wc -l
echo "${ASIANGIRL_90}   "
ls -l ./saved/${ASIANGIRL}/${SELECTED}_90 | wc -l


# 找出目录下空白的txt文件
find ./ -type f -name "*.txt" -empty