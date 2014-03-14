#!/bin/bash

cd /home/fanlong.jin/e0

#*****  [repo sync]  **********************************************************
repo forall -c git clean -f
repo forall -c git checkout -f
repo sync
repo start lgeyt_e0_rogers_master --all 


#******* [make daily tag] **************************************************** 
#repo forall -c git tag -a lgeyt_e0_canada_master_daily_`date +%Y-%m-%d`  -m "daily_tag"
#repo forall -c git tag -a lgeyt_e0_canada_master_WeeklyVersion_`date +%Y-%m-%d`  -m "weekly_tag_08d"
#repo forall -c git push --tags


#*******[source copy] **************************************************** 
#cd /home/fanlong.jin/e0
#cp -rvf /home/fanlong.jin/e0/script/abs.sh  ./
# ./abs.sh total E0TLS CA clean -j8
#	rsync -avurz --exclude=*.repo --exclude=*.git --exclude=*.gitignore /home/fanlong.jin/e0/android /home/fanlong.jin/Daily_Source/
#	rsync -avurz --exclude=*.repo --exclude=*.git --exclude=*.gitignore /home/fanlong.jin/e0/modem /home/fanlong.jin/Daily_Source/
#	rsync -avurz --exclude=*.repo --exclude=*.git --exclude=*.gitignore /home/fanlong.jin/e0/script /home/fanlong.jin/Daily_Source/
#	sleep 60

	
##******* [compress source code 7za] **************************************************** 
##cd /home/fanlong.jin
##/usr/local/bin/7za a /home/fanlong.jin/E400b_compress_source/E400b_`date +%Y-%m-%d`_reposync.7z ./Daily_Build_Source/


#******* [compress source code gz] **************************************************** 
#cd /home/fanlong.jin/Daily_Source
#tar cvfz 07d_final_android.tar.gz android/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore
#tar cvfz 07d_final_modem.tar.gz modem/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore
#tar cvfz 07d_final_script.tar.gz script/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore


#******** [compile] **************************************************** 
 cd /home/fanlong.jin/e0
 cp -rvf /home/fanlong.jin/e0/script/abs.sh  ./
 ./abs.sh total E0RGS CA clean -j8
 ./abs.sh total E0RGS CA build -j8 
 
 
 #******** [compile  base] **************************************************** 
cd /home/fanlong.jin/e0_base
repo forall -c git clean -f
repo forall -c git checkout -f
repo sync
repo start e0_canada_master --all 
 cd /home/fanlong.jin/e0_base
 cp -rvf /home/fanlong.jin/e0_base/script/abs.sh  ./
 ./abs.sh total E0OPEN EU clean -j8
 ./abs.sh total E0OPEN EU build -j8 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
#mkdir /home/fanlong.jin/e0_compress_source
#cd /home/james.jin/u0_compress_source
#rm *.7z
#cd /home/fanlong.jin/e0
#repo sync
#repo forall -c git clean -f
#repo forall -c git checkout -f
#repo sync
#repo start lgeyt_m3_canada_master --all 
#make daily tag
#repo forall -c git tag -a lgeyt_m3_canada_master_daily_`date +%Y-%m-%d`  -m "daily_tag"
#repo forall -c git push --tags

#cd /home/fanlong.jin/e0
#cp -rvf /home/fanlong.jin/e0/script/abs.sh  ./
# ./abs.sh total E0TLS CA clean -j8
# [source copy]
#	rsync -avurz --exclude=*.repo --exclude=*.git --exclude=*.gitignore /home/fanlong.jin/e0/android /home/fanlong.jin/Daily_Build_Source/
#	rsync -avurz --exclude=*.repo --exclude=*.git --exclude=*.gitignore /home/fanlong.jin/e0/modem /home/fanlong.jin/Daily_Build_Source/
#	rsync -avurz --exclude=*.repo --exclude=*.git --exclude=*.gitignore /home/fanlong.jin/e0/script /home/fanlong.jin/Daily_Build_Source/
#	sleep 60
#tar cvfz E400b_07d_SE1_0217.tar.gz  E0/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore


#cd /home/fanlong.jin/e0
#tar cvfz 07d_SE1_android.tar.gz android/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore
#tar cvfz 07d_SE1_modem.tar.gz modem/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore
#tar cvfz 07d_SE1_script.tar.gz script/ --exclude *.git --exclude *.repo/ --exclude *.manifest/ --exclude *.gitignore
	
#compress source code
#cd /home/fanlong.jin
#/usr/local/bin/7za a /home/fanlong.jin/E400b_compress_source/E400b_`date +%Y-%m-%d`_reposync.7z ./Daily_Build_Source/
#compile
#cd /home/james.jin
#mkdir u0_daily_compile
#rm -rf u0_daily_compile/*
#cp -rf /home/james.jin/u0/* /home/james.jin/u0_daily_compile/
#cd /home/james.jin/u0_daily_compile
#cp -rvf /home/fanlong.jin/e0/script/abs.sh  ./
# cd /home/fanlong.jin/e0
# ./abs.sh total E0TLS CA clean -j8
# ./abs.sh total E0TLS CA user_build -j8 
#build modem
#cd modem/MODEL/build
#source ./buildenv.sh
#perl buildsetup.pl U0OPEN_CN.cfg
#make MULTI=32
#make all
#build android
#cd /home/james.jin/u0_daily_compile
#cd android
#source ./build/envsetup.sh
#choosecombo 1 u0_open_cn userdebug rev_c
#make -j32 2>&1 | tee build.log

