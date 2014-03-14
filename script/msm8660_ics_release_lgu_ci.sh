#!/bin/bash
function save_error_log
{
    echo "save build error log.."
    cp $BUILDDIR/android/out/build.log $LOGDIR    
    grep -n -e ' expected' -e cannot -e ' Stop.' -e ' Stop ' -e ' error:' -e ' error' -e ' Error ' -e 'errors ' -e ' undefined ' $BUILDDIR/android/out/build.log | grep -v -e 'warning:' -e 'Warning:' -e 'note: ' > $LOGDIR/build_error.log
}

function is_build_complete
{
    SUCCESS1=$(ls $WORKDIR/android/out/target/product/$PRODUCT_NAME/system.img 2>/dev/null | wc -l)
    SUCCESS2=$(ls $WORKDIR/$MODEM_PATH/modem_proc/build/ms/bin/PIL_IMAGES/MSM_FATIMAGE_AAABQNSZ/NON-HLOS.bin 2>/dev/null | wc -l)
    SUCCESS=`expr $SUCCESS1 + $SUCCESS2`
    echo $SUCCESS
}

function is_android_build_complete
{
    SUCCESS1=$(ls $WORKDIR/android/out/target/product/$PRODUCT_NAME/system.img 2>/dev/null | wc -l)
    echo $SUCCESS1
}

function is_modem_build_complete
{
    SUCCESS2=$(ls $WORKDIR/$MODEM_PATH/modem_proc/build/ms/bin/PIL_IMAGES/MSM_FATIMAGE_AAABQNSZ/NON-HLOS.bin 2>/dev/null | wc -l)
    echo $SUCCESS2
}

function do_build_android
{
    echo "build android.."

    cd $BUILDDIR/android
    rm -rf out

    source ./build/envsetup.sh
    choosecombo 1 $PRODUCT_NAME 3
	m -j12
}

function do_build_modem
{
    echo "build modem.."

    cd $BUILDDIR/$MODEM_PATH
    ./clean_all.sh
    ./build_$PRODUCT_NAME.sh
    ./build_$PRODUCT_NAME.sh
}

function do_teambuild_submit
{
    echo "do_teambuild_submit"
    cd $BUILDDIR
	for name in $(cat list.txt);do ssh -p 29475 165.186.89.36 gerrit review --verified=+1 --submit $name; done
}

function make_message
{
	if [ $(echo $RECEIVER | wc -w) -eq 0 ]; then
		echo "unexpected result.. report to manager.."
		##defulat revceiver
		RECEIVER='sean.cho@lge.com lgesettings@gmail.com'
	fi

    echo "make email message.."
	
    MESSAGEFILE=$WORKDIR/notice.txt
        if [ $(is_build_complete) -eq 2 ]; then
            echo "subject: [${MODEL_NAME}/Auto-BUILD Success]" > $MESSAGEFILE
            echo "MIME-Version: 1.0" >> $MESSAGEFILE
            echo "Content-Type: text/html" >> $MESSAGEFILE
            echo "<html><head><style>Body {font-size:10pt;}P, TR, TD, DIV {font-size:10pt;} P{margin-top:1; margin-bottom:1;}</style></head>" >> $MESSAGEFILE
            echo "<body bgcolor=\"white\" text=\"black\" link=\"blue\" vlink=\"purple\" alink=\"red\">" >> $MESSAGEFILE
            echo "<li><b>Built from : </b></li><font color=\"red\"><b>${WORK_BRANCH}</b></font><br />" >> $MESSAGEFILE
            echo "<li><b>Result : Build success!!! </b></li><br />" >> $MESSAGEFILE
            echo "<blockquote><pre>" >> $MESSAGEFILE
            echo "<font color=\"blue\"><li><b>Gerrit compile test list: </b></li></font><b>" >> $MESSAGEFILE
			cat $WORKDIR/listforhuman.txt >> $MESSAGEFILE
			echo "</b><br />" >> $MESSAGEFILE
            echo "<font color=\"red\"><li><b>Build Error Message : </b></li></font> <b>None</b><br /><br />" >> $MESSAGEFILE
            echo "</blockquote></pre><br />" >> $MESSAGEFILE
            echo "</body></html>" >> $MESSAGEFILE
            echo "." >> $MESSAGEFILE
        else
            sed -i "s|commit |<font color=\"red\">+--------------------------------------------------------------------------+</font>\ncommit |g" ${LOGDIR}/git_change_history_${CURR_DATE}.log
            sed -i "s|Author: |Author: <font color=\"blue\">|g" ${LOGDIR}/git_change_history_${CURR_DATE}.log
            sed -i "s|Date: |</font>Date: |g" ${LOGDIR}/git_change_history_${CURR_DATE}.log
            echo "subject: [${MODEL_NAME}/Auto-BUILD Error]" > $MESSAGEFILE
            echo "MIME-Version: 1.0" >> $MESSAGEFILE
            echo "Content-Type: text/html" >> $MESSAGEFILE
            echo "<html><head><style>Body {font-size:10pt;}P, TR, TD, DIV {font-size:10pt;} P{margin-top:1; margin-bottom:1;}</style></head>" >> $MESSAGEFILE
            echo "<body bgcolor=\"white\" text=\"black\" link=\"blue\" vlink=\"purple\" alink=\"red\">" >> $MESSAGEFILE
            echo "<li><b>Built from : </b></li><font color=\"red\"><b>${WORK_BRANCH}</b></font><br />" >> $MESSAGEFILE
            echo "<li><b>Result : Build Error!!! </b></li><br />" >> $MESSAGEFILE
            echo "<blockquote><pre>" >> $MESSAGEFILE
            echo "<font color=\"red\"><li><b>Build Error Message : </b></li></font><br /><br />" >> $MESSAGEFILE
            # Error log msg
            cat $LOGDIR/build_error.log >> $MESSAGEFILE
            echo "<br /><br />" >> $MESSAGEFILE
            echo "<font color=\"red\"><li><b>Gerrit test list: </b></li></font><br /><br />" >> $MESSAGEFILE
            cat $WORKDIR/listforhuman.txt >> $MESSAGEFILE
            echo "</blockquote></pre><br />" >> $MESSAGEFILE
            echo "</ul></font></body></html>" >> $MESSAGEFILE
            echo "." >> $MESSAGEFILE
        fi
}

