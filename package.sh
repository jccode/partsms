#!/usr/bin/sh

exclude_list=("env" ".*" "apiclient" "TODO" "API.org")

exclude=''
for i in ${exclude_list[@]}; do
    exclude+=" --exclude "$i
done


# create package
cd ..
rm -rf partsms.tar.bz2
echo "tar cjvf partsms.tar.bz2 partsms/ $exclude"
tar cjvf partsms.tar.bz2 partsms/ $exclude

