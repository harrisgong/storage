#!/usr/bin/python
#-*-coding:utf-8-*-

#changeHistory.py

import string
import sys
import getopt
import re
import os
import os.path
import csv
import time
from xlwt import *
import pymssql
import sgmllib
import MySQLdb


################# Baseline DiffLog #################
def diffBetweenTag(tag1, tag2):
	dothis = """repo forall -p -c 'git log  --pretty=format:"^SHA^&&&|()%h&&&|()%s%n%b&&&|()%an&&&|()%ai&&&|()%cn&&&|()^FILELIST^" --name-status '""" + tag1 + ".." + tag2
	phand = os.popen(dothis)
	lines = phand.read()
	return lines
################# Diff Log to CSV  #################
NEWLN = '\n'
MAX_COMMIT_LINE = 500
mssqlDB = pymssql.connect(host='165.186.89.38', user='swtdif', password='swtdif00', database='SWQIS_ODS')
mssqlCursor = mssqlDB.cursor()
		
#mysqlDB = MySQLdb.connect(host='165.243.137.78', db='reviewdb_test_project',user='gerrit', passwd='!a123456')#, chars    et='utf8')#, use_unicode=True)
#mysqlCursor = mysqlDB.cursor()

class _ProjectHolder:
    projects = []
    def __init__(self, data,  mysqlCursor):
        # Remove Empty Line
	lines = data.split(NEWLN)
	data = ""
	for line in lines:
		if(len(line) != 0):
			data += line + NEWLN
        # Parse Data
	TOKEN = 'project '
	project = ''
	commits = '' 
	lines = data.split(NEWLN)
	for line in lines:
		if(line[:len(TOKEN)] == TOKEN   # start with project token
			or len(line) == 0):          # last line
			if(len(project) != 0):
				projectItem = _Project(project, commits, mysqlCursor) 
				self.projects.append( projectItem )
				if projectItem: del projectItem
#					print "Project : %s \n, Commits : %s" % (project, commits)
			commits = ''    
			project = line[len(TOKEN):]                    
		else:
			commits += line + NEWLN
		
class _Project:
	name = None
	commits = []
	tdInfo = []
	def __init__(self, name, data, mysqlCursor):
		commits = []
		self.commits = commits
		self.name = name
		
		# Parse Project
		items = self.__extract_commit__(data)
		for item in items:
			if(len(item) != 0):
				element = self.__extract_commit_info__(item)
				#print "commit log: %s\nfiles: %s " % (element[0], element[1])
				file_pack = self.__extract_commit_files__(element[1])
				#print "file_packs count: %d" % len(file_packs)
#				for file_pack in file_packs:

				#TD Headlines from Commits
				tdHeadlines = re.findall("TD\d{10}", element[0])

				#If TD Headline exist
				if(len(tdHeadlines) > 0 ):
					for tdHeadline in tdHeadlines:
						self.tdInfo = self.__extract_td_headlines__(tdHeadline)
						commitItem = _Commit(element[0], file_pack, self.tdInfo, mysqlCursor)
						self.commits.append( commitItem )
				else:
					commitItem = _Commit(element[0], file_pack, ["", "", "", "", "", "", ""], mysqlCursor)
					self.commits.append( commitItem )
				
    
	def __extract_commit__(self, data):
		TOKEN = '^SHA^&&&|()'
		commit = ''
		files = []
		commits = data.split(TOKEN)
		return commits

	def __extract_commit_info__(self, data):
		TOKEN = '&&&|()^FILELIST^\n'
		elements = data.split(TOKEN)
		return elements

	def __extract_commit_files__(self, data):
		files = []
		elements = data.split(NEWLN)

		for element in elements: 
			if(len(element) != 0):
				# tab to space and append
				files.append(element.replace('\t', '    ')) 
				quotient, remainder = divmod( len(files), MAX_COMMIT_LINE )
		        # More than 500 files
				if( quotient > 0 and remainder == 0): # do split
					files = []
					files.append("Modified more than 500 files")
					break;
        # remainder pack
		return files


	def __extract_td_headlines__(self, tdHeadline):

		self.tdQuery(tdHeadline)# + ":")
		tdInfo = ['', '', '', '', '', '', '']

		row = mssqlCursor.fetchone()

		# If TDHeadline is incorrent
		if row is None:
			tdInfo[0] = tdHeadline
			tdInfo[1] = "Wrong TD Headline"
			return tdInfo
			
		length = len(row)

		for i in range(length):

			# None Field
			"""
			if row[i] is None:
				continue
			"""
			try:		
				text = row[i].replace("<br>", "\n")
				text = text.replace("<br />", "\n")
				text = text.replace("&nbsp;", "")
				text = re.sub("<[a-z|:/]+[^<>]*>", "", text)
				text = text.replace("&lt;", "<")
				text = text.replace("&gt;", ">")
				text = text.replace("\r\n", "")
				tdInfo[i] = text
				tdInfo[i] = unicode(text, "euc-kr")
				"""	
			except TypeError:
				print "TypeError1"
				"""
			except AttributeError, ae:
				continue

			except UnicodeDecodeError, ue:
				tdInfo[i] = ""

		return tdInfo

	def tdQuery(self, tdHeadline):		
		mssqlCursor.execute(
					"""
					select b.Headline, d.Description, d.RND_Comments, b.QM_Function, b.DEV_Function, b.Closed_in_Version, b.Group_Name
					from td.ODS_ALL_BUG b, td.ODS_ALL_BUG_DESC d
					where b.Project_ID = d.Project_ID
					and b.Defect_ID = d.Defect_ID
					and replace(b.Headline,':','') =  '""" + tdHeadline + "';"

					)

