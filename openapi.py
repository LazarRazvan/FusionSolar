'''
Before running this source file make sure you follow the instructions
from https://forum.huawei.com/enterprise/en/communicate-with-fusionsolar-through-an-openapi-account/thread/591478-100027?page=3

You can't access Fusion Solar devices without an OpenAPI account previously created.
'''

import requests
import json
import sys

'''
OpenAPI URLs
@login_url  			: Login url for POST method.
@logout_url 			: Logout url for POST method.
@get_station_list_url	: Get stations list url for POST method.
@real_time_data_url		: Power station info url for POST method.
'''
login_url = 'https://eu5.fusionsolar.huawei.com/thirdData/login'
logout_url = 'https://eu5.fusionsolar.huawei.com/thirdData/logout'
get_station_list_url = 'https://eu5.fusionsolar.huawei.com/thirdData/getStationList'
real_time_data_url = 'https://eu5.fusionsolar.huawei.com/thirdData/getStationRealKpi'


'''
OpenAPI variables.

@username		: OpenAPI username.
@password		: OpenAPI password.
@xsrf_token 	: Session token returned by login method.
@plant_name		: Plant name to be interrogated.
@station_code	: Station code returned by get statil list method
'''
username = ''
password = ''
xsrf_token = ''
plant_name = ''
station_code = ''

def read_credentials():
	"""
	Function to read OpenAPI credentials (username/password).
	"""
	global username
	global password

	print ("Enter OpenAPI Credentials")
	username = input("Username: ")
	password = input("Password: ")


def openapi_login():
	"""
	Perform login to OpenAPI account.

	Requires username and passowrd and return session token in response cookie.
	"""

	global xsrf_token
	login_obj = {
		"userName" : username,
		"systemCode" : password
	}	

	# Send login request
	response = requests.post(
							login_url,
							json = login_obj,
							cookies = {"web-auth" : "true", "Cookie_1" : "value"},
							timeout = 3600
							)

	# Inspect login response
	try:
		json_status = json.loads(response.content)
		if json_status['success'] == False:
			print ("ERROR: Login Failed")
			sys.exit()

		print ("INFO: Login Successfully")

	except ValueError:
		print ("ERROR: Login unexpected response from server")

	# Get session cookie (xsrf-token)
	cookies_dict = response.cookies.get_dict()
	if "XSRF-TOKEN" not in cookies_dict:
		print ("ERROR: XSRF-TOKEN not found in cookies")
		sys.exit()

	xsrf_token = cookies_dict.get("XSRF-TOKEN")
	print ("XSRF-TOKEN: %s" % xsrf_token)

def openapi_get_station_list():
	"""
	Read station list for current user.

	Require session token.
	"""
	global station_code
	global plant_name
	plant_obj = {}

	# Send get station list request
	response = requests.post(
							get_station_list_url,
							json = plant_obj,
							cookies = {"XSRF-TOKEN" : xsrf_token, "web-auth" : "true"},
							headers = {"XSRF-TOKEN": xsrf_token},
							timeout = 3600
	)

	# Inspect response
	try:
		json_plant = json.loads(response.content)
		if json_plant['success'] == False:
			print ("ERROR: Get Station List Failed")
			openapi_logout()
			sys.exit()

	except ValueError:
		openapi_logout()
		print ("ERROR: Get station list unexpected response from server")
		sys.exit()

	# read plant name
	plant_name = input("Enter plant name: ")

	print ("INFO: Stations list:")
	# plant name lookup inside plants list
	for station in json_plant['data']:
		if "stationName" not in station:
				print ("ERROR: Unknown format in get station list response")
				openapi_logout()
				sys.exit()
		
		print ("INFO: Station name : %s; Station code : %s" % (station.get('stationName'), station.get('stationCode')))
		if station.get('stationName') == plant_name:
			station_code = station.get('stationCode')

	if station_code == '':
		print ("ERROR: Plant name %s not found in station list" % plant_name)


# OpenAPI Read Station Real TimeData
def openapi_real_time_data():
	rtime_obj = { "stationCodes" : station_code }

	# Send real time data request
	response = requests.post(
							real_time_data_url,
							json = rtime_obj,
							cookies = {"XSRF-TOKEN" : xsrf_token, "web-auth" : "true"},
							headers = {"XSRF-TOKEN": xsrf_token},
							timeout = 3600
	)

	# Evaluate real time response
	try:
		json_rtime = json.loads(response.content)
		if json_rtime['success'] == False:
			print ("ERROR: Real Time Information Failed")
			openapi_logout()
			sys.exit()

	except ValueError:
		openapi_logout()
		print ("ERROR: Plant list unexpected response from server")


	print ("INFO: Real time data for %s station:" % plant_name)
	# Print values
	for data_obj in json_rtime['data']:
		map_obj = data_obj.get('dataItemMap')
		print ("Day power : %s" % map_obj.get('day_power'))
		print ("Month power : %s" % map_obj.get('month_power'))
		print ("Total power : %s" % map_obj.get('total_power'))
		print ("Health State : %s" % map_obj.get('real_health_state'))		


def openapi_logout():
	"""
	Perform logout to OpenAPI account.

	Requires session token.
	"""
	logout_obj = { "xsrfToken" : xsrf_token }

	# Send logout request
	response = requests.post(
							logout_url,
							json = logout_obj,
							cookies = {"XSRF-TOKEN" : xsrf_token, "web-auth" : "true"},
							headers = {"XSRF-TOKEN": xsrf_token}
							)

	# Inspect logout response
	try:
		json_status = json.loads(response.content)
		if json_status['success'] == False:
			print ("ERROR: Logout Failed")
			sys.exit()

		print ("INFO: Logout Successfully")
	except ValueError:
		print ("ERROR: Logout unexpected response from server")


if __name__ == "__main__":
	read_credentials()
	openapi_login()
	openapi_get_station_list()
	openapi_real_time_data()
	openapi_logout()