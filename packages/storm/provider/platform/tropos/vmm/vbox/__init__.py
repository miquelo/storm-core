#
# This file is part of STORM-CORE.
#
# STORM-CORE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# STORM-CORE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STORM-CORE.  If not, see <http://www.gnu.org/licenses/>.
#

# Fer peticions SOAP directament. Anàlisi amb SoapUI.
#
# useradd -m vbox -G vboxusers
# passwd vbox
# su - vbox -c vboxwebsrv

import io
import soap
import xml

NS_VIRTUALBOX = "http://www.virtualbox.org/"

class VirtualMachineManager:

	def __init__(self, props):
	
		host = props["host"]
		port = props["port"]
		username = props["username"]
		password = props["password"]
		self.__client = soap.Client(host, port, "/")
		self.__ref = self.__logon(username, password)
		
	def __read_result(self, op_name):
	
		for reader in self.__client.read():
			vbox_prefix = reader.ns_prefix(NS_VIRTUALBOX)
			for result in reader:
				if result.is_element():
					name = result.name()
					if xml.QName(op_name, vbox_prefix) == name:
						yield from result
					else:
						raise Exception("Invalid result message")
				elif result.is_text():
					result.ignore()
				else:
					raise Exception("Invalid result node")
					
	def __read_returnval(self, op_name):
	
		for reader in self.__read_result(op_name):
			if reader.is_text():
				reader.ignore()
			elif reader.is_element():
				name = reader.name()
				if xml.QName("returnval") != name:
					raise Exception("Unexpected element '{}'".format(name))
				yield from reader
			else:
				raise Exception("Invalid return node")
				
	def __logon(self, username, password):
	
		writer = self.__client.write(NS_VIRTUALBOX)
		call = writer.call("IWebsessionManager_logon", NS_VIRTUALBOX)
		
		elem = call.element("username")
		text = elem.text()
		text.append(username)
		elem.close()
		
		elem = call.element("password")
		text = elem.text()
		text.append(password)
		elem.close()
		
		call.close()
		writer.close()
		
		retval = io.StringIO()
		op_name = "IWebsessionManager_logonResponse"
		for reader in self.__read_returnval(op_name):
			if reader.is_text():
				for c in reader:
					retval.write(c)
			else:
				raise Exception("Invalid return value node")
		return retval.getvalue()
		
	def __logoff(self):
	
		writer = self.__client.write(NS_VIRTUALBOX)
		call = writer.call("IWebsessionManager_logoff", NS_VIRTUALBOX)
		
		elem = call.element("refIVirtualBox")
		text = elem.text()
		text.append(self.__ref)
		elem.close()
		
		call.close()
		writer.close()
		
		retval = io.StringIO()
		op_name = "IWebsessionManager_logoffResponse"
		for reader in self.__read_result(op_name):
			raise Exception("Invalid result value node")
				
	def close(self):
	
		self.__logoff()
		self.__client.close()
		
vmm = VirtualMachineManager({
	"host": "localhost",
	"port": "18083",
	"username": "vbox",
	"password": "12345678"
})
vmm.close()