class _Commit:
	id = None
	message = []
	committer = None
	time = None
	author = None
	review = ""
	files = []
	tdInfo = []
	tdHeadline = ""
	rndComments = ""
	desc = ""
		
	def __init__(self, info, files, tdInfo, mysqlCursor):
		# Parse Commit Info
		TOKEN = "&&&|()"
		fields = info.split(TOKEN);
		self.id = fields[0]

#		if( len(tdInfo) > 0):
		self.tdInfo = tdInfo
			
#			self.__extract_tdInfo__(tdInfo)

		self.message = self.__extract_message__(fields[1], mysqlCursor) 
		self.author = fields[2] 
		self.time = fields[3]
		self.committer = fields[4]
		self.files = files
#print "id : %s" % self.id
#        print "message : %s" % self.message
#        print "committer : %s" % self.committer
#        print "time : %s" % self.time
#        print "files : <%s>" % files

	def __extract_tdInfo__(self, data):
		self.tdHeadline = data[0]
		self.rndComments = data[1]
		self.desc = data[2]

	def __extract_message__(self, data, mysqlCursor):
		messages = []
		elements = data.split(NEWLN)
		for element in elements: 
			messages.append(element)

			# Code Review
			row = element.partition(" ")
			if(row[0] == "Change-Id:"):
				self.review = self.__extract_code_review__(row[2], mysqlCursor)

		return messages

	def __extract_code_review__(self, change_key, mysqlCursor):
		query = self.__gerrit_query__(change_key, mysqlCursor)
		data = ""
		"""
		#v1
		for splitQuery in query:
			data += splitQuery[0] + NEWLN

		"""
		for splitQuery in query:
			text = splitQuery[0].split(NEWLN)
			for splitText in text:
				if(len(splitText) > 1):
					data += splitText + NEWLN
		return data

#	code review query
	def __gerrit_query__(self, change_key, mysqlCursor):
		mysqlCursor.execute("select change_messages.message from change_messages, changes where changes.change_key = '" + change_key + "' and changes.change_id = change_messages.change_id;")
		return mysqlCursor.fetchall()

def diffLog2csv(data, ipport):
	ip_port = ipport.split(":")

	ip = ip_port[0]
	port = ip_port[1]

	#access mapping database for find the git project
	mysqlDB = MySQLdb.connect(host=ip, db='tag_compare_mapping_db' ,user='tag_compare')
	mysqlCursor = mysqlDB.cursor()

	mysqlCursor.execute(
					"select db_name from mapping_table where port='" + port + "';")

	database = mysqlCursor.fetchone()

