import re
import os
import fnmatch
import sys
import csv
import time
import datetime
import salesByStation

verboseOutput = False

class session:
	# This class will hold the results of parsing
	def __init__ (self, directoryName):
		self.pathName = directoryName
		self.version = "Unknown"
		#Operations - by date - by version
		self.operations = {}
		#This stores the operations before the version has been determined
		self.operationsBuffer = {}
		#Events - by date - by version
		self.events = {}
		#This stores the events before the version has been determined
		self.eventsBuffer = {}
		self.stations = {}
		self.isPreparingToLogout = False
		self.submitsLogged = 0
	
	#May want to do something like this at some point.
	def setEmployee(self, employeeNumber):
		return None
	
	#Keep track of the current version
	def setVersion(self, versionNumber):
		self.version = versionNumber
		#If self.operationsBuffer!= {} transfer to an appropriate operation by date by version
		if self.operationsBuffer:
			if(verboseOutput):
				print "Emptying the operations buffer"
			for date in self.operationsBuffer:
				for operation in self.operationsBuffer[date]:
					if date in self.operations:
						if self.version in self.operations[date]:
							if operation in self.operations[date][self.version]:
								self.operations[date][self.version][operation] += self.operationsBuffer[date][operation]
							else: 
								self.operations[date][self.version][operation] = self.operationsBuffer[date][operation]
						else:
							self.operations[date][self.version] = {}
							self.operations[date][self.version][operation] = self.operationsBuffer[date][operation]
					else:
						self.operations[date] = {}
						self.operations[date][self.version] = {}
						self.operations[date][self.version][operation] = self.operationsBuffer[date][operation]
			del self.operationsBuffer
			self.operationsBuffer = {}
		#If self.eventsBuffer!= {} transfer to an appropriate operation by date by version
		if self.eventsBuffer:
			if(verboseOutput):
				print "Emptying the events buffer"
			for date in self.eventsBuffer:
				for operation in self.eventsBuffer[date]:
					if date in self.events:
						if self.version in self.events[date]:
							if operation in self.events[date][self.version]:
								self.events[date][self.version][operation] += self.eventsBuffer[date][operation]
							else: 
								self.events[date][self.version][operation] = self.eventsBuffer[date][operation]
						else:
							self.events[date][self.version] = {}
							self.events[date][self.version][operation] = self.eventsBuffer[date][operation]
					else:
						self.events[date] = {}
						self.events[date][self.version] = {}
						self.events[date][self.version][operation] = self.eventsBuffer[date][operation]
			del self.eventsBuffer
			self.eventsBuffer = {}
	
	def getPathName(self):
		return self.pathName
	
	def addStation(self, date, stationNumber):
		if date in self.stations:
			if not stationNumber in self.stations[date]:
				self.stations[date].append(stationNumber)
		else:
			self.stations[date] = []
			self.stations[date].append(stationNumber)
				
	def getStations(self, date):
		if date in self.stations:
			return self.stations[date]
		else: 
			return None
		
	def resetVersion(self):
		self.version = "Unknown"
		self.isPreparingToLogout = False
	def versionIsKnown(self):
		return (self.version!="Unknown")
		
	def prepareToLogout(self):
		self.isPreparingToLogout = True
		self.submitsLogged = 0
	def isPreparedToLogout(self):
		return self.isPreparingToLogout
		
	def loggedSubmit(self):
		self.submitsLogged += 1
		if((self.submitsLogged==2)and(self.isPreparingToLogout)):
			self.resetVersion()
			self.submitsLogged=0
			if(verboseOutput):
				print "Resetting the version number and switching to next login section" 
		
	def hasEvents(self, date):
		if(date in self.events):
			return True
		else:
			return False
	
	def addEvent(self, date, event):
		if(self.version=="Unknown"):
			if date in self.eventsBuffer:
				if(event in self.eventsBuffer[date]):
					self.eventsBuffer[date][event] += 1
				else:
					self.eventsBuffer[date][event] = 1
			else:
				self.eventsBuffer[date] = {}
				self.eventsBuffer[date][event] = 1
		else:
			if date in self.events:
				if self.version in self.events[date]:
					if event in self.events[date][self.version]:
						self.events[date][self.version][event] += 1
					else:
						self.events[date][self.version][event] = 1
				else:
					self.events[date][self.version] = {}
					self.events[date][self.version][event] = 1
			else:
				self.events[date] = {}
				self.events[date][self.version] = {}
				self.events[date][self.version][event] = 1
		
	def addOperation(self, date, operation):
		#If operation is one of those calculated in the "Send(s)" metric
		if((operation=="Append")or(operation=="Send")):
			self.addEvent(date, "__Send")
		#If operation is a SubmitCC
		if(operation=="SubmitCC"):
			self.addEvent(date, "_CC")
		if(self.version=="Unknown"):	
			if date in self.operationsBuffer:
				if operation in self.operationsBuffer[date]:
					self.operationsBuffer[date][operation] += 1
				else:
					self.operationsBuffer[date][operation] = 1
			else:
				self.operationsBuffer[date] = {}
				self.operationsBuffer[date][operation] = 1
		else:	
			if date in self.operations:
				if self.version in self.operations[date]:
					if operation in self.operations[date][self.version]:
						self.operations[date][self.version][operation] += 1
					else: 
						self.operations[date][self.version][operation] = 1
				else:
					self.operations[date][self.version] = {}
					self.operations[date][self.version][operation] = 1
			else:
				self.operations[date] = {}
				self.operations[date][self.version] = {}
				self.operations[date][self.version][operation] = 1

	def printEventsOnDate(self, date):
		try:
			for version in sorted(self.events[date]):
				if date in self.events:
					if version in sorted(self.events[date]):
						sys.stdout.write("iWriteOn" + version + " - ")
						isFirst = True
						for event in sorted(self.events[date][version], key=str.lower):
							#print the records of important events
							if(isFirst):
								isFirst=False
							else:
								sys.stdout.write(", ")
							#Putting _ in front of an event will bump it to the front of the queue
							eventName = event
							eventName = eventName.replace('_','')
							if(self.events[date][version][event]>1):
								sys.stdout.write(str(self.events[date][version][event]).strip() + " " + eventName + "'s")
							else:
								sys.stdout.write(str(self.events[date][version][event]).strip() + " " + eventName)
						print ""
					else:
						if(verboseOutput):
							print "No events on " + date
				else:
					if(verboseOutput):
						print "No events on " + date
			stations = self.getStations(date)
			if(stations):
				for station in sorted(stations):
					if(verboseOutput):
						print "Get SLS Usage for " + station
					#Convert the date to a format used in this python module
					salesDateFormat = date.split("/")[2] + "-" + date.split("/")[0] + "-" + date.split("/")[1]
					if(verboseOutput):
						print self.pathName + "/sls" + date.split("/")[0] + date.split("/")[2][2:] + ".dbf"
					salesFileName = self.pathName + "/sls" + date.split("/")[0] + date.split("/")[2][2:] + ".dbf" 
					if os.path.isfile(salesFileName):
						salesByStation.main(salesFileName, salesDateFormat, station)
					else:
						if(verboseOutput):
							print "Sales data not found"
		except KeyError:
			print "No Usage Data"			
	
	def printForDate(self, date):
		try:
			for version in sorted(self.operations[date]):
				print date + " - iWriteOn" + version
				for operation in sorted(self.operations[date][version], key=str.lower):
					#print the records of important transactions
					print "Operation: " + operation + " occured # " + str(self.operations[date][version][operation]) + " times."
				#for version in self.events[date]:
				if version in self.events[date]:
					for event in sorted(self.events[date][version], key=str.lower):
						#print the records of important events
						print "Event: " + event + " occured # " + str(self.events[date][version][event]) + " times."
		except KeyError:
			print "There are no records for that date"
		
	def printEmailForAllDates(self):
		try:
			for date in sorted(self.events):
				print date
				self.printEventsOnDate(date)
				print ""
		except KeyError:
			print "There are no records for that date"
		
	def printForAllDates(self):
		try:
			for date in sorted(self.operations):
				for version in sorted(self.operations[date]):
					print date + " - iWriteOn" + version
					for operation in sorted(self.operations[date][version], key=str.lower):
						#print the records of important transactions
						print "Operation: " + operation + " occured # " + str(self.operations[date][version][operation]) + " times."
						
					if date in self.events:
						if version in sorted(self.events[date]):
							for event in sorted(self.events[date][version], key=str.lower):
								#print the records of important events
								print "Event: " + event + " occured # " + str(self.events[date][version][event]) + " times."
						else:
							if(verboseOutput):
								print "No events on " + date
					else:
						if(verboseOutput):
							print "No events on " + date
					print ""			
				
		except KeyError:
			print "There are no records for that date"
			
			
		

	
