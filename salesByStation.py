import datetime, sys
from mx import DateTime
from dbfpy import dbf

def main(fileName, date, stationNumber):
	countStationSales(fileName, date, stationNumber)

def countStationSales(filename, onDate, stationNumber):
	db = dbf.Dbf(filename)
	start_stations_bydate = {}
	settle_stations_bydate = {}
	stations = []
	
	for rec in db:
		""" Determine database elements """
		# print "DATE: " + str(rec[10])
		date = str(rec[10])
		# print "START_STN: " + str(rec[43])
		start_station = str(rec[43])
		# print "SETTLE_STN: " + str(rec[44])
		settle_station = str(rec[44])
		# print "\n"
		
		if not date in start_stations_bydate:
			""" Date is not found """
			start_stations_bydate[date] = {}
			settle_stations_bydate[date] = {}
			start_stations_bydate[date][start_station] = 1
			settle_stations_bydate[date][settle_station] = 1
			if not start_station in stations: stations.append(start_station)
			if not settle_station in stations: stations.append(settle_station)
		else:
			""" Date is Found """
			if not start_station in stations: stations.append(start_station)
			if not settle_station in stations: stations.append(settle_station)
			
			if not start_station in start_stations_bydate[date]: start_stations_bydate[date][start_station] = 1
			else: start_stations_bydate[date][start_station] = start_stations_bydate[date][start_station] + 1
			
			if not settle_station in settle_stations_bydate[date]: settle_stations_bydate[date][settle_station] = 1
			else: settle_stations_bydate[date][settle_station] = settle_stations_bydate[date][settle_station] + 1
			
		
	stations.sort()
	
	total_checks_settled = 0
	total_checks_settled_bystation = {}
	total_checks_started = 0
	total_checks_started_bystation = {}

	
	
	for date in sorted(start_stations_bydate):
		#print "\n" + date

		checks_started_today = 0
		checks_settled_today = 0
		
		""" Initialize and update larger comparisons """
		for station in stations:
			if station in start_stations_bydate[date]: 
				checks_started_today += start_stations_bydate[date][station]
				total_checks_started += start_stations_bydate[date][station]
				if station not in total_checks_started_bystation:
					total_checks_started_bystation[station] = start_stations_bydate[date][station]
				else: total_checks_started_bystation[station] += start_stations_bydate[date][station]
			if station in settle_stations_bydate[date]: 
				checks_settled_today += settle_stations_bydate[date][station]
				total_checks_settled += settle_stations_bydate[date][station]
				if station not in total_checks_settled_bystation:
					total_checks_settled_bystation[station] = settle_stations_bydate[date][station]
				else: total_checks_settled_bystation[station] += settle_stations_bydate[date][station]
			
		""" Display by Station
		for station in stations:
			if station in start_stations_bydate[date]: print " + Checks Started At Station " + station + ": " + str(start_stations_bydate[date][station]) + " (%.2f"  % (100* float(start_stations_bydate[date][station]) / float(checks_started_today) ) + "%)"
			if station in settle_stations_bydate[date]: print " - Checks Settled At Station " + station + ": " + str(settle_stations_bydate[date][station]) + " (%.2f"  % (100*float(settle_stations_bydate[date][station])/float(checks_settled_today)) + "%)"
		"""
		
		""" Display Start and Settle separately
		for station in stations:
			if station in start_stations_bydate[date]: print " + Checks Started At Station " + station + ": " + str(start_stations_bydate[date][station]) + " (%.2f"  % (100* float(start_stations_bydate[date][station]) / float(checks_started_today) ) + "%)"
		for station in stations:
			if station in settle_stations_bydate[date]: print " - Checks Settled At Station " + station + ": " + str(settle_stations_bydate[date][station]) + " (%.2f"  % (100*float(settle_stations_bydate[date][station])/float(checks_settled_today)) + "%)"
		"""

		
	"""print "\n\n***** Monthly Totals *****\n"
		
	for station in stations:
		if station in total_checks_started_bystation: 
			print "Total Checks Started At Station " + station + ": " + str(total_checks_started_bystation[station]) + " (%.2f" % (float(100)*float(total_checks_started_bystation[station])/float(total_checks_started)) + "%)"
	print
	for station in stations:
		if station in total_checks_settled_bystation: 
			print "Total Checks Settled At Station " + station + ": " + str(total_checks_settled_bystation[station]) + " (%.2f" % (float(100)*float(total_checks_settled_bystation[station])/float(total_checks_settled)) + "%)"
	"""
	
			
	if onDate in start_stations_bydate:
		if stationNumber in start_stations_bydate[onDate]: 
			total_checks_started_onDate = 0
			for station in start_stations_bydate[onDate]: total_checks_started_onDate += start_stations_bydate[onDate][station]
			print "Checks Started on Station " + stationNumber + ": " + str(start_stations_bydate[onDate][stationNumber]) + " (%.2f"  % (100*float(start_stations_bydate[onDate][stationNumber])/float(total_checks_started_onDate)) + "% of total)"
		else: print "Checks Started on Station " + stationNumber + ": 0 (0.00% of total)"
	else: print "No Checks Started on " + onDate
	
	if onDate in settle_stations_bydate:
		if stationNumber in settle_stations_bydate[onDate]: 
			total_checks_settled_onDate = 0
			for station in settle_stations_bydate[onDate]: total_checks_settled_onDate += settle_stations_bydate[onDate][station]
			print "Checks Settled on Station " + stationNumber + ": " + str(settle_stations_bydate[onDate][stationNumber]) + " (%.2f"  % (100*float(settle_stations_bydate[onDate][stationNumber])/float(total_checks_settled_onDate)) + "% of total)"
		else: print "Checks Settled on Station " + stationNumber + ": 0 (0.00% of total)"
	else: print "No Checks Settled on " + onDate
 

if __name__ == "__main__":
	countStationSales(sys.argv[1],sys.argv[2],sys.argv[3])
