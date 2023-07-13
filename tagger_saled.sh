#!/bin/bash

# 只有 saled 目录做，其它的直接使用 tagger.sh 或 tagger.py
SALED='saled'



# remote 取值 all | remoteonly | [empty]
remote=""

# tagger 如果指定 level，且 doCopy = 1 会 copy 整个目录(加_lv9后缀)
# sh tagger.sh 1 saled asianboy 02 9 0.45 all

# sh show_man.sh 'f' saved asiangirl 90 0 remoteonly

sh tagger.sh 1 ${SALED} asiangirl "01" 9 0.45 "${remote}"
sh tagger.sh 1 ${SALED} asiangirl "80" 9 0.45 "${remote}"
sh tagger.sh 1 ${SALED} asiangirl "90" 9 0.45 "${remote}"
