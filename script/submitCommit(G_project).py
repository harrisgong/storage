.#!/usr/bin/python
import subprocess

def readCommitId():
    commit_id_list = []
    mergedCommitIdFile = 'mergedCommits.txt'
        
    f = open(mergedCommitIdFile, 'r')
    
    while True:
        context = f.readline()
        context = context.replace('\n','')
        if not context:
            break
        commit_id_list.append(context)
        print 'CommitID: ' + context
   
    f.close()
   
    return commit_id_list

def subCommitId(commit_id_list):
    qcmd = []
    for commit_id in commit_id_list:
        qcmd = ["ssh", "-p", "29447", "gtdr.integrator@165.243.137.64", "gerrit", \
	   "approve", "--verified=+1", "--code-review=+2", \
	   "--submit",commit_id]#ssh -p 29447 gtdr.integrator@165.243.137.64 gerrit approve --verified=+1 --code-review=+2 --submit COMMIT_ID
        p = subprocess.Popen(qcmd, shell=None, stdout=subprocess.PIPE)
        print p.stdout.read() 

def main():
    subCommitId(readCommitId())
    print 'Submit Success ~.~'

if __name__ == '__main__':
    main()