function func_exit_if_error()
{
    set -e
    set -o pipefail
}

function refresh_source()
{
	echo "repo sync.."			
	repo sync -d -j10
	repo forall -c 'git reset --hard remotes/lap/${REPO_RREV}'
	repo start $MASTER_BRANCH --all
}

function is_teambuild_conflict()
{
    if [ -f $TEAMBUILDLOG ] ; then
        echo $(cat $TEAMBUILDLOG | grep "Error: Conflict" | wc -l)
    else
		###no exist
        echo 1
    fi
}

function teambuild_procedure()
{
	export GERRIT_BRANCH=$WORK_BRANCH
	if [ -e $TEAMBUILDLOG ]; then
		rm $TEAMBUILDLOG
	fi

	while [ $(is_teambuild_conflict) -ne 0 ]
	do
	if [ -e $TEAMBUILDLOG ]; then
		rm $TEAMBUILDLOG
	fi
	echo "teambuild excuting"
	python teambuild.py 2>&1 | tee $TEAMBUILDLOG
	done
}

function do_build()
{
	do_build_modem
	echo "modem build complete"
	if [ $(is_modem_build_complete) -eq 1 ]; then
		do_build_android
		echo "android  build complete"
		 if [ $(is_android_build_complete) -eq 1 ]; then
			do_teambuild_submit
			echo "team build submitted"
		 else
			save_error_log
		 fi
	else
			save_error_log
	fi
}

function usage(){
	echo "==================================================================================================="
	echo "usage:>./msm8660_ics_release_lgu_ci.sh 3"
	echo " 선택한 번호 이하의 작업만 진행 됩니다. 예>1입력의 경우 0을 제외한 1,2,3이 실행"
	echo " build가 성공적으로 끝나면 teambuild.py의 결과물인 list.txt의 내용이 자동으로 gerrit에 submit됩니다."
	echo "==================================================================================================="
	echo " 0> repo sync"
	echo " 1> teambuild"
	echo " 2> build"
	echo " 3> send e-mail"
	echo "==================================================================================================="
}

function send_mail()
{
	echo "sending notice e-mail.."
	for MAIL_RCVER in ${RECEIVER}
	do
		#echo ${MAIL_RCVER}	
		/usr/sbin/sendmail -F "${SENDER_NAME}" -f "${SENDER_EMAIL}" -t "${MAIL_RCVER}" < $MESSAGEFILE
	done
}

################################################################################################################
#해당 쉘파일을 프로젝트의 상위 폴더에서 실행하세요.
################################################################################################################
#### phase - init values (edit here)
MASTER_BRANCH=msm8660_ics_release
WORK_BRANCH=msm8660_ics_release_lgu
MODEM_PATH=svlte_modem
LTE_PATH=svlte_lte
PRODUCT_NAME=i_lgu
MODEL_NAME='LG-LU6200'
CURR_DATE=$(date '+%m%d')
WORKDIR=/home/sean.cho/msm8660_ics_release_lgu
BUILDDIR=$WORKDIR
LOGDIR=$WORKDIR/log
SENDER_EMAIL="i-model-integrator@lge.com"
SENDER_NAME="i-model-integrator"
HOMEDIR=/home/sean.cho
TEAMBUILDLOG=$LOGDIR/teambuild.log
RECEIVER='sean.cho@lge.com lgesettings@lge.com'
################################################################################################################
#### phase - ready
ARG=$1
if [ ! "$ARG" ] ; then
    usage
    exit 0
fi
mkdir -p $LOGDIR
cd $WORKDIR
################################################################################################################


	
################################################################################################################
#### phase 0 - init build environment
echo "continuous start.."

if [ $ARG -le 0 ]; then
	echo "refresh_source"
	refresh_source
fi
################################################################################################################



################################################################################################################
#### phase 1 - init build environment & teambuild
if [ $ARG -le 1 ]; then
	echo "teambuild_procedure"
    teambuild_procedure
fi
################################################################################################################



################################################################################################################
#### phase 2 - compiling
if [ $ARG -le 2 ]; then
	echo "do_build"
    do_build
fi
################################################################################################################



################################################################################################################
#### phase 3 - send message
if [ $ARG -le 3 ]; then
	echo "send_mail"
    make_message
	send_mail
fi
################################################################################################################


################################################################################################################
echo "finish.."
exit 0