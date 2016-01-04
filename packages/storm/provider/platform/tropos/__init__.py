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

from storm.provider.platform.tropos.vmm import vbox
from storm.provider.platform.tropos.cm import docker

class Platform:

	def __init__(self, base_res, props):
	
		self.__builder = docker.ImageBuilder(
			self.__builder_endpoint_config_fn
		)
		self.__repository = docker.ImageRepository(
			self.__repository_endpoint_config_fn
		)
		self.__executor = ContainerExecutor(
			self.__executor_endpoint_config_list_fn
		)
		
	def __endpoint_props(self, host, port):
	
		return {
			"host": host,
			"port": port
		}
		
	def __builder_endpoint_config_fn(self, work):
	
		return None
		
	def __repository_endpoint_config_fn(self, work):
	
		return None
		
	def __executor_endpoint_config_list_fn(self, work):
	
		return None
		
	def builder(self):
	
		return self.__builder
		
	def repository(self):
	
		return self.__repository
		
	def executor(self):
	
		return self.__executor
		
	def destroy(self, context):
	
		pass
		
class ContainerExecutor:

	def __init__(self, endpoint_config_list_fn)
	
		self.__endpoint_config_list_fn = endpoint_config_list_fn
		
	def __runners(self, work):
	
		return [
			docker.ContainerRunner(lambda work: config)
			for config in self.__endpoint_config_list_fn(work)
		]
		
	def execute(self, work, cont, config):
	
		pass