#	connect to mysql server 
	mysqlDB = MySQLdb.connect(host=ip, db=database[0] ,user='tag_compare')
	mysqlCursor = mysqlDB.cursor()

	pch = _ProjectHolder(data, mysqlCursor)

	mysqlCursor.close()
	mysqlDB.close()

	projects = pch.projects
	if len(projects) < 1:
		return ''
	csvData = "Git Name|Commit ID|Commit Time|Committer|Author|Commit Message|Commit Files(A:Added, M:Modified, D:Deleted)|Code Review|TDHeadLine|Description|R&D Comments|QM Function|DEV Function|Closed in Version|Group Name" + NEWLN
	
	sepChar = chr(1)
	
	
	for project in projects:
		projName = project.name
		projCommits = project.commits

		for commit in projCommits:
			commitId = commit.id

			tdHeadline = commit.tdInfo[0].encode("utf-8")

			Description = sepChar
			try:
				Description += commit.tdInfo[1].encode("utf-8")
			except UnicodeDecodeError:
				Description += commit.tdInfo[1]

			Description += sepChar
			
			rndComments = sepChar
			try:
				rndComments += commit.tdInfo[2].encode("utf-8")
			except UnicodeDecodeError:
				rndComments += commit.tdInfo[2]

			rndComments += sepChar

			qmFunction = commit.tdInfo[3].encode("utf-8")
			devFunction = commit.tdInfo[4].encode("utf-8")
			closedInVersion = commit.tdInfo[5].encode("utf-8")
			groupName = commit.tdInfo[6].encode("utf-8")

			commitMessage = sepChar
			codeReview = sepChar
			for messageItem in commit.message:
				if( len(commitMessage) > 1 ):
					commitMessage += NEWLN
				commitMessage += messageItem
			commitMessage += sepChar

			codeReview += commit.review
			codeReview += sepChar		
			committer = commit.committer
			author = commit.author
			commitTime = commit.time[:-5]
			files = sepChar
			for fileItem in commit.files:
				if( len(files) > 1 ):
					files += NEWLN
				files += fileItem
			files += sepChar   
			csvData += "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (projName, commitId, commitTime, committer, author,  commitMessage, files, codeReview, tdHeadline, Description, rndComments, qmFunction, devFunction, closedInVersion, groupName) + NEWLN
	return csvData

#################    CSV to XLS    #################

style = XFStyle()
def openExcelSheet(outputFileName):
	""" Opens a reference to an Excel WorkBook and Worksheet objects """
	workbook = Workbook(encoding='utf-8')
	worksheet = workbook.add_sheet("Sheet 1")
	worksheet.col(0).width = 8000
	worksheet.col(1).width = 3000
	worksheet.col(2).width = 6000
	worksheet.col(3).width = 6000
	worksheet.col(4).width = 6000
	worksheet.col(5).width = 15000
	worksheet.col(6).width = 15000
	worksheet.col(7).width = 15000
	worksheet.col(8).width = 6000
	worksheet.col(9).width = 15000
	worksheet.col(10).width = 15000
	worksheet.col(11).width = 6000
	worksheet.col(12).width = 6000
	worksheet.col(13).width = 10000
	worksheet.col(14).width = 6000
	return workbook, worksheet

def writeExcelHeader(worksheet, titleCols, firstTag, secondTag):
	""" Write the header line into the worksheet """
	cno = 0
	worksheet.write(0, 0, "Old Tag")
	worksheet.write(0, 1, "New Tag")
	worksheet.write(1, 0, firstTag)
	worksheet.write(1, 1, secondTag)
	for titleCol in titleCols:
		worksheet.write(3, cno, titleCol)
		cno = cno + 1

def writeExcelRow(worksheet, lno, columns):
	""" Write a non-header row into the worksheet """
	cno = 0
	for column in columns:
		#if cno == 4:
#	    print "lnc, cno, column:%s, %s, %s" % (lno, cno, column)
		try:
			worksheet.write(lno, cno, column, style)
			cno = cno + 1
		except UnicodeDecodeError:
			worksheet.write(lno, cno, " ")
			cno = cno + 1
			
def closeExcelSheet(workbook, outputFileName):
	""" Saves the in-memory WorkBook object into the specified file """
	workbook.save(outputFileName)
		
def getDefaultOutputFileName(inputFileName):
	""" Returns the name of the default output file based on the value
		of the input file. The default output file is always created in
		the current working directory. This can be overriden using the
		-o or --output option to explicitly specify an output file """
	baseName = os.path.basename(inputFileName)
	rootName = os.path.splitext(baseName)[0]
	return string.join([rootName, "xls"], '.')

def renameOutputFile(outputFileName, fno):
	""" Renames the output file name by appending the current file number
		to it """
	dirName, baseName = os.path.split(outputFileName)
	rootName, extName = os.path.splitext(baseName)
	backupFileBaseName = string.join([string.join([rootName, str(fno)], '-'), extName], '')
	backupFileName = os.path.join(dirName, backupFileBaseName)
	try:
		os.rename(outputFileName, backupFileName)
	except OSError:
		print "Error renaming output file:", outputFileName, "to", backupFileName, "...aborting"
		sys.exit(-1)

def formatStyle(wrap=0):
	# Initialize a style
	# Create a alignment to use with the style
	align = Alignment()
	align.wrap=wrap
	align.vert=align.VERT_TOP
	# Create a font to use with the style
	#font = Font()
	#font.name = 'Times New Roman'
	# Set the style's font & alignmentto this new one you set up
	style.alignment = align
	#style.font = font 
	return style

