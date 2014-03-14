#!/usr/bin/python			 

import sys
import os
import subprocess
import json

import Queue
import threading
import time
from multiprocessing import Process

remoteUrl = 'ssh://165.243.137.64:29447/'
queue = Queue.Queue()

def getChanges():
    branch = os.environ.get("GERRIT_BRANCH")
    print "------------------------------------"
    print "BRANCH: " + branch
    print "------------------------------------"
    qcmd = ["ssh", "-p", "29447", "165.243.137.64", "gerrit", \
	   "query", "--format=JSON", "--current-patch-set", \
	   "status:open", \
           "label:CodeReview+2", \
           "NOT label:CodeReview-2", "NOT label:Verified-1", \
	   "branch:" + branch
           ]
    changes = []
    p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)
    f = open("mergedCommit.txt", 'w')
    while 1:
	context = p.stdout.readline()
	f.write(p.stdout.readline())
	if not context:
	    break
	changes.append(json.loads(context))
    changes.pop(len(changes)-1)
    # to keep timeline in gerrit
    changes.reverse()
    
    print "getChanges done..."
    return changes

def devidebyProject(a_changes):
    print "devidbyProject"
    
     
    for change in a_changes:
        print change[u'project'] + " " + change[u'currentPatchSet'][u'ref']
    
    print "---------------------------------------------------------"
    changesDic = {}
    for change in a_changes:
        changesDic[change[u'project']] = change[u'currentPatchSet'][u'ref']
    
    changeSet = []
    i=0    
    for v in changesDic:
        subSet = []
        for change in a_changes:
            if v == change[u'project']:
                subSet.append(change)
        i=i+1
        changeSet.append(subSet) 
    for k in changeSet:
        for l in k:
            print l[u'project'] + " " + l[u'currentPatchSet'][u'ref']   
 
    return changeSet
                  
def removeCommitWithAbandonedParent(a_changes):
    changes = []
    for change in a_changes:
        print change[u'project'] + " " + change[u'currentPatchSet'][u'ref']
        if isParentAbandoned(change[u'number']) != 1:
	    changes.append(change)
	    print "  (o) INCLUDE  " + change[u'number']
        else:
	    print "  (x) EXCLUDED " + change[u'number']
	print ""
    return changes

def isParentAbandoned(a_changeID):
    parentID = getParentChangeID(a_changeID)
    if parentID !=0 :
        status = getStatus(parentID)
        print "  Checking ParentID: " + parentID + ", status: " + status
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
        
def getParentChangeID(a_changeID):
    qcmd = ["ssh", "-p", "29447", "165.243.137.64", "gerrit", \
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

def getStatus(a_changeID):
    qcmd = ["ssh", "-p", "29447", "165.243.137.64", "gerrit", \
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
        
def printProjectRefList(changes):
    print ""
    print "=== BEGIN: Changes ready to be merged "
    for change in changes:
        print change[u'project'] + " " + change[u'currentPatchSet'][u'ref']
    print "=== END: Changes ready to be merged "
    print "commits will be applied : ", len(changes)
    print ""

def printListToFile(changes,file_name):
    f = file(file_name, 'w')
    for change in changes:
        f.writelines(change[u'currentPatchSet'][u'revision']  + "\n")

def applyPatchSet(changes):
    repoRoot = os.getcwd()
    cmdGitCheckout = ["git", "checkout", "-b common_gerrit_work"]
    pGitCheckout = subprocess.Popen(cmdGitCheckout, shell=None, stdout=subprocess.PIPE)
    pGitCheckout.wait()
    listPullSet = []
    for change in changes:
        cmdRepoList = ["repo", "list", change[u'project']]
        pRepoList = subprocess.Popen(cmdRepoList, shell=None, stdout=subprocess.PIPE)
        repoListResult = pRepoList.stdout.readline()
        os.chdir(repoListResult.split(' ')[0])
        cmdGitPull = ["git", "pull", remoteUrl + change[u'project'], change[u'currentPatchSet'][u'ref']]
        pGitPull = subprocess.Popen(cmdGitPull, shell=None, stdout=subprocess.PIPE)
        pGitPull.wait()
	checkApplyError(pGitPull.stdout.read(), change)
        os.chdir(repoRoot)
            
def checkApplyError(outString, change):
    errorCase1 = r"Automatic merge failed; fix conflicts and then commit the result."
    if outString.find(errorCase1) != -1:
        setVerifyFailToGerrit(change)
        print >> sys.stderr, "Error: Conflict, please check conflict commit"
        cmdGitReset = ["git", "reset", "--hard"]
        pGitReset = subprocess.Popen(cmdGitReset, shell=None, stdout=subprocess.PIPE)
        pGitReset.wait()

    return 0
    
def setVerifyFailToGerrit(change):
#    qcmd = ["ssh", "-p", "29447", "165.243.137.64", "gerrit", \
#	   "review", "--verified=-1", change[u'currentPatchSet'][u'revision'], \
#	   "-m", "'\"Uploaded source made conflict compared with the latest source.\nafter repo sync, You Must upload it again\"'"]
#    p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)
    print "skip!!!!!!!!!!!!!!!"
#    print p.stdout.read()         

def do_task(listChange,id):
    print 'process id:', os.getpid()
    printProjectRefList(listChange)
    printListToFile(listChange,'Process-'+str(id))
    applyPatchSet(listChange)    
       
def main(argv):
   listChangeSet = devidebyProject(getChanges())
   for subSet in listChangeSet:
       queue.put(subSet)
   queue.put('STOP')
       
#   for i in range(len(listChangeSet)):
   id=0    
   while True:
       subSet = queue.get()
       if subSet == 'STOP': break
       else:
          process=Process(target=do_task, args=(subSet,id))
          id=id+1
          process.start()
#          process.join()
   
   
if __name__ == '__main__':
    main(sys.argv[1:])