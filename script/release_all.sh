#!/bin/sh
# jamin.koo@lge.com Thu 25 Oct 2011
# copy all images from out folder

#
# modified cesc.lee@lge.com 02.13.2012 
# [G] modified dohyun.lee@lge.com 03.21.2012
#
# modified joonsuk.ryu@lge.com 04.17.2012

if test -z "$1"
then
	echo "usage : ./release_image.sh target-name BUILD_TAG_NAME (ex. # ./release_image.sh d1l <TAG_NAME>"
	exit 0
fi

# each SEC_COUNT below is synced with non_HLOS/boot_images/core/storage/tools/jsdcc/partition_load_pt/tot_auto-build.sh
if test -z "$2"
then
    case "$1" in
        "j1a")
        MODEL_NAME=E970
        VERSION_FILE=j1a_ATT_US.mk
        SEC_COUNT=30535680
        ;;
        "j1b")
        MODEL_NAME=                     #TODO: to be defined appropriately
        VERSION_FILE=j1b_BELL_CA.mk
        SEC_COUNT=30535680
        ;;
        "j1u")
        MODEL_NAME=F180L
        VERSION_FILE=j1u_LGU_KR.mk
        SEC_COUNT=30535680
        ;;
        "j1sk")
        MODEL_NAME=F180S
        VERSION_FILE=j1sk_SKT_KR.mk
        SEC_COUNT=30535680
        ;;
        "j1kt")
        MODEL_NAME=F180K
        VERSION_FILE=j1kt_KT_KR.mk
        SEC_COUNT=30535680
        ;;
        "j1v")
        MODEL_NAME=VS940
        VERSION_FILE=j1v_VZW_US.mk
        SEC_COUNT=30535680
        ;;
        "j1d")
        MODEL_NAME=DS1107
        VERSION_FILE=j1d_DCM_JP.mk
        SEC_COUNT=30535680
        ;;
        "j1kd")
        MODEL_NAME=KS1107
        VERSION_FILE=j1kd_KDDI_JP.mk
        SEC_COUNT=30535680
        ;;
        "j1r")
        MODEL_NAME=                          #TODO: to be defined appropriately
        VERSION_FILE=j1r_RGS_CA.mk
        SEC_COUNT=30535680
        ;;
        "j1sp")
        MODEL_NAME=LS970
        VERSION_FILE=j1sp_SPR_US.mk
        SEC_COUNT=30535680
        ;;
        "j1tl")
        MODEL_NAME=                          #TODO: to be defined appropriately
        VERSION_FILE=j1tl_TLS_CA.mk
        SEC_COUNT=30535680
        ;;
        "j1tm")
        MODEL_NAME=E979
        VERSION_FILE=j1tm_TMO_US.mk
        SEC_COUNT=30535680
        ;;
        *)
        echo "Invalid target!"
        ;;
    esac

    mkdir temp
    find android/device/lge/$1 -name ${VERSION_FILE} -exec egrep 'ro.lge.swversion=' {} \; > temp/a.txt
    TAG_NAME=`cat temp/a.txt | awk '{split($1,array,"="); print array[2]}'`
    rm -rf temp
else
    TAG_NAME=$2
fi

# Local Variable Define
TARGET_NAME=$1

echo "TARGET: ${TARGET_NAME}"
NON_HLOS_ROOT=non_HLOS
ANDROID_ROOT=android

IMAGE_RELEASE_OUT=release/${TARGET_NAME}_${MODEL_NAME}/${TAG_NAME} #/IMAGES/${TARGET_NAME}
OBJECT_RELEASE_OUT=${IMAGE_RELEASE_OUT}/OBJECT/${TARGET_NAME}
ANDROID_OUT=${ANDROID_ROOT}/out-${VERSION_FILE%.*}
TARGET_OUT=${ANDROID_OUT}/target/product/${TARGET_NAME}
COMMON_OUT=${ANDROID_OUT}/target/common
FRW_JAR=${COMMON_OUT}/obj/JAVA_LIBRARIES/framework_intermediates

