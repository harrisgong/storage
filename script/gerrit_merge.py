#!/usr/bin/env python

import sys
import os
import subprocess
import json
import copy

remoteUrl = 'ssh://lap.lge.com:29475/' #defualt url
branch = 'msm8960_ics_release' #default branch
dict_branch_list = { "msm8960_ics_release" : "1" , "capp_ics" : "2" , "LG_apps_master" : "3", "LG_apps_release" : "4" }
applyBranchList = [] # 1 : msm8960_ics_release / 2 : capp_ics / 3 : LG_apps_release / 4 : LG_apps_master
option = []
commit_num = 0

def printRED(err):
    print "\033[31m" + err + "\033[0m"

def printCYAN(des):
    print "\033[36m" + des + "\033[0m"

def printBG_WT(des):
    print "\033[7m" + des + "\033[0m"

def printYEL(des):
	print "\033[33m" + des + "\033[0m"


def make_qcmd(option, branch) :
    result = []
    lap_qcmd = ["ssh", "-p", "29475", "lap.lge.com", "gerrit", \
        "query", "--format=JSON", "--current-patch-set"]
    Apps_qcmd = ["ssh", "-p", "29427", "165.243.137.64", "gerrit", \
        "query", "--format=JSON", "--current-patch-set"]

    add_git_pull_qcmd = ["status:open", "label:CodeReview+2", "NOT label:CodeReview-1", \
                         "NOT label:CodeReview-2", "NOT label:Verified-1", \
                         "branch:" + branch
                        ]

    add_git_cpick_qcmd = ["branch:" + branch] # must add option, commit id
    
    if option[0] == 'cpick' or option[0] == '2':
        if branch == 'LG_apps_release' or branch == 'LG_apps_master' :
            result = Apps_qcmd + add_git_cpick_qcmd
        elif branch == 'msm8960_ics_release' or branch == 'capp_ics' :
            result = lap_qcmd + add_git_cpick_qcmd
    else : # git-pull or want to know merge lists
        if branch == 'LG_apps_release' or branch == 'LG_apps_master' :
            result = Apps_qcmd + add_git_pull_qcmd
        elif branch == 'msm8960_ics_release' or branch == 'capp_ics' :
            result = lap_qcmd + add_git_pull_qcmd

    if option[0] == 'include' or option[0] == '4':
        result.append("project:" + option[1])
    if option[0] == 'user' or option[0] == '6':
        result.append("owner:" + option[1])
    if option[0] == 'exclude' or option[0] == '3':
        exclude_proj = copy.deepcopy(option[1:])
        while exclude_proj :
            result.append("NOT project:" + exclude_proj.pop())
    return result

def getChanges(option, branch):
    printYEL("------------------------------------------------")
    printYEL("        BRANCH: " + branch)
    printYEL("------------------------------------------------")
    
    changes = []
    if option[0] == '2' or option[0] == 'cpick' :
        try :
            f = file("ch-pick.txt", 'r')
        except:
            printRED("[Exception] -ch-pick.txt- FILE is not exist!")
            exit()
    else:
        pass

    qcmd = make_qcmd(option, branch)

    if option[0] != '2' :
        p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)
        commit = "dummy"
    else : # case : cherry-pick
        pass

    i = 0
    remainBranch = 4
    while 1:
        if option[0] == '2' or option[0] == 'cpick' : # git cherry-pick
            if remainBranch == 4 :
                commit = f.readline()
                printCYAN("commit ================= " + commit )
            else :
                pass
            qcmd = make_qcmd(option, branch)
            qcmd.append("commit:" + commit)

            p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)

        context = p.stdout.readline()
        #print ""
        #printCYAN("context == " + str(context) )
        if ( option[0] == '2' or option[0] == 'cpick' ) and \
             str(context).find("project") == -1 :
            if remainBranch != 0 :
                if branch == 'msm8960_ics_release':
                    branch = 'capp_ics'
                    remainBranch = remainBranch - 1
                elif branch == 'capp_ics' :
                    branch = 'LG_apps_master'
                    remainBranch = remainBranch - 1
                elif branch == 'LG_apps_master' :
                    branch = 'LG_apps_release'
                    remainBranch = remainBranch - 1
                elif branch == 'LG_apps_release' :
                    branch = 'msm8960_ics_release'
                    remainBranch = remainBranch - 1
            else :
                printRED("   ==========================================  ")
                printRED("   [Error]  There is not a COMMIT !!  ")
                printRED("   ==========================================  ")
                exit()
        else :
            #printCYAN( " FIND IT ! " )
            remainBranch = 4
            #applyBranchList.append(dict_branch_list[branch])
            applyBranchList.append(branch)

        if not context or not commit:
            break
        #temp = json.loads(context)
        if remainBranch == 4 :
            changes.append(json.loads(context))
        #printYEL("changes ==== " + str(len(changes)))

    if option[0] != '2' and option[0] != 'cpick':
        changes.pop(len(changes)-1) # <- OK list : cpick, include, 
        # to keep timeline in gerrit
        changes.reverse()
        applyBranchList.reverse()
    else :
        pass

    return changes

