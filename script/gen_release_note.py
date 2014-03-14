#!/usr/bin/env python

import sys, os, subprocess

def getChangeLogs(tag1, tag2):
    scope = tag1 + ".." + tag2
    cmdFullLog = ["repo", "forall", "-pc", \
		  "git", "log", "--no-merges", \
                  "--format=TITLE_HEADER%s - %ae %h%n%b", \
		  scope]
    p = subprocess.Popen(cmdFullLog, shell=None, stdout=subprocess.PIPE)
    p.wait()
    fullContents = []
    fullTitle = "Full changelog"
    fullContents.append("\n")
    fullContents.append(fullTitle)
    fullContents.append(getUnderBar(fullTitle, "-"))
    shortContents = []
    shortTitle = "Short changelog"
    shortContents.append("\n")
    shortContents.append(shortTitle)
    shortContents.append(getUnderBar(shortTitle, "-"))
    countOfCommit = 0
    while 1:
        context = p.stdout.readline()
        if not context:
	    break
	elif context[0:12] == "TITLE_HEADER":
	    fullContents.append("- " + context[12:].strip() + "\n")
	    shortContents.append("- " + context[12:].strip() + "\n")
	    countOfCommit = countOfCommit + 1
	elif context[0:8] == "project ":
	    fullContents.append("\n." + context.strip() + "\n")
	    shortContents.append("\n." + context.strip() + "\n")
	else:
	    fullContents.append("  " + context.strip())
    return shortContents, fullContents, countOfCommit

def getMD5SUM():
    cmd1 = ['repo', 'forall', '-c', 'git', 'log', '-1', '--pretty=format:%h']
    cmd2 = ['md5sum']
    Pcmd1 = subprocess.Popen(cmd1, shell=None, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    Pcmd2= subprocess.Popen(cmd2, shell=None, stdin=Pcmd1.stdout, stdout=subprocess.PIPE)
    out = Pcmd2.communicate()[0]
    return out.split()[0]

def getBasicInfo(tag, countOfCommit):
    contents = []
    title = "Release notes for " + tag
    contents.append(title)
    contents.append(getUnderBar(title, "="))
    contents.append("\n")
    titleBasicInfo = "Basic information"
    contents.append(titleBasicInfo)
    contents.append(getUnderBar(titleBasicInfo, "-"))
    contents.append(tag + " is now available:")
    contents.append("\n")
    contents.append("* Current version : " + tag)
    contents.append("* Android version : " + getCurrentAndroidVersion(tag))
    contents.append("* Count of commit : " + str(countOfCommit))
    contents.append("* Value of MD5SUM : " + getMD5SUM())
    return contents


def getCurrentAndroidVersion(tag):
    currentDir = os.getcwd()
    os.chdir("android/frameworks/base")
    cmdAndroidVersion = ["git", "describe", tag, "--abbrev=0", \
		     "--match", "android-*"]
    p = subprocess.Popen(cmdAndroidVersion, shell=None,\
	                 stdout=subprocess.PIPE)
    p.wait()
    os.chdir(currentDir)
    return p.stdout.readline().strip()


def getUnderBar(content, barType):
    underBar = ""
    for i in range(len(content)):
	underBar = underBar + barType
    print "writing " + content + "..."
    return underBar


def composeReleaseNote(tag1, tag2):
    contents = []
    shortChangeLog, fullChangeLog, countOfCommit = getChangeLogs(tag1, tag2)
    contents.extend(getBasicInfo(tag2, countOfCommit))
    contents.extend(shortChangeLog)
    contents.extend(fullChangeLog)
    fileName = "ReleaseNotes-" + tag2 + ".txt"
    writeFile(contents, fileName)
    cmdAsciiDoc = ["asciidoc", "-a", "toc", fileName]
    p = subprocess.Popen(cmdAsciiDoc, shell=None, stdout=subprocess.PIPE)
    p.wait()
    os.remove(fileName)


def writeFile(contentsList, fileName):
    f = open(fileName, 'w')
    for content in contentsList:
        f.write("%s \n" % content)
    f.close()


def main (argv) :
    tag1 = argv[0]
    tag2 = argv[1]
    composeReleaseNote(tag1, tag2)


if __name__ == '__main__':
    main(sys.argv[1:])