#!/bin/bash
echo "########## android build ##########"

rm -rf ./release
cd android
source build/envsetup.sh
choosecombo 1 $G_ANDROID 3
make -j24 2>&1 | tee android.log

androidBuildResult=${PIPESTATUS[0]}
if [ "${androidBuildResult}" != "0" ]
then 
    echo "###############android build error##################"
    echo "###############checking build error##################"
    grep -n -e ' expected' -e cannot -e ' Stop.' -e ' Stop ' -e ' error:' -e ' error' -e ' Error ' -e 'errors ' -e ' undefined ' -e 'incompatible' -e 'already defined' android.log | grep -v -e 'warning:' -e 'Warning:' -e 'note: ' -e 'cp: ' > build_error.log
    exit ${androidBuildResult}
fi



echo "########## modem build ##########"
cd MDM9x15
./build_target.sh -b all $LOCALE
modemBuildResualt=${PIPESTATUS[0]}

if [ "${modemBuildResult}" != "0" ]
then 
    echo "###############modem build error##################"
    exit ${modemBuildResult}
fi