def csvData2xls(outputFileName, firstTag, secondTag):
	inputFileName = "diffData.csv"
	titlePresent = True
	sepChar = "|"
	linesPerFile = -1
	style = formatStyle(1)
	try:
		inputFile = open(inputFileName, 'r')
	except IOError:
		print "File not found:", inputFileName, "...aborting"
		sys.exit(-1)
	if (outputFileName == ""):
		outputFileName = getDefaultOutputFileName(inputFileName)
	align = Alignment()
		
	workbook, worksheet = openExcelSheet(outputFileName)
	fno = 0
	lno = 3
	titleCols = []
	csv.field_size_limit(1000000000)
	reader = csv.reader(inputFile, delimiter=sepChar, quotechar=chr(1))
	for line in reader:
		if (lno == 3 and titlePresent):
			if (len(titleCols) == 0):
				titleCols = line
			writeExcelHeader(worksheet, titleCols, firstTag, secondTag)
		else:
			writeExcelRow(worksheet, lno, line)
		lno = lno + 1
		if (linesPerFile != -1 and lno >= linesPerFile):
			closeExcelSheet(workbook, outputFileName)
			renameOutputFile(outputFileName, fno)
			fno = fno + 1
			lno = 0
			workbook, worksheet = openExcelSheet(outputFileName)

	inputFile.close()
	closeExcelSheet(workbook, outputFileName)

	if (fno > 0):
		renameOutputFile(outputFileName, fno)

#################       MAIN       #################
def usage():
	""" Display the usage """
	print "Usage: " + sys.argv[0] + " BASELINE_TAG1 BASELINE_TAG2 IP:PORT"
	print "Show change between baseline tag."
	sys.exit(2)

def validateOpts(opts):
	""" Returns option values specified, or the default if none """
	testVal = ""
	for option, argval in opts:
		if (option in ("-t", "--test")):
			outputFileName = argval
		if (option in ("-h", "--help")):
			usage()
	return testVal

def main():
	# fix UnicodeDecodeError: 'ascii' 
	#mm1 = sys.getdefaultencoding()
	#mm2 = sys.stdin.encoding
	#mm3 = sys.stdout.encoding
	#print "python: %s, sys stdin: %s, sys stdout: %s" % (mm1, mm2, mm3)
	#reload(sys)
	#sys.setdefaultencoding('utf-8')
	try:
		opts,args = getopt.getopt(sys.argv[1:], "t:h", ["test", "help"]) 
	except getopt.GetoptError:
		usage()
	if (len(args) != 3):
		usage()
	firstTag = args[0]
	secondTag = args[1]
	ip = args[2]	

	testVal = validateOpts(opts)
	# Make Baseline DiffLog
	print 'Get changes betweens tags...'
	diffLogData = diffBetweenTag(firstTag, secondTag)
	if len(diffLogData) == 0:
		print "Maybe differ data Noe. do opertion with other baseline tag"
		sys.exit(-1)
		
	# Convert DiffLog to CSV Data
	print 'Building spreadsheet...'
	csvData = diffLog2csv(diffLogData, ip)
	if len(csvData) == 0:
		print "Maybe differ data Noe. do opertion with other baseline tag"
		sys.exit(-1)
		
	# Make Temporary CSV FILE
	csvTempFileName = "diffData.csv"
	try:
		wFile = open(csvTempFileName, 'w')
		wFile.write(csvData)
		wFile.close()
	except IOError:
		print "File operation failed:", csvTempFileName, "...aborting"
		sys.exit(-1)
		
	# Convert CSV to Excel
	print 'Saving file...'
	#time setting
	now = time.localtime()
	date = str(now[0])+ string.zfill(now[1], 2) + string.zfill(now[2], 2) + "_" + string.zfill(now[3], 2) + string.zfill(now[4], 2) + string.zfill(now[5], 2)

#	outputFileName = "Tag_Compare_Result.xls"# % (firstTag, secondTag)
	outputFileName = "Tag_Compare_Result_%s.xls" % date
#	outputFileName = "Tag_Compare_Result_%s_%s_%s.xls" % (firstTag.replace('/', '_'), secondTag.replace('/', '_'), date)
	csvData2xls(outputFileName, firstTag, secondTag)
		
	# Remove Temporary CSV FILE
	os.remove(csvTempFileName)
	
	#close
	mssqlCursor.close()
	mssqlDB.close()

		
if __name__ == "__main__":
	main()

