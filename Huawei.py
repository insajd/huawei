#       Huawei Library made by Christian Bianchini 7 November 2012
#
#       This library is working with the model E3131 but what I have seen on the API calls,
#       you can try to use it with other different models and expand this library
#
#       For any issues or improvment that you'd like to add on this library, just send me an email
#       max246@gmail.com
#
#
#       You can use this library without any restrictions!
#       V1.0
#		V1.1 - 25-10-2015 Library changed to work with E3372

from xml.dom import minidom
from array import *

import requests
import re

s = None;

def grep_csrf(html):
	pat = re.compile(r".*meta name=\"csrf_token\" content=\"(.*)\"", re.I)
	matches = (pat.match(line) for line in html.splitlines())
	return [m.group(1) for m in matches if m]

class Huawei():
	ip = "http://192.168.8.1"
	xml_response = 0
	xml_error = 0

	def __init__(self):
		global s
		print ("Huawei object started")
		s = requests.Session()
		r = s.get(self.ip + "/html/index.html")
		csrf_tokens = grep_csrf(r.text)
		s.headers.update({'__RequestVerificationToken': csrf_tokens[0]})

	def getText(self,nodelist):
            """ Method to get the text from a dom node """
	    rc = []
	    for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
		    rc.append(node.data)
	    return ''.join(rc)
	def send_request(self,url,header,data):
		if data is not None:
			if header != '':
				s.headers.update (header)
			r = s.post(self.ip + url, data=data)
			s.headers.update({'__RequestVerificationToken': r.headers['__RequestVerificationToken']})
		else:
			r = s.get(self.ip + url, data=data)
		result = r.text
		
		print (result)
		return result
	def parse_xml(self,data):
		""" Parse the xml output from the http request and returns True if the responde is ok otherwise there is an error """
		xmldoc = minidom.parseString(data)
		self.xml_error = xmldoc.getElementsByTagName("error")
		if len(self.xml_error) > 0: 
			return False
		else:
			self.xml_response = xmldoc.getElementsByTagName("response")
			return True
	def connect(self):
		""" Method to connect the dongle at the network """
		data = "<request><Action>1</Action></request>"
		result = self.send_request("/api/dialup/dial","",data)
		if self.parse_xml(result):
			return True
		else:
			return False
	def disconnect(self):
		""" Method to disconnect the dongle from the internet connection """
		data = "<request><Action>0</Action></request>"
		result = self.send_request("/api/dialup/dial","",data)
		if self.parse_xml(result):
			return True
		else:
			return False
	def get_sms_count(self):
		""" Method to return the count of all sms stored on the sim and dongle """
		result = self.send_request("/api/sms/sms-count","",None)
		if self.parse_xml(result):
			print  self.getText(self.xml_response[0].getElementsByTagName("LocalUnread")[0].childNodes)
			localUnread = self.getText(self.xml_response[0].getElementsByTagName("LocalUnread")[0].childNodes)
			localInbox = self.getText(self.xml_response[0].getElementsByTagName("LocalInbox")[0].childNodes)
			localOutbox = self.getText(self.xml_response[0].getElementsByTagName("LocalOutbox")[0].childNodes)
			localDraft = self.getText(self.xml_response[0].getElementsByTagName("LocalDraft")[0].childNodes)
			localDeleted = self.getText(self.xml_response[0].getElementsByTagName("LocalDeleted")[0].childNodes)
			simUnread = self.getText(self.xml_response[0].getElementsByTagName("SimUnread")[0].childNodes)
			simInbox = self.getText(self.xml_response[0].getElementsByTagName("SimInbox")[0].childNodes)
			simOutbox = self.getText(self.xml_response[0].getElementsByTagName("SimOutbox")[0].childNodes)
			simDraft = self.getText(self.xml_response[0].getElementsByTagName("SimDraft")[0].childNodes)
			localMax = self.getText(self.xml_response[0].getElementsByTagName("LocalMax")[0].childNodes)
			simMax = self.getText(self.xml_response[0].getElementsByTagName("SimMax")[0].childNodes)
			resultArray = [localUnread,localInbox,localOutbox,localDraft,localDeleted,simUnread,simInbox,simOutbox,simDraft,localMax,simMax]
			return resultArray		
		else:
			return None
	def delete_sms(self,index):
		""" Method to delete a sms message """
		data = "<request>"
		data += "<Index>"+str(index)+"</Index>"
		data += "</request>"
                result = self.send_request("/api/sms/delete-sms","",data)
                if self.parse_xml(result):
			return True
		else:
			return False
	def get_sms_list(self):
		""" Method to get the list of messages in the inbox"""
		data = "<request>"
		data += "<PageIndex>1</PageIndex>"
		data += "<ReadCount>20</ReadCount>"
		data += "<BoxType>1</BoxType>"
		data += "<SortType>0</SortType>"
		data += "<Ascending>0</Ascending>"
		data += "<UnreadPreferred>0</UnreadPreferred>"
		data += "</request>"
		result = self.send_request("/api/sms/sms-list","",data)
                if self.parse_xml(result):
                        count = int(self.getText(self.xml_response[0].getElementsByTagName("Count")[0].childNodes))
                        if count > 0: #IF there is more than 1 message
                                messages = (self.xml_response[0].getElementsByTagName("Message"))
                                resultArray = []
                                for message in messages:
                                        resultArray.append(self.get_sms(message))
                                return resultArray
                                        
                        else:#No messages in the inbox
                                return None
                else:
                        return None          
	def get_sms(self,sms):
			""" Method to get the message from the dom object """
			smstat = self.getText(sms.getElementsByTagName("Smstat")[0].childNodes)
			index = self.getText(sms.getElementsByTagName("Index")[0].childNodes)
			phone = self.getText(sms.getElementsByTagName("Phone")[0].childNodes)
			content = self.getText(sms.getElementsByTagName("Content")[0].childNodes)
			date = self.getText(sms.getElementsByTagName("Date")[0].childNodes)
			sca = self.getText(sms.getElementsByTagName("Sca")[0].childNodes)
			saveType = self.getText(sms.getElementsByTagName("SaveType")[0].childNodes)
			priority = self.getText(sms.getElementsByTagName("Priority")[0].childNodes)
			smsType = self.getText(sms.getElementsByTagName("SmsType")[0].childNodes)
			resultArray = [smstat,index,phone,content,date,sca,
							saveType,priority,smsType]
			return resultArray
	def set_sms_read(self,index):
		""" Method to set a message as read """
		data = "<request><Index>"+str(index)+"</Index></request>"
		result = self.send_request("/api/sms/send-sms","",data)
		if self.parse_xml(result):
			return True
		else:
			return False
	def send_message(self,index,phone_number,content,date):
		""" Method to send a message 
			 -1 if its not a replay to any index """
		data = "<request>"
		data += "<Index>"+str(index)+"</Index>"
		data += "<Phones><Phone>"+str(phone_number)+"</Phone></Phones>"
		data += "<Sca></Sca>"
		data += "<Content>"+str(content)+"</Content>"
		data += "<Length>"+str(len(content))+"</Length>"
		data += "<Reserved>1</Reserved>"
		data += "<Date>"+date+"</Date>"
		data += "</request>"
		result = self.send_request("/api/sms/send-sms","",data)
		if self.parse_xml(result):
			return True
		else:
			return False
	def set_connection_settings(self,roam_enable_autoconnect,autoreconnect,roam_autoreconnect,reconnect_interval,max_idle_time,connect_mode):
		"""Method to set connection settings """
		data = "<request>"
		data += "<RoamAutoConnectEnable>"+str(roam_enable_autoconnect)+"</RoamAutoConnectEnable>"
		data += "<AutoReconnect>"+str(autoreconnect)+"</AutoReconnect>"
		data += "<RoamAutoReconnctEnable>"+str(roam_autoreconnect)+"</RoamAutoReconnctEnable>"
		data += "<ReconnectInterval>"+str(reconnect_interval)+"</ReconnectInterval>"
		data += "<MaxIdelTime>"+str(max_idle_time)+"</MaxIdelTime>"
		data += "<ConnectMode>"+str(connect_mode)+"	</ConnectMode>"
		data += "</request>"
		result = self.send_request("/api/dialup/connection","",data)
		if self.parse_xml(result):
			return True
		else:
			return False
	def pin_operations(self,operate_type,current_pin,new_pin,puk_code):
		""" Method to modify the sim's autentication  """
		data = "<request>"
		data += "<OperateType>"+str(operate_type)+"</OperateType>"
		data += "<CurrentPin>"+str(current_pin)+"</CurrentPin>"
		data += "<NewPin>"+str(new_pin)+"</NewPin>"
		data += "<PukCode>"+str(puk_code)+"</PukCode>"
		data += "</request>"
		result = self.send_request("/api/pin/operate","",data)
		if self.parse_xml(result):
			return True
		else:
			return False
	def get_connection_status(self):
		result = self.send_request("/api/monitoring/status","",None)
                if self.parse_xml(result):
                        connectionStatus = self.getText(self.xml_response[0].getElementsByTagName("ConnectionStatus")[0].childNodes)
                        signalStrength = self.getText(self.xml_response[0].getElementsByTagName("SignalStrength")[0].childNodes)
                        signalIcon = self.getText(self.xml_response[0].getElementsByTagName("SignalIcon")[0].childNodes)
                        currentNetworkType = self.getText(self.xml_response[0].getElementsByTagName("CurrentNetworkType")[0].childNodes)
                        currentServiceDomain = self.getText(self.xml_response[0].getElementsByTagName("CurrentServiceDomain")[0].childNodes)
                        roamingStatus = self.getText(self.xml_response[0].getElementsByTagName("RoamingStatus")[0].childNodes)
                        batteryStatus = self.getText(self.xml_response[0].getElementsByTagName("BatteryStatus")[0].childNodes)
                        batteryLevel = self.getText(self.xml_response[0].getElementsByTagName("BatteryLevel")[0].childNodes)
                        simlockStatus = self.getText(self.xml_response[0].getElementsByTagName("simlockStatus")[0].childNodes)
                        wanIPAddress = self.getText(self.xml_response[0].getElementsByTagName("WanIPAddress")[0].childNodes)
                        primaryDNS = self.getText(self.xml_response[0].getElementsByTagName("PrimaryDns")[0].childNodes)
                        secondaryDNS = self.getText(self.xml_response[0].getElementsByTagName("SecondaryDns")[0].childNodes)
                        currentWifiUser = self.getText(self.xml_response[0].getElementsByTagName("CurrentWifiUser")[0].childNodes)
                        totalWifiUser = self.getText(self.xml_response[0].getElementsByTagName("TotalWifiUser")[0].childNodes)
                        serviceStatus = self.getText(self.xml_response[0].getElementsByTagName("ServiceStatus")[0].childNodes)
                        simStatus = self.getText(self.xml_response[0].getElementsByTagName("SimStatus")[0].childNodes)
                        wifiStatus = self.getText(self.xml_response[0].getElementsByTagName("WifiStatus")[0].childNodes)
                        resultArray = [connectionStatus,signalStrength,signalIcon,currentNetworkType,
                                        currentServiceDomain,roamingStatus,batteryStatus,batteryLevel,simlockStatus,
                                        wanIPAddress,primaryDNS,secondaryDNS,currentWifiUser,totalWifiUser,serviceStatus,
                                        simStatus,wifiStatus]
                        return resultArray
                else:
                        return None
	def check_notifications(self):
		""" Method to get the current status of all important notifications """
		result = self.send_request("/api/monitoring/check-notifications","",None)
		if self.parse_xml(result):
			unreadMessage = self.getText(self.xml_response[0].getElementsByTagName("UnreadMessage")[0].childNodes)
			smsStorageFull = self.getText(self.xml_response[0].getElementsByTagName("SmsStorageFull")[0].childNodes)
			onlineUpdateStatus = self.getText(self.xml_response[0].getElementsByTagName("OnlineUpdateStatus")[0].childNodes)
			responseArray = [unreadMessage,smsStorageFull,onlineUpdateStatus]
			return responseArray
		else:
			return None

	def get_network_information(self):
		""" Method to return the current plmn information """
		result = self.send_request("/api/net/current-plmn","",None)
		if self.parse_xml(result):
			state = self.getText(self.xml_response[0].getElementsByTagName("State")[0].childNodes)
			full_name = self.getText(self.xml_response[0].getElementsByTagName("FullName")[0].childNodes)
			short_name = self.getText(self.xml_response[0].getElementsByTagName("ShortName")[0].childNodes)
			numeric = self.getText(self.xml_response[0].getElementsByTagName("Numeric")[0].childNodes)
			rat = self.getText(self.xml_response[0].getElementsByTagName("Rat")[0].childNodes)
			responseArray = [state,full_name,short_name,numeric,rat]
			return responseArray
		else:
			return None
	def get_device_information(self):
		""" Method to return all information about the device """
		result = self.send_request("/api/device/information","",None)
		if self.parse_xml(result):
			deviceName = self.getText(self.xml_response[0].getElementsByTagName("DeviceName")[0].childNodes)
			serialNumber = self.getText(self.xml_response[0].getElementsByTagName("SerialNumber")[0].childNodes)
			imei = self.getText(self.xml_response[0].getElementsByTagName("Imei")[0].childNodes)
			imsi = self.getText(self.xml_response[0].getElementsByTagName("Imsi")[0].childNodes)
			iccid = self.getText(self.xml_response[0].getElementsByTagName("Iccid")[0].childNodes)
			msisdn = self.getText(self.xml_response[0].getElementsByTagName("Msisdn")[0].childNodes)
			hardwareVersion = self.getText(self.xml_response[0].getElementsByTagName("HardwareVersion")[0].childNodes)
			softwareVersion = self.getText(self.xml_response[0].getElementsByTagName("SoftwareVersion")[0].childNodes)
			webUIVersion = self.getText(self.xml_response[0].getElementsByTagName("WebUIVersion")[0].childNodes)
			#uptime = self.getText(self.xml_response[0].getElementsByTagName("Uptime")[0].childNodes)
			macAddress = self.getText(self.xml_response[0].getElementsByTagName("MacAddress1")[0].childNodes)
			macAddress2 = self.getText(self.xml_response[0].getElementsByTagName("MacAddress2")[0].childNodes)
			productFamily = self.getText(self.xml_response[0].getElementsByTagName("ProductFamily")[0].childNodes)
			classify = self.getText(self.xml_response[0].getElementsByTagName("Classify")[0].childNodes)
			responseArray = [deviceName,serialNumber,imei,imsi,iccid,msisdn,hardwareVersion,
                                        softwareVersion,webUIVersion,
										#uptime,
										macAddress,macAddress2,
                                        productFamily,classify]
			return responseArray
		else:
			return None

	def is_connected(self):
		""" Method to get if the dongle is connected to an internet connection """
		result = self.get_connection_status()
		if result[0] == "901": #901 => connected, 902 => disconnected, 900 => connecting
			return True
		else:
			return False
				
		
	def get_device_autorun_version(self):
		""" Method to get device autorun version """
		result = self.send_request("/api/device/autorun-version","",None)
		return result

	def get_device_basic_information(self):
		""" Method to get device basic_information """
		result = self.send_request("/api/device/basic_information","",None)
		return result

	def get_device_device_feature_switch(self):
		""" Method to get device device feature switch """
		result = self.send_request("/api/device/device-feature-switch","",None)
		return result

	#def get_device_information(self):
	#	""" Method to get device information """
	#	result = self.send_request("/api/device/information","",None)
	#	return result

	def get_device_signal(self):
		""" Method to get device signal """
		result = self.send_request("/api/device/signal","",None)
		return result

	def get_dhcp_settings(self):
		""" Method to get dhcp settings """
		result = self.send_request("/api/dhcp/settings","",None)
		return result

	def get_dialup_connection(self):
		""" Method to get dialup connection """
		result = self.send_request("/api/dialup/connection","",None)
		return result

	def get_dialup_dialup_feature_switch(self):
		""" Method to get dialup dialup feature switch """
		result = self.send_request("/api/dialup/dialup-feature-switch","",None)
		return result

	def get_dialup_mobile_dataswitch(self):
		""" Method to get dialup mobile dataswitch """
		result = self.send_request("/api/dialup/mobile-dataswitch","",None)
		return result

	def get_dialup_profiles(self):
		""" Method to get dialup profiles """
		result = self.send_request("/api/dialup/profiles","",None)
		return result

	def get_global_module_switch(self):
		""" Method to get global module switch """
		result = self.send_request("/api/global/module-switch","",None)
		return result

	def get_language_current_language(self):
		""" Method to get language current language """
		result = self.send_request("/api/language/current-language","",None)
		return result

	#def get_monitoring_check_notifications(self):
	#	""" Method to get monitoring check notifications """
	#	result = self.send_request("/api/monitoring/check-notifications","",None)
	#	return result

	def get_monitoring_converged_status(self):
		""" Method to get monitoring converged status """
		result = self.send_request("/api/monitoring/converged-status","",None)
		return result

	def get_monitoring_month_statistics(self):
		""" Method to get monitoring month_statistics """
		result = self.send_request("/api/monitoring/month_statistics","",None)
		return result

	def get_monitoring_start_date(self):
		""" Method to get monitoring start_date """
		result = self.send_request("/api/monitoring/start_date","",None)
		return result

	#def get_monitoring_status(self):
	#	""" Method to get monitoring status """
	#	result = self.send_request("/api/monitoring/status","",None)
	#	return result

	def get_monitoring_traffic_statistics(self):
		""" Method to get monitoring traffic statistics """
		result = self.send_request("/api/monitoring/traffic-statistics","",None)
		return result

	#def get_net_current_plmn(self):
	#	""" Method to get net current plmn """
	#	result = self.send_request("/api/net/current-plmn","",None)
	#	return result

	def get_net_net_feature_switch(self):
		""" Method to get net net feature switch """
		result = self.send_request("/api/net/net-feature-switch","",None)
		return result

	def get_net_net_mode(self):
		""" Method to get net net mode """
		result = self.send_request("/api/net/net-mode","",None)
		return result

	def get_net_net_mode_list(self):
		""" Method to get net net mode list """
		result = self.send_request("/api/net/net-mode-list","",None)
		return result

	def get_net_network(self):
		""" Method to get net network """
		result = self.send_request("/api/net/network","",None)
		return result

	def get_net_plmn_list(self):
		""" Method to get net plmn list """
		result = self.send_request("/api/net/plmn-list","",None)
		return result

	def get_net_register(self):
		""" Method to get net register """
		result = self.send_request("/api/net/register","",None)
		return result

	def get_online_update_cancel_downloading(self):
		""" Method to get online update cancel downloading """
		result = self.send_request("/api/online-update/cancel-downloading","",None)
		return result

	def get_online_update_check_new_version(self):
		""" Method to get online update check new version """
		result = self.send_request("/api/online-update/check-new-version","",None)
		return result

	def get_online_update_status(self):
		""" Method to get online update status """
		result = self.send_request("/api/online-update/status","",None)
		return result

	def get_online_update_upgrade_messagebox(self):
		""" Method to get online update upgrade messagebox """
		result = self.send_request("/api/online-update/upgrade-messagebox","",None)
		return result

	def get_pin_simlock(self):
		""" Method to get pin simlock """
		result = self.send_request("/api/pin/simlock","",None)
		return result

	def get_pin_status(self):
		""" Method to get pin status """
		result = self.send_request("/api/pin/status","",None)
		return result

	def get_redirection_homepage(self):
		""" Method to get redirection homepage """
		result = self.send_request("/api/redirection/homepage","",None)
		return result

	def get_security_dmz(self):
		""" Method to get security dmz """
		result = self.send_request("/api/security/dmz","",None)
		return result

	def get_security_firewall_switch(self):
		""" Method to get security firewall switch """
		result = self.send_request("/api/security/firewall-switch","",None)
		return result

	def get_security_lan_ip_filter(self):
		""" Method to get security lan ip filter """
		result = self.send_request("/api/security/lan-ip-filter","",None)
		return result

	def get_security_nat(self):
		""" Method to get security nat """
		result = self.send_request("/api/security/nat","",None)
		return result

	def get_security_sip(self):
		""" Method to get security sip """
		result = self.send_request("/api/security/sip","",None)
		return result

	def get_security_special_applications(self):
		""" Method to get security special applications """
		result = self.send_request("/api/security/special-applications","",None)
		return result

	def get_security_upnp(self):
		""" Method to get security upnp """
		result = self.send_request("/api/security/upnp","",None)
		return result

	def get_security_virtual_servers(self):
		""" Method to get security virtual servers """
		result = self.send_request("/api/security/virtual-servers","",None)
		return result

	def get_sms_backup_sim(self):
		""" Method to get sms backup sim """
		result = self.send_request("/api/sms/backup-sim","",None)
		return result

	def get_sms_config(self):
		""" Method to get sms config """
		result = self.send_request("/api/sms/config","",None)
		return result

	def get_sms_send_status(self):
		""" Method to get sms send status """
		result = self.send_request("/api/sms/send-status","",None)
		return result

	#def get_sms_sms_count(self):
	#	""" Method to get sms sms count """
	#	result = self.send_request("/api/sms/sms-count","",None)
	#	return result

	def get_sms_sms_feature_switch(self):
		""" Method to get sms sms feature switch """
		result = self.send_request("/api/sms/sms-feature-switch","",None)
		return result

	def get_sms_splitinfo_sms(self):
		""" Method to get sms splitinfo sms """
		result = self.send_request("/api/sms/splitinfo-sms","",None)
		return result

	def get_sntp_sntpswitch(self):
		""" Method to get sntp sntpswitch """
		result = self.send_request("/api/sntp/sntpswitch","",None)
		return result
		
#a  = Huawei()
#print a.connect()
#print a.disconnect()
#print a.get_device_information()
#print a.get_network_information()
#print a.check_notifications()
#print a.get_connection_status()

#print a.set_connection_settings(1,1,,1,0,0)
#print a.send_message("-1","07507251356","test","2012-11-05 21:00:00")

#print a.get_sms_list()
#print a.delete_sms(20005)
