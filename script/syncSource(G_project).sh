#!/bin/bash
echo "########## repo init & sync ##########"
repo init -u ssh://165.243.137.64:29447/manifest.git -b j1_8064
repo forall -c 'git reset --hard remotes/m/${GERRIT_BRANCH}'
repo sync -j3
repo start $GERRIT_BRANCH --all
echo "########## check md5sum ##########"
repo forall -c git log -1 --pretty=format:%h | md5sum