class errorHHEntry:
	# This class will decompose an entry line in error.hh
	Name = "errorHHEntry"
	message = "Default"

	# Bla about __init__
	def __init__(self, line):	
		self.line = line
		
		if(self.isOldLog(line)):
			#This section parses the old log file format.  This expects the line to contain ', /asi/iWriteOn/iWriteOn'.
			#192.168.30.103, 0, /asi/iWriteOn/iWriteOn17.0.2011.08170/asihh/iWriteOn/Classes/WOSoapCall.mm:327: 11/06/2011, 18:57:13, --- executeRequest: PutInfo URI:IEmployeeOps
			
			if(len(self.line.split(','))<5):
				return None
				
			self.date = line.split(',')[2].split(':')[-1].lstrip()
			self.time = line.split(',')[3].lstrip()
			self.ipAddress = line.split(',')[0].lstrip()
			self.station = line.split(',')[1].lstrip()
			self.source = line.split(',')[2].split(':')[0].lstrip()
			self.message = ''.join(line.split(',')[4:]).lstrip().rstrip()
		elif(self.isUDIDLog(line)):
			#This section parses an entry format which contains the UDID.  This expects to never find ', /asi/iWriteOn/iWriteOn' in a current log.
			#192.168.112.155, 0, 02/29/2012, 21:05:21, 4483, WOSoapCall.mm:408, --- executeRequest: fileGetTemp URI:IFileOps
			if(verboseOutput):
				print "We're UDID logging!!!"
			if(len(self.line.split(','))<7):
				return None
				
			self.date = line.split(',')[2].lstrip()
			self.time = line.split(',')[3].lstrip()
			self.ipAddress = line.split(',')[0].lstrip()
			self.station = line.split(',')[1].lstrip()
			self.source = line.split(',')[5].lstrip()
			self.message = ''.join(line.split(',')[6:]).lstrip().rstrip()
		else: 
			#This section parses the current log file format.  This expects to never find ', /asi/iWriteOn/iWriteOn' in a current log.
			#192.168.0.107, 0, 02/29/2012, 17:12:50, WOSoapCall.mm:426, --- executeRequest: fileGetTemp URI:IFileOps
			
			if(len(self.line.split(','))<6):
				return None
				
			self.date = line.split(',')[2].split(' ')[-1]
			self.time = line.split(',')[3].lstrip()
			self.ipAddress = line.split(',')[0].lstrip()
			self.station = line.split(',')[1].lstrip()
			self.source = line.split(',')[4].lstrip()
			self.message = ''.join(line.split(',')[5:]).lstrip().rstrip()

	#Display the entry without evaluating the message
	def display(self):
		if(self.message!="Default"):
			if(verboseOutput):
				print '<SOURCE=\"' + self.source + '\" MESSAGE=\"' + self.message + '\" DATE=\"' + self.date + '\" TIME=\"' + self.time + '\" IP=\"' + self.ipAddress  + '\"' + '>'
		else:
			if(verboseOutput):
				print self.line

	def getLine(self):
		return self.line
			
	def getMessage(self):
		return self.message
		
	def getSource(self):
		return self.source
		
	def getDate(self):
		return self.date
		
	def getTime(self):
		return self.time
		
	def getIP(self):
		return self.ipAddress
		
	def getStation(self):
		return self.station
		
	#This is a test to see if the log format matches the older log format.
	#Because we have a different number of columns in the two files, this simplifies my parsing
	def isOldLog(self, line):
		return re.search(', /asi/iWriteOn/iWriteOn',line)
		
	#This is a test to see if the log format matches the older log format.
	#Because we have a different number of columns in the two files, this simplifies my parsing
	def isUDIDLog(self, line):
		if(len(line.split(','))>4):
			potentialUDID = line.split(',')[4].lstrip()
			if(len(potentialUDID)!=4):
				return False
			return True
		else:
			return False
			
	#Request entry functions	
	#Example message: '--- executeRequest: fileGetTemp URI:IFileOps'
	def isRequest(this):
		return re.search('--- executeRequest:',this.message)
	def getRequestOp(this):
		return this.message.split(':')[1].lstrip().split(' ')[0]
	def getRequestURI(this):
		return this.message.split(':')[-1].lstrip()
	
	#Response entry functions
	#Example message: ' --- timer step  (18047 ms; incr: 265 ms) (endRequest: fileGetTemp URI:IFileOps (128 ms))'
	def isResponse(this):
		return re.search('\(endRequest:',this.message)
	def getResponseOp(this):
		return this.message.split('(endRequest:')[1].lstrip().split(' ')[0]
	def getResponseTime(this):
		#Which of these darn numbers is significant.  Ask Trevor?
		return None
	def getResponseURI(this):
		return this.message.split(':')[-1].split(' ')[0]
		
	#Memory log entry functions	
	#Example message: 'MEM: rss(17649664), vs(387981312), [fileGetTemp URI:IFileOps]'
	def isMemoryLog(this):
		return re.search('MEM:',this.message)
	def getMemoryLogOp(this):
		return this.message.split('[')[1].split(' ')[0].lstrip()
	def getMemoryLogRSS(this):
		return this.message.split('rss(')[1].split(')')[0]
	def getMemoryLogVS(this):
		return this.message.split('vs(')[1].split(')')[0]
	def getMemoryLogURI(this):
		return this.message.split(':')[-1].split(']')[0]
	
	#This will determine if a line contains a "memory warning"
	#Example message: 'MB:This application is getting low on memory.  Please restart it.'
	def isMemoryWarning(this):
		return re.search('MB:This application is getting low on memory.  Please restart it.', this.message)
	
	#These will determine if the line contains one of the following networking error messages

	#Example message: 'MB:Unable to connect to server.'
	def isUnableToConnect(this):
		return re.search('MB:Unable to connect to server.', this.message)
		
	#Example message: 'MB:Could not connect to the server.'
	def isCouldNotConnect(this):
		return re.search('MB:Could not connect to the server.', this.message)

	#Example message: 'MB:network connection timed out'
	def isConnectionTimeout(this):
		return re.search('MB:network connection timed out', this.message)

	#Example message: 'MB:The Internet connection appears to be offline.'
	def isInternetOffline(this):
		return re.search('MB:The Internet connection appears to be offline.', this.message)
		
	#Example message: 'MB:Network error.  Items may not have been sent.  Open the table or tab and use the &#39;Recover Order&#39; command to recover any unsent items.'
	def isRecoverySuggestion(this):
		return re.search('MB:Network error.  Items may not have been sent.', this.message)
		
	#Example message: '--- Application launching.'
	def isApplicationLaunching(this):
		return re.search('--- Application launching.', this.message)
	
	#This will keep track of which employee is logged in.
	#Example message: '--- empLogin 6 (Anna Wall) Dining Area 1'
	def isEmpLogin(this):
		return re.search('--- empLogin', this.message)
	def getEmpLoginName(this):
		return this.message.split('(')[1].split(')')[0]
	def getEmpLoginEmpNo(this):
		return this.message.split('--- empLogin ')[1].split(' ')[0]
	def getEmpLoginDiningArea(this):
		return this.message.split('Dining Area ')[1].lstrip()
		
	#This is necessary to know when to break between login sessions
	#Example message: ' --- Preparing to log out.'
	def isLogout(this):
		return re.search('Preparing to log out.',this.message)
		
	def isClientSubmittedLog(this):
		return re.search('Client submitted log', this.line)
	
	#Version number entry functions
	#Example message: ' this source file: /asi/iWriteOn/iWriteOn18.0.2012.02240/asihh/iWriteOn/../pocketrmpos/PocketRMPOSDlg.cpp:488'
	def isVersionLog(this):
		return re.search('iWriteOn/iWriteOn',this.line)	
	def getVersion(this):
		return this.line.split('iWriteOn/iWriteOn')[1].split('/')[0]
	
	#This is just to keep track of entries which do not fit into some (currently) important metric
	def isNone(this):
		return this.message=="Default"

