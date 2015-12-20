#
# This file is part of STORM.
#
# STORM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# STORM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STORM.  If not, see <http://www.gnu.org/licenses/>.
#

import io
import json
import os
import tarfile
import urllib

class Endpoint:

	def __init__(self, host, port):
	
		self.__http = httplib2.Http()
		self.__endpoint = "http://{}:{}".format(host, port)
		
	def __ref_str(self, ref):
	
		if ref.version is None:
			return "{}:latest".format(ref.name)
		else:
			return "{}:{}".format(ref.name, ref.version)
			
	def __request(self, method, uri, message):
	
		headers = {}
		if isinstance(message, (list, dict)):
			headers["Content-Type"] = "application/json"
			body = json.dumps(message)
		else:
			body = message
		resp, resp_body = self.__http.request(
			"{}{}".format(self.__endpoint, uri),
			method,
			headers=headers,
			body=body
		)
		return (resp, resp_body.decode("UTF-8"))
		
	def __request_post(self, uri, message=None):
		
		return self.__request("POST", uri, message)
		
	def __command_repr(self, cmd):
	
		return cmd
		
	def build_file(self, image, image_file):
	
		tarf = tarfile.open(name=None, mode="w", fileobj=image_file)
		docker_file = io.StringIO()
		
		if image.extends is not None:
			ext_str = self.__ref_str(image.extends)
			docker_file.write("FROM {}\n".format(ext_str))
			
		for res in image.definition.resources:
			docker_file.write("ADD {}\n".format([ res.target, res.target ]))
			source_file = res.source_res.open("rb")
			if len(res.properties) > 0:
				# If there is properties, there is need of processing 
				target_file = io.StringIO()
				util.resolve(source_file, target_file, res.properties)
				target_file = io.BytesIO(target_file.read().encode("UTF-8"))
			else:
				# If not, there is not up date at all
				target_file = source_file
			info = tarfile.TarInfo(name=res.target)
			target_file.seek(0, os.SEEK_END)
			info.size = target_file.tell()
			target_file.seek(0)
			tarf.addfile(info, target_file)
			
			source_file.close()
			target_file.close()
			
		for pr in image.definition.provision:
			docker_file.write("RUN {}\n".format(pr.args))
		for ex in image.definition.execution:
			docker_file.write("CMD {}\n".format(ex.args))
			
		info = tarfile.TarInfo(name="Dockerfile")
		docker_file.seek(0, os.SEEK_END)
		info.size = docker_file.tell()
		docker_file.seek(0)
		docker_file = io.BytesIO(docker_file.read().encode("UTF-8"))
		tarf.addfile(info, docker_file)
		docker_file.close()
		
		tarf.close()
		image_file.seek(0)
		
	def build(self, image, image_file):
	
		quoted_ref = urllib.parse.quote(self.__ref_str(image.ref))
		uri = "/build?t={}".format(quoted_ref)
		resp, resp_body = self.__request_post(uri, image_file.read())
		
		if resp.status != 200:
			msg = "Could not build Docker image: {}".format(body)
			raise Exception(msg)
			
class RegistryEndpoint:

	def __init__(self, host, port):
	
		self.__http = httplib2.Http()
		self.__endpoint = "http://{}:{}".format(host, port)

