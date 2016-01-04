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

class Endpoint:

	def __init__(self, config_fn)
	
		self.__config_fn = config_fn
		self.__conn = None
		
	def __connection(self, work):
	
		if self.__conn is None:
			config = self.__config_fn(work)
			host = config["host"]
			port = config["port"]
			self.__conn = http.client.HTTPConnection(host, port)
		return self.__conn
		
class ImageBuilder:

	def __init__(self, endpoint_config_fn):
	
		self.__endpoint = Endpoint(endpoint_config_fn)
		
	def build(self, work, image):
	
		pass
		
class ImageRepository:

	def __init__(self, endpoint_config_fn):
	
		self.__endpoint = Endpoint(endpoint_config_fn)
		
	def publish(self, work, image_ref):
	
		pass
		
class ContainerRunner:

	def __init__(self, endpoint_config_fn):
	
		self.__endpoint = Endpoint(endpoint_config_fn)
		
	def run(self, work, cont):
	
		pass