def printListToFile(filename, changes):
    f = file(filename, 'w')
    for change in changes:
        f.writelines(change[u'currentPatchSet'][u'revision']  + "\n")
        
def printProjectRefList(changes):
    #print "changes ========= " + str(changes)
    print ""
    printCYAN("=== BEGIN: Changes ready to be merged ")
    for change in changes:
        print change[u'project'] + " " + change[u'currentPatchSet'][u'ref']
    printCYAN("=== END: Changes ready to be merged ")
    print "commits will be applied : ", len(changes)
    print ""
    global commit_num
    commit_num = len(changes)
    
def make_url(branch, index) :
    result = ""
    #print "applyBranch == " + str(applyBranchList)
    branch = applyBranchList[index]
    if branch == "LG_apps_release" or branch == "LG_apps_master" :
        result = 'ssh://165.243.137.64:29427/'
    else :
        result = 'ssh://lap.lge.com:29475/'

    return result

def applyPatchSet(changes, option, project_name, branch):
    repoRoot = os.getcwd()
    listPullSet = []
    #printCYAN("changes = " + str(changes))
    i = 0
    for change in changes:
        cmdRepoList = ["repo", "list", str(change[u'project'])]
        #printCYAN("change[project] = " + str(change[u'project']))
        pRepoList = subprocess.Popen(cmdRepoList, shell=None, stdout=subprocess.PIPE)
        repoListResult = pRepoList.stdout.readline()
        #printCYAN("RepoList = " + repoListResult)
        os.chdir(repoListResult.split(' ')[0])

        global commit_num
        print ""
        printYEL("=======  " + "remains ...[" + str(commit_num) + "]  =======")
        commit_num = commit_num - 1
        remoteUrl = make_url(branch, i)
        cmdGitPull = ["git", "pull", remoteUrl + change[u'project'], change[u'currentPatchSet'][u'ref']]
        cmdGitFetch = ["git", "fetch", remoteUrl + change[u'project'], change[u'currentPatchSet'][u'ref']]
        cmdGitCherryPick = ["git", "cherry-pick", "FETCH_HEAD"]
        
        if option[0] != '2' and option[0] != 'cpick' :
            print "\033[36m"
            pGitCmd = subprocess.Popen(cmdGitPull, shell=None, stdout=subprocess.PIPE)
            pGitCmd.wait()
            print "\033[0m"
            rstCmd = pGitCmd.stdout.read()
        elif option[0] == '2' or option[0] == 'cpick' :
            print "\033[36m"
            pGitFetch = subprocess.Popen(cmdGitFetch, shell=None, stdout=subprocess.PIPE)
            pGitFetch.wait()
            print "\033[0m"
            pGitCmd = subprocess.Popen(cmdGitCherryPick, shell=None, stderr=subprocess.PIPE)
            pGitCmd.wait()
            rstCmd = pGitCmd.stderr.read()
        
        if checkApplyError(rstCmd, change) == -1:
            #printCYAN("CheckApplyError method !!! ----IF")
            cmdGitReset = ["git", "reset", "--hard", "HEAD"]
            pGitCmd = subprocess.Popen(cmdGitReset, shell=None, stdout=subprocess.PIPE)
            pGitCmd.wait()
            pGitCmd.stdout.read()
            os.chdir(repoRoot)
            f = file('conflict' + project_name + '.txt', 'a+')
            f.writelines(change[u'currentPatchSet'][u'revision']  + "\n")
            f.close
        else:
            #printCYAN("CheckApplyError method !!! ----else")
            os.chdir(repoRoot)
            f = file('applied' + project_name + '.txt', 'a+')
            f.writelines(change[u'currentPatchSet'][u'revision']  + "\n")
            f.close

        os.chdir(repoRoot)
        i = i + 1

def checkApplyError(outString, change):
    errorCase1 = r"Automatic merge failed; fix conflicts and then commit the result."
    errorCase2 = r"hint: after resolving the conflicts, mark the corrected paths"
    errorCase3 = "fatal:"

    if outString.find(errorCase1) != -1 or \
       outString.find(errorCase2) != -1 or \
       outString.find(errorCase3) != -1 :
        # setVerifyFailToGerrit(change)
        printRED("++++++++++++++++++++")
        printRED("=> [Error] : Conflict, please check conflict commit")
        printRED(outString)
        printRED("++++++++++++++++++++")
        #sys.exit(-1)
        return -1
    else:
        return 0