BOOT_IMAGE_OUT=${NON_HLOS_ROOT}/boot_images/build/ms/bin/AAAAANAZ
NON_HLOS_BIN_OUT=${NON_HLOS_ROOT}/common/build
RPM_OUT=${NON_HLOS_ROOT}/rpm_proc/build/ms/bin/AAAAANAAR
TRUSTZONE_IMAGE_OUT=${NON_HLOS_ROOT}/trustzone_images/build/ms/bin/AAAAANAZ

FASTBOOT=${ANDROID_ROOT}/build

if [ ! -d "$IMAGE_RELEASE_OUT" ] ; then
	mkdir -p $IMAGE_RELEASE_OUT

fi

if [ ! -d "$TARGET_OUT" ] ; then
	echo "Android images are not exist.."
	exit 0
fi

if [ ! -d "$BOOT_IMAGE_OUT" ] ; then
	echo "Boot images are not exist.."
	exit 0
fi


if [ ! -d "$NON_HLOS_BIN_OUT" ] ; then
	echo "non_HLOS images are not exist.."
	exit 0
fi
 
if [ ! -d "$RPM_OUT" ] ; then
	echo "RPM image is not exist.."
	exit 0
fi

# copy android images

if [ ! -d "${IMAGE_RELEASE_OUT}/${TAG_NAME}" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/${TAG_NAME}
fi


cp ${TARGET_OUT}/emmc_appsboot.mbn ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/boot.img ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/system.img.ext4 ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/userdata.img.ext4 ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/persist.img.ext4 ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/recovery.img ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/cache.img.ext4 ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/tombstones.img.ext4 ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/format_first.img ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/misc.img ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy Fota bin
cp ${TARGET_OUT}/root/sbin/lge_fota ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${TARGET_OUT}/system/build.prop ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy android installed-files list
cp ${TARGET_OUT}/installed-files.txt ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy rpm image
cp ${RPM_OUT}/rpm.mbn ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy boot images
cp ${BOOT_IMAGE_OUT}/sbl1.mbn ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${BOOT_IMAGE_OUT}/sbl2.mbn ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${BOOT_IMAGE_OUT}/sbl3.mbn ${IMAGE_RELEASE_OUT}/${TAG_NAME}

cp ${TRUSTZONE_IMAGE_OUT}/tz.mbn ${IMAGE_RELEASE_OUT}/${TAG_NAME}
#cp ${BOOT_IMAGE_OUT}/tzapps.mbn ${IMAGE_RELEASE_OUT}/images
#cp ${BOOT_IMAGE_OUT}/tzplayready.mbn ${IMAGE_RELEASE_OUT}/images

# copy nonHLOS images
cp ${NON_HLOS_BIN_OUT}/NON-HLOS.bin ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy xml files
cp ${NON_HLOS_BIN_OUT}/partition-${TARGET_NAME}.xml ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${NON_HLOS_BIN_OUT}/patch0.xml ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${NON_HLOS_BIN_OUT}/rawprogram0.xml ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy batch files
cp ${FASTBOOT}/fastboot_lge.bat ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp Document_tools/tools/release_image/download.bat ${IMAGE_RELEASE_OUT}/${TAG_NAME}

cp ${FASTBOOT}/fastboot.exe ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${NON_HLOS_BIN_OUT}/fastboot_all.py ${IMAGE_RELEASE_OUT}/${TAG_NAME}

# copy bin files for using miniDP
cp ${NON_HLOS_BIN_OUT}/gpt_both0.bin ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${NON_HLOS_BIN_OUT}/gpt_main0.bin ${IMAGE_RELEASE_OUT}/${TAG_NAME}
cp ${NON_HLOS_BIN_OUT}/gpt_backup0.bin ${IMAGE_RELEASE_OUT}/${TAG_NAME}


# add html build_log

if [ ! -d "${IMAGE_RELEASE_OUT}/Log" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Log
fi

cd ./${ANDROID_ROOT}/build/tools
python warn.py ../../build_log.txt > ../../../${IMAGE_RELEASE_OUT}/Log/build_log_android.html
python warn.py ../../../non_HLOS/build.log > ../../../${IMAGE_RELEASE_OUT}/Log/build_log_modem.html
cd ../../../



# make tot file
#cd ${NON_HLOS_ROOT}
#./build_target.sh -t $TARGET_NAME # currently not working is this.
cd ${IMAGE_RELEASE_OUT}/${TAG_NAME}
python ../../../../non_HLOS/boot_images/core/storage/tools/jsdcc/partition_load_pt/ptool.py -x partition-${TARGET_NAME}.xml
python ../../../../non_HLOS/boot_images/core/storage/tools/jsdcc/partition_load_pt/checksparse.py -i rawprogram0.xml
python ../../../../non_HLOS/boot_images/core/storage/tools/jsdcc/partition_load_pt/makeLGTot.py -r rawprogram0.xml -d ${SEC_COUNT} -o ${TAG_NAME}.tot

rm -rf system.img_*.ext4
rm -rf tombstones.img_*.ext4
rm -rf cache.img_*.ext4
rm -rf persist.img_*.ext4





cd ../../../..

# add txt build_log
if [ ! -d "${IMAGE_RELEASE_OUT}/Log/MDM" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Log/MDM
fi
if [ ! -d "${IMAGE_RELEASE_OUT}/Log/non_HLOS" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Log/non_HLOS
fi

cp ./android/build_log.txt ${IMAGE_RELEASE_OUT}/Log/Android-build-log.txt
cp ./non_HLOS/build.log ${IMAGE_RELEASE_OUT}/Log/non_HLOS/non_HLOS-build-log.txt

if [ -f "${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt" ] ; then
	rm ${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt
fi

cp ./MDM9x15/boot_images/build/ms/build-log.txt ${IMAGE_RELEASE_OUT}/Log/MDM/MDM9x15-build-log-boot_images.txt
cp ./MDM9x15/apps_proc/build/ms/build-log.txt ${IMAGE_RELEASE_OUT}/Log/MDM/MDM9x15-build-log-apps_proc.txt
cp ./MDM9x15/modem_proc/build/ms/build-log.txt ${IMAGE_RELEASE_OUT}/Log/MDM/MDM9x15-build-log-modem_proc.txt
cp ./MDM9x15/rpm_proc/build/build.log ${IMAGE_RELEASE_OUT}/Log/MDM/MDM9x15-build-log-rpm_proc.txt
# make one log for MDM log

 
cat ./MDM9x15/apps_proc/build/ms/build-log.txt >> ${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt
cat ./MDM9x15/boot_images/build/ms/build-log.txt >> ${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt
cat ./MDM9x15/modem_proc/build/ms/build-log.txt >> ${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt
cat ./MDM9x15/rpm_proc/build/build.log >> ${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt
cat ./non_HLOS/build.log >> ${IMAGE_RELEASE_OUT}/Log/MDM9x15-build-log.txt

if [ ! -d "${IMAGE_RELEASE_OUT}/Debugging" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Debugging
fi



#Copying MDM Debugging 

if [ ! -d "${IMAGE_RELEASE_OUT}/Debugging/MDM" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Debugging/MDM
fi
if [ ! -d "${IMAGE_RELEASE_OUT}/Debugging/non_HLOS" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
fi
cp -r ./MDM9x15/apps_proc/build/ms/M9x15AFEHRMAZA*.elf ${IMAGE_RELEASE_OUT}/Debugging/MDM
cp -r ./MDM9x15/modem_proc/build/ms/M9x15*.elf ${IMAGE_RELEASE_OUT}/Debugging/MDM
cp -r ./MDM9x15/rpm_proc/build/rpm/9x15/build/RPM.elf ${IMAGE_RELEASE_OUT}/Debugging/MDM
#MDM9x15/modem_proc/build/bsp/modem_proc_img/build/ACEFWMAZ/MODEM_PROC_IMG_ACEFWMAZQ.elf 라는 파일이 맞는지 확인
#cp ${MODEM_PROC_IMG_ELF_OUT}/MODEM_PROC_IMG_ACEFWMAZQ.elf ${IMAGE_RELEASE_OUT}/Debugging/MDM

SBL1_ELF_OUT=non_HLOS/boot_images/core/boot/secboot3/hw/apq8064/sbl1
SBL2_ELF_OUT=non_HLOS/boot_images/core/boot/secboot3/hw/apq8064/sbl2
SBL3_ELF_OUT=non_HLOS/boot_images/core/boot/secboot3/hw/apq8064/sbl3
TZAPPS_ELF_OUT=non_HLOS/trustzone_images/core/bsp/tzapps/build/AAAAANAZ
TZBSP_ELF_OUT=non_HLOS/trustzone_images/core/bsp/tzbsp/build/AAAAANAZ
WCNSS_PROC_ELF_OUT=non_HLOS/wcnss_proc/build/ms
LPASS_PROC_ELF_OUT=non_HLOS/lpass_proc/
MODEM_PROC_IMG_ELF_OUT=MDM9x15/modem_proc/build/bsp/modem_proc_img/build/ACEFWMAZ/

cp -r ./non_HLOS/rpm_proc/build/rpm/8064/build/RPM.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL1_ELF_OUT}/SBL1_AAAAANAZA.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL2_ELF_OUT}/SBL2_AAAAANAZA.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL3_ELF_OUT}/SBL3_AAAAANAZA.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS

cp ${SBL1_ELF_OUT}/SBL1_AAAAANAZA.sym ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL2_ELF_OUT}/SBL2_AAAAANAZA.sym ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL3_ELF_OUT}/SBL3_AAAAANAZA.sym ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS

cp ${SBL1_ELF_OUT}/SBL1_AAAAANAZA.map ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL2_ELF_OUT}/SBL2_AAAAANAZA.map ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp ${SBL3_ELF_OUT}/SBL3_AAAAANAZA.map ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS

#non_HLOS/trustzone_images/core/bsp/tzapps/build/AAAAANAZ/tzapps.elf
cp ${TZAPPS_ELF_OUT}/tzapps.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
#non_HLOS/trustzone_images/core/bsp/tzbsp/build/AAAAANAZ/tz.elf
cp ${TZBSP_ELF_OUT}/tz.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS

#non_HLOS/wcnss_proc/build/ms/8064_RIVA.elf
cp ${WCNSS_PROC_ELF_OUT}/8064_RIVA.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
#non_HLOS/lpass_proc/dsp.elf
cp ${LPASS_PROC_ELF_OUT}/dsp.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp non_HLOS/dsps_proc/build/ms/dsps.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp non_HLOS/dsps_proc/core/bsp/sensorsimg/build/arm7/sensorsimg/arm7/DSPSBLDZ/8064/sensorsimg.elf ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp non_HLOS/dsps_proc/core/bsp/sensorsimg/build/arm7/sensorsimg/arm7/DSPSBLDZ/8064/sensorsimg.map ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS
cp non_HLOS/dsps_proc/core/bsp/sensorsimg/build/arm7/sensorsimg/arm7/DSPSBLDZ/8064/sensorsimg.sym ${IMAGE_RELEASE_OUT}/Debugging/non_HLOS



# Copying symbols debugging
if [ ! -d "${IMAGE_RELEASE_OUT}/Debugging/Android" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Debugging/Android
fi

cp -rf ${FRW_JAR}/classes.jar ${IMAGE_RELEASE_OUT}/Debugging/Android/framework_classes.jar
cd ${FRW_JAR}
tar -zcvf framework_src.tar.gz ./src
cd ../../../../../../../
cp -rf ${FRW_JAR}/framework_src.tar.gz ${IMAGE_RELEASE_OUT}/Debugging/Android/


tar -cvzf ./${IMAGE_RELEASE_OUT}/Debugging/Android/${TARGET_NAME}_symbols_${TAG_NAME}.tar.gz ${TARGET_OUT}/symbols
#mv ${TARGET_NAME}_symbols_${TAG_NAME}.tar.gz 
cp ${TARGET_OUT}/obj/KERNEL_OBJ/vmlinux ./${IMAGE_RELEASE_OUT}/Debugging/Android/
cp ${TARGET_OUT}/obj/KERNEL_OBJ/System.map ./${IMAGE_RELEASE_OUT}/Debugging/Android/
cp ${TARGET_OUT}/obj/EMMC_BOOTLOADER_OBJ/build-${TARGET_NAME}/lk ${IMAGE_RELEASE_OUT}/Debugging/Android/



# Creating Test Folder

if [ ! -d "${IMAGE_RELEASE_OUT}/Test" ] ; then
	mkdir -p ${IMAGE_RELEASE_OUT}/Test
fi

