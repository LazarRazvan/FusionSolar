'''
Before running this source file make sure you follow the instructions
from https://forum.huawei.com/enterprise/en/communicate-with-fusionsolar-through-an-openapi-account/thread/591478-100027?page=3

You can't access Fusion Solar devices without an OpenAPI account previously created.
'''

import requests
import json
import sys

'''
OpenAPI utils.

@login_url  : Login url for POST method.
@logout_url : Logout url for POST method.
@login_obj  : JSON object containing login credentials.
@xsrf_token : Session token returned by login method.
'''
login_url = 'https://eu5.fusionsolar.huawei.com/thirdData/login'
logout_url = 'https://eu5.fusionsolar.huawei.com/thirdData/logout'
login_obj = {
	"userName" : "<openapi_username>",
	"systemCode" : "<openapi_password>" 
}
xsrf_token = ''


def openapi_login():
	"""
	Perform login to OpenAPI account.

	Use credentials and inspect response to check status.
	"""

	global xsrf_token

	# Send POST request
	response = requests.post(
							login_url,
							json = login_obj,
							cookies = {"web-auth" : "true", "Cookie_1" : "value"},
							timeout = 3600
							)

	# Evaluate login status
	try:
		json_status = json.loads(response.content)
		print ("INFO: Login response from server %s" % json_status)
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



# OpenAPI Logout method
def openapi_logout():
	"""
	Perform logout to OpenAPI account.

	Use credentials and inspect response to check status.
	"""
	logout_obj = { "xsrfToken" : xsrf_token }

	# Send POST request
	response = requests.post(
							logout_url,
							json = logout_obj,
							cookies = {"XSRF-TOKEN" : xsrf_token, "web-auth" : "true"},
							headers = {"XSRF-TOKEN": xsrf_token}
							)

	# Evaluate logout status
	try:
		json_status = json.loads(response.content)
		print ("INFO: Logout response from server %s" % json_status)
		if json_status['success'] == False:
			print ("ERROR: Logout Failed")
			sys.exit()

		print ("INFO: Logout Successfully")

	except ValueError:
		print ("ERROR: Logout unexpected response from server")



if __name__ == "__main__":
	openapi_login()
	openapi_logout()