def setVerifyFailToGerrit(change):
    qcmd = ["ssh", "-p", "29475", "lap.lge.com", "gerrit", \
	   "review", "--verified=-1", change[u'currentPatchSet'][u'revision'], \
	   "-m", "'\"Conflict when git pull this commit, please check your change\"'"]
    p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)

    print p.stdout.read()


def getStatus(a_changeID):
    qcmd = ["ssh", "-p", "29475", "lap.lge.com", "gerrit", \
	   "gsql", "--format=JSON", "-c", \
	   "\"select status from changes where change_id=", a_changeID, "\""
           ]
    p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)

    changes = []
    while 1:
	context = p.stdout.readline()
	if not context:
	    break
	changes.append(json.loads(context))
    changes.pop(len(changes)-1)

    if len(changes)!=0:
	return changes[0][u'columns'][u'status']
    else:
        return 0


def getParentChangeID(a_changeID):
    qcmd = ["ssh", "-p", "29475", "lap.lge.com", "gerrit", \
	   "gsql", "--format=JSON", "-c", \
	   "\"select change_id from patch_sets where revision=(select ancestor_revision from patch_set_ancestors where change_id=", a_changeID, ")\""
           ]
    
    p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)

    changes = []
    while 1:
	context = p.stdout.readline()
	if not context:
	    break
	changes.append(json.loads(context))
    changes.pop(len(changes)-1)

    if len(changes)!=0:
	return changes[0][u'columns'][u'change_id']
    else:
        return 0


def isParentAbandoned(a_changeID):
    parentID = getParentChangeID(a_changeID)
    if parentID !=0 :
        status = getStatus(parentID)
        print "  Checking ParentID: " + parentID + ", status: " + str(status)
        if status == "A":
            print "    ! parent status : ABANDONED " + parentID
            return 1
        elif status == "n":
            if isVerifiedReviewed(parentID) == 0:
                print "    ! parent status : NOTREVIEWED " + parentID
                return 1
            return isParentAbandoned(parentID)
        elif status == "M" :
            return 0
    else :
        return 0 


def removeCommitWithAbandonedParent(a_changes):
    changes = []
    #printCYAN( "A-changes === " + str(a_changes))
    for change in a_changes:
        print change[u'project'] + " " + change[u'currentPatchSet'][u'ref']
        if isParentAbandoned(change[u'number']) != 1:
	    changes.append(change)
	    print "  (o) INCLUDE  " + change[u'number']
        else:
	    print "  (x) EXCLUDED " + change[u'number']
	print ""
    return changes


def isVerifiedReviewed(a_changeID):
    qcmd = ["ssh", "-p", "29475", "lap.lge.com", "gerrit", \
	   "query", "--format=JSON", "--current-patch-set", \
	   "status:open", \
	   "label:CodeReview+2", \
	   "NOT label:CodeReview-2", "NOT label:Verified-1", \
	   "change:", a_changeID
	   ]
    p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)
 
    len = 0 
    while 1:
        context = p.stdout.readline()
        if not context:
	    break
	len = len + 1

    if len == 2:
        return 1
    else:
        return 0

def usage():
    print ""
    print ""
    printYEL("gerrit_merge.py USAGE....")
    printCYAN("[0] exit")
    print ""
    printCYAN("[1] git pull all of commits at gerrit")
    printCYAN("    ex) ./gerrit_merge.py all")
    printCYAN("    ex) ./gerrit_merge.py 1")
    print ""
    printCYAN("[2] git cherry-pick at gerrit commits")
    printCYAN("    ex) ./gerrit_merge.py cpick ( it needs cherry-pick List file : ch-pick.txt ) ")
    printCYAN("    ex) ./gerrit_merge.py 2 ( it needs cherry-pick List file : ch-pick.txt ) ")
    printCYAN("        ch-pick.txt -> save commit id line by line ")
    print ""
    printCYAN("[3] exclude proejcts")
    printCYAN("    ex) ./gerrit_merge.py exclude kernel/msm modem_proc")
    printCYAN("    ex) ./gerrit_merge.py 3 kernel/msm modem_proc")
    print ""
    printCYAN("[4] include proejcts")
    printCYAN("    ex) ./gerrit_merge.py include kernel/msm ( must write ONE project ! )")
    printCYAN("    ex) ./gerrit_merge.py 4 kernel/msm ( must write ONE project ! )")
    print ""
    printCYAN("[5] show all of projects of merge-candidate-commit ")
    printCYAN("    ex) ./gerrit_merge.py mglist")
    printCYAN("    ex) ./gerrit_merge.py 5")