def readErrorHH(thisSession):
	#Read the entries in error.hh specified by filename and store the results into thisSession
	ignoredLines = []
	unhandledLines = []
	fileReader = open(thisSession.getPathName() + "/error.hh", 'r')
	
	
	for line in fileReader:
		entry = errorHHEntry(line)
		
		if(not entry.isNone() ):	
			if(verboseOutput):
				entry.display()
			if(entry.isRequest()):
				if(verboseOutput):
					print "Source: " + entry.getSource() + "URI: " + entry.getRequestURI() + " Request Op: " + entry.getRequestOp()
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
					
				if(entry.isVersionLog()):
					if(verboseOutput):
						print "Version is 	" + entry.getVersion() + " Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()	
					thisSession.setVersion(entry.getVersion())
					
				thisSession.addOperation(entry.getDate(),entry.getRequestOp())
				thisSession.addStation(entry.getDate(), entry.getStation())
			elif(entry.isMemoryLog()):
				if(verboseOutput):
					print "Source: " + entry.getSource() + " Memory Log Op: " + entry.getMemoryLogOp() + " URI: " + entry.getMemoryLogURI()
					print "RSS=" + entry.getMemoryLogRSS() + " VS=" + entry.getMemoryLogVS() 
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
			elif(entry.isResponse()):
				if(verboseOutput):
					print "Source: " + entry.getSource() + " Response Op: " + entry.getResponseOp() + " URI: " + entry.getResponseURI()
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
			elif(entry.isLogout()):
				if(verboseOutput):
					print "Preparing to logout" + " Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.prepareToLogout()
			elif(entry.isEmpLogin()):
				if(verboseOutput):
					print "Employee Name: " + entry.getEmpLoginName() + " Number: " + entry.getEmpLoginEmpNo() + " Dining Area: " + entry.getEmpLoginDiningArea()
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
			elif(entry.isClientSubmittedLog()):
				if(verboseOutput):
					print "Client submitted log"
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.loggedSubmit()
			elif(entry.isMemoryWarning()):
				if(verboseOutput):
					print "Adding Memory Warning"
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.addEvent(entry.getDate(), "Low Memory")
			elif(entry.isUnableToConnect()):
				if(verboseOutput):
					print "Unable to connect to server."
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.addEvent(entry.getDate(), "Net Connect")
			elif(entry.isCouldNotConnect()):
				if(verboseOutput):
					print "Could not connect to the server."
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.addEvent(entry.getDate(), "Net Connect")
			elif(entry.isConnectionTimeout()):
				if(verboseOutput):
					print "Network connection timed out."
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.addEvent(entry.getDate(), "Net Timeout")
			elif(entry.isInternetOffline()):
				if(verboseOutput):
					print "The Internet connection appears to be offline."
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.addEvent(entry.getDate(), "Net Internet")
			elif(entry.isRecoverySuggestion()):
				if(verboseOutput):
					print "Network Error.  Items may not have been sent."
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.addEvent(entry.getDate(), "Net Recovery")
			elif(entry.isApplicationLaunching()):
				if(verboseOutput):
					print "Application Launching"
					print "Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				#thisSession.addEvent(entry.getDate(), "App Launch")
			elif(entry.isVersionLog()):
				if(verboseOutput):
					print "Version is " + entry.getVersion() + " Date: " + entry.getDate() + " Time: " + entry.getTime() + " IP: " + entry.getIP()
				thisSession.setVersion(entry.getVersion())
			else:
				if(verboseOutput):
					print "This line didn't \"fit in\""
					unhandledLines.append(line)
		else:
			if(verboseOutput):
				print entry.getLine()
				print "This line is ignored"
				ignoredLines.append(line)
		if(verboseOutput):
			print ""
	
	if(verboseOutput):
		print "Unhandled lines = " + str(unhandledLines)
		print "Ignored lines = " + str(ignoredLines)
	
