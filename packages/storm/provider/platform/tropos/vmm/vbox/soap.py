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

import http.client
import io
import xml

NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_XSD = "http://www.w3.org/2001/XMLSchema"
NS_SOAPENV = "http://schemas.xmlsoap.org/soap/envelope/"

class SOAPReader:

	def __init__(self, ns_dict, body):
	
		self.__ns_dict = ns_dict
		self.__body = body
		
	def __iter__(self):
	
		yield from self.__body
		
	def ns_prefix(self, ns):
	
		return self.__ns_dict[ns]
		
class SOAPWriter:

	def __init__(self, ns_dict, envelope, body, close_fn):
	
		self.__ns_dict = ns_dict
		self.__envelope = envelope
		self.__body = body
		self.__close_fn = close_fn
		
	def call(self, name, ns=None):
	
		return self.__body.element(xml.QName(
			name,
			None if ns is None else self.__ns_dict[ns]
		))
		
	def close(self):
	
		self.__body.close()
		self.__envelope.close()
		self.__close_fn()
		
class Client:

	def __init__(self, host, port, url):
	
		self.__conn = http.client.HTTPConnection(host, port)
		self.__url = url
		self.__out = None
			
	def __close_writer(self):
	
		self.__out.write("\n")
		self.__conn.request("POST", self.__url, self.__out.getvalue())
		
	def __ns_dict(self, elem):
	
		ns_dict = {}
		for attr in elem.attributes():
			name = attr.name
			if name.prefix is None and name.local_name == "xmlns":
				ns_dict[attr.value] = None
			elif name.prefix == "xmlns":
				ns_dict[attr.value] = name.local_name
		return ns_dict
		
	def __read_envelope(self, ns_dict, envelope):
	
		header_read = False
		prefix_soapenv = ns_dict[NS_SOAPENV]
		
		for reader in envelope:
			if reader.is_text():
				reader.ignore()
			elif reader.is_element():
				name = reader.name()
				if xml.QName("Header", prefix_soapenv) == name:
					if header_read:
						raise Exception("SOAP header already processed")
					else:
						header_read = True
						reader.ignore()
				elif xml.QName("Body", prefix_soapenv) == name:
					ns_dict.update(self.__ns_dict(reader))
					yield SOAPReader(ns_dict, reader)
				else:
					msg = "Invalid SOAP envelope element '{}'".format(name)
					raise Exception(msg)
			else:
				raise Exception("Invalid SOAP envelope node")
				
	def read(self):
	
		resp = self.__conn.getresponse()
		
		prolog_read = False
		envelope = None
		
		for reader in xml.FragmentReader(resp):
			if reader.is_text():
				reader.ignore()
			elif reader.is_proc_instr():
				name = reader.name()
				name_without_prefix = name.prefix is None
				name_xml = name.local_name.lower() == "xml"
				if prolog_read and name_without_prefix and name_xml:
					raise Exception("Prolog already processed")
				prolog_read = True
				reader.ignore()
			elif reader.is_element():
				name = reader.name()
				ns_dict = self.__ns_dict(reader)
				if xml.QName("Envelope", ns_dict[NS_SOAPENV]) == name:
					if envelope is not None:
						raise Exception("SOAP envelope already processed")
					envelope = reader
					yield from self.__read_envelope(ns_dict, envelope)
				else:
					raise Exception("Invalid SOAP element '{}'".format(name))
			else:
				raise Exception("Invalid SOAP node")
				
	def write(self, *ns_args):
	
		SOAPENV_PREFIX = "soapenv"
		
		self.__out = io.StringIO()
		
		ns_dict = {
			ns: "ns{}".format(index + 1)
			for index, ns in enumerate(ns_args)
		}
		ns_dict[NS_SOAPENV] = SOAPENV_PREFIX
		
		doc = xml.FragmentWriter(self.__out)
		prolog = doc.processing_instruction(xml.QName("xml"))
		prolog.append(str(xml.Attribute(xml.QName("version"), "1.0")))
		prolog.append(" ")
		prolog.append(str(xml.Attribute(xml.QName("encoding"), "UTF-8")))
		prolog.close()
		nl = doc.text()
		nl.append("\n")
		envelope = doc.element(
			xml.QName("Envelope", SOAPENV_PREFIX),
			(
				xml.Attribute(xml.QName(ns_prefix, "xmlns"), ns)
				for ns, ns_prefix in ns_dict.items()
			)
		)
		header = envelope.element(
			xml.QName("Header", SOAPENV_PREFIX)
		)
		header.close()
		body = envelope.element(
			xml.QName("Body", SOAPENV_PREFIX)
		)
		
		return SOAPWriter(
			ns_dict,
			envelope,
			body,
			self.__close_writer
		)
		
	def close(self):
	
		self.__conn.close()

