#!/usr/bin/python
import sys
import subprocess as p
import os
import time
import datetime

os.system("clear")

modelName="LG"
versionFile=""
countryName=""
carrierName=""
versionName=""


if sys.argv[1] == "j1a":
        modelName="LGE970"	
        versionFile="j1a_ATT_US.mk"
        contryName="US"
        carrierName="ATT"
elif sys.argv[1] == "j1b":
        modelName="LGE970"
        versionFile="j1b_BELL_CA.mk"
        contryName="CA"
        carrierName="BELL"
elif sys.argv[1] == "j1d":
        modelName="LGL07D"
        versionFile="j1d_DCM_JP.mk"
        contryName="JP"
        carrierName="DCM"
elif sys.argv[1] == "j1kd":
        modelName="LGL21"
        versionFile="j1kd_KDDI_JP.mk"
        contryName="JP"
        carrierName="KDDI"
elif sys.argv[1] == "j1kt":
        modelName="LGF180K"
        versionFile="j1kt_KT_KR.mk"
        contryName="KR"
        carrierName="KT"
elif sys.argv[1] == "j1r":
        modelName="LGE971"
        versionFile="j1r_RGS_CA.mk"
        contryName="CA"
        carrierName="RGS"
elif sys.argv[1] == "j1sp":
        modelName="LS970"
        versionFile="j1sp_SPR_US.mk"
        contryName="US"
        carrierName="SPR"
elif sys.argv[1] == "j1tl":
        modelName="LGE970"
        versionFile="j1tl_TLS_CA.mk"
        contryName="CA"
        carrierName="TLS"
elif sys.argv[1] == "j1tm":
        modelName="LGE979"
        versionFile="j1tm_TMO_US.mk"
        contryName="US"
        carrierName="TMO"
elif sys.argv[1] == "j1u":
        modelName="LGF180L"
        versionFile="j1u_LGU_KR.mk"
        contryName="KR"
        carrierName="LGU"
elif sys.argv[1] == "j1sk":
        modelName="F180S"
        versionFile="j1sk_SK_KR.mk"
        contryName="KR"
        carrierName="SK"
elif sys.argv[1] == "j1v":
        modelName="VS940"
        versionFile="j1v_VZW_US.mk"
        contryName="US"
        carrierName="VZW"
else:
	print("invalid target")
	sys.exit(1)


#Getting date 
localTime=time.localtime(time.time())
time = time.asctime(localTime)
timeParsed=time.split()
month=timeParsed[1].upper()
year=timeParsed[4]
if int(timeParsed[2]) < 10 :
	date = "0"+timeParsed[2]
	
else :
	date=timeParsed[2]


versionPath="./android/device/lge/"+sys.argv[1]+"/"

#Git and Repo Command Script
repoClear="repo forall "+versionPath+' -c "git reset HEAD '+versionFile+';git checkout ."'
repoSync="repo sync " + versionPath
gitAdd="repo forall "+ versionPath +" -c 'git add '" + versionFile
gitStatus="repo forall "+ versionPath +" -c 'git status'"
gitCommit="repo forall "+ versionPath +" -c 'git commit'"
gitReset='repo forall '+ versionPath +' -c "git reset --hard HEAD^"'
repoUpload="repo upload " + versionPath

#Clear git.
print "Cleaning git started..."
if os.system(repoClear) != 0 :
	sys.exit("Clear failed")
print "Cleaning git done."



#Repo sync
print "\nrepo sync started..."

if os.system(repoSync) != 0 :
	sys.exit("Repo Sync failed")
print "repo sync done."

os.system("sleep 1")

#Showing SW Version 
print "\n\nLast swversion name : \n"
os.system('grep "ro.lge.swversion=" ' + versionPath +versionFile)
print ""

#Getting new Version and setting path
versionName = raw_input("Please Input SW Version (eg. 07a ): ")
dayVersion = ""



		
# Sprint and ATT have different format.

if sys.argv[1] != "j1sp":      	
      	
      	if sys.argv[1] == "j1a":
      		print "\n\nPleas select Options : "
      		print "    1. AM"
      		print "    2. PM"
      		option = raw_input("    3. none \n\n")
      		if option == "1" :
      			dayVersion = "_1"
      		elif option == "2" :
      			dayVersion = "_2"      			

	swversionName="swversion="+modelName+"-00-V"+versionName+"-"+carrierName+"-"+contryName+"-"+month+"-"+date+"-"+year+dayVersion

else :
	if localTime[1] <10 :
		monthNum= "0" + str(localTime[1])
		
	else :
		monthNum= localTime[1]
	
	swversionName="swversion="+modelName+"Z"+versionName+"_00_"+monthNum+"-"+date+"-"+year

#Updating SW Version Name?
changeConfirmed = raw_input("\nnew swversion name is \n\n\tro.lge."+ swversionName+"\n\ncontinue? (y/Y) :")
if changeConfirmed == "y" or changeConfirmed == "Y" :
	os.system("clear")
else :
	print "\nAborting Changes\n"
	os.system("sleep 1")
	sys.exit(1)
print "\nnew swversion name will be save to " +versionPath + versionFile
print "\n" + swversionName 
#Setting Script
sedCmd='sed -i "s/ro.lge.swversion=.*/ro.lge.'+ swversionName + "/\" " +versionPath +versionFile
print ""
os.system("sleep 1.5")
print ""


#Commiting SW Version Name?
commitConfrim = raw_input("Do you want to Commit changes ? (y/Y)")
if commitConfrim == "y" or commitConfrim == "Y" :
	print "Commiting begins now"
else :
	print "Aborting Changes"
	os.system("sleep 1")
	sys.exit(1)

#execute cmd
os.system(sedCmd)
os.system(gitStatus)
os.system(gitAdd)
os.system(gitStatus)
result = os.system(gitCommit)

if result != 0 : 
	os.system(repoClear)
	sys.exit(1)

result = os.system(repoUpload)

if result != 0 : 
	os.system(gitReset)
	sys.exit(1)


#print p.call('repo upload ./android/device/lge/j1kd',shell=True,stdin=p.PIPE,stdout=p.PIPE)
#print( p.call('cp build.sh por',shell=True,stdin=p.PIPE,stdout=p.PIPE))