def printForEmail(currentSession, selectedDate):
	selectedDateAsFormattedString = selectedDate.strftime("%m/%d/%Y") 
	currentSession.printEventsOnDate(selectedDateAsFormattedString)	
	
def getResultsForSessionOnDate(currentSession, selectedDate):
	selectedDateAsFormattedString = selectedDate.strftime("%m/%d/%Y") 
	print "We want the results for: " + selectedDateAsFormattedString
	print ""
	currentSession.printForDate(selectedDateAsFormattedString)
	
def getResultsForAllSessions(currentSession):
	today = datetime.date.today()
	selectedDateAsFormattedString = today.strftime("%m/%d/%Y") 
	print "On " + selectedDateAsFormattedString + " we want results for all sessions."
	print ""
	currentSession.printEmailForAllDates()

def getResultsForDirectory(directoryName):
	currentSession = session(directoryName)
	readErrorHH(currentSession)
	currentSession.printEmailForAllDates()
	
def getYesterdaysResultsForDirectory(directoryName):
	currentSession = session(directoryName)
	readErrorHH(currentSession)

	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)
	yesterdayAsFormattedString = yesterday.strftime("%m/%d/%Y") 
	
	
def runDailyProcess(processDirectory):
	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)
	yesterdayAsFormattedString = yesterday.strftime("%m/%d/%Y") 
	print "Usage for " + yesterdayAsFormattedString + ":"
	print ""
	for directory in os.listdir(processDirectory):
		if os.path.isdir(os.path.join(processDirectory, directory)):
			currentDirectory = processDirectory + "/" + directory
			currentSession = session(currentDirectory)
			readErrorHH(currentSession)
			
			numberOfCrashes = 0
			for crashFile in os.listdir(currentDirectory):
				#print crashFile
				if fnmatch.fnmatch(crashFile, "writeon_" + yesterday.strftime("%Y-%m-%d") + "*.crash"):
					numberOfCrashes += 1
					
			if(currentSession.hasEvents(yesterdayAsFormattedString)):
				print "Site: " + directory
				if(numberOfCrashes == 0):
					print "No Crashes."
				else:
					print "Number Of Crashes: " + str(numberOfCrashes)
				
				currentSession.printEventsOnDate(yesterdayAsFormattedString)
				print ""
	
if __name__=="__main__":

	processDirectory = "C:/process"
	runDailyProcess(processDirectory)
	
	