def printProjListMergeCandidate(a_changes, option):
    if option[0] == '5' :
        try :
            f = file("tempProjListMergeCandidate.txt", 'w')
        except:
            printRED("[Exception] File does not open!")
    else:
        pass
    changes = []
    for change in a_changes:
        f.write(change[u'project'])
        f.write("\n")
    f.close()

    shellsortcmd = ["sort", "tempProjListMergeCandidate.txt"]
    p = subprocess.Popen(shellsortcmd, shell=None, stdout=subprocess.PIPE)
    rstSortCmd = p.stdout.read()
    printCYAN(rstSortCmd)
    printCYAN("   commit = " + str(len(rstSortCmd.split('\n'))-1))
    f = file("sortedProjListMergeCandidate.txt", 'w')
    f.write(rstSortCmd)
    f.close()

    shelluniqcmd = ["uniq", "sortedProjListMergeCandidate.txt"]
    p = subprocess.Popen(shelluniqcmd, shell=None, stdout=subprocess.PIPE)
    rstUniqCmd = p.stdout.read()
    #printCYAN(rstUniqCmd)
    f = file("ProjListMergeCandidate.txt", 'w')
    f.write(rstUniqCmd)
    f.close()

    removeFileCmd = ["rm", "tempProjListMergeCandidate.txt"]
    p = subprocess.Popen(removeFileCmd, shell=None, stdout=subprocess.PIPE)
    removeFileCmd = ["rm", "sortedProjListMergeCandidate.txt"]
    p = subprocess.Popen(removeFileCmd, shell=None, stdout=subprocess.PIPE)

def runSeq(option, branch) :

    project_name = ""

    # git pull all of commits
    if option[0] == 'all' or option[0] == '1' : 
        project_name = "_All"
        listChange = removeCommitWithAbandonedParent(getChanges(option, branch))
        printProjectRefList(listChange)
        printListToFile('candidate' + project_name + '.txt', listChange)
        applyPatchSet(listChange, option, project_name, branch)

    # git cherry-pick ( using a lot of options -> commitID, changeID, starred )
    elif option[0] == 'cpick' or option[0] == '2' :
        listChange = getChanges(option, branch)
        printProjectRefList(listChange)
        applyPatchSet(listChange, option, project_name, branch)

    # git pull specified ( exclude ) project
    elif option[0] == 'exclude' or option[0] == '3' : 
        project_name = "_exclude"
        printYEL("option : " + option[0] + "  GIT PULL NOT SPECIFIED PROJECT")
        listChange = removeCommitWithAbandonedParent(getChanges(option, branch))
        printProjectRefList(listChange)
        printListToFile('candidate' + project_name + '.txt', listChange)
        applyPatchSet(listChange, option, project_name, branch)

    # git pull specified ( include ) project
    elif option[0] == 'include' or option[0] == '4' : 
        project_name = "_" + option[1].replace("/", "_")
        printYEL("option : " + option[0] + "  GIT PULL SPECIFIED PROJECT")
        listChange = removeCommitWithAbandonedParent(getChanges(option, branch))
        printProjectRefList(listChange)
        printListToFile('candidate' + project_name + '.txt', listChange)
        applyPatchSet(listChange, option, project_name, branch)

    # git pull specified ( include ) project
    elif option[0] == 'user' or option[0] == '6' : 
        project_name = "_user"
        printYEL("option : " + option[0] + "  GIT PULL SPECIFIED USER")
        listChange = removeCommitWithAbandonedParent(getChanges(option, branch))
        printProjectRefList(listChange)
        printListToFile('candidate' + project_name + '.txt', listChange)
        applyPatchSet(listChange, option, project_name, branch)
    # show all of projects ( candidate : MERGE )

    elif option[0] == 'mglist' or option[0] == '5' : 
        printProjListMergeCandidate(getChanges(option, branch), option)
        exit()

    # exit
    elif option[0] == '0' : 
        exit()

def main(argv):
    global branch
    #branch  = ""
    option = argv[0:]

#   print "option = " + str(option)
    if option == [] :
        usage()
        exit()
    elif option[0] != '2' and option[0] != 'cpick' :
        branch = raw_input('[' + branch + '] input branch => ')

    if branch == "" :
        branch = "msm8960_ics_release"
    else :
        pass

    # Run script as option
    runSeq(option, branch)

if __name__ == '__main__':
    main(sys.argv[1:])
