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

from storm.module import resource
from storm.module import util

from storm.provider.platform.devel import docker
from storm.provider.platform.devel import packer
from storm.provider.platform.devel import vagrant

import io
import os.path
import sys
import tempfile

class Platform:

	def __init__(self, data_res, props):
	
		self.__data_res = data_res
		self.__props = props
		
	def __docker_endpoint(self):
	
		return docker.Endpoint(
			self.__props["support_ip"],
			self.__props["docker_port"]
		)
		
	def __docker_registry_endpoint(self):
	
		return docker.RegistryEndpoint(
			self.__props["support_ip"],
			self.__props["docker_registry_port"]
		)
		
	def __running(self):
	
		vagrant.up(self.__resource_group_res("vagrant"))
		
	def __resource_group_res(self, name):
	
		return self.__data_res.ref(name)
		
	def __resource_build(self, resource_group_name, path, config_vars):
	
		source_res = resource.ref(os.path.abspath(__file__))
		source_res = source_res.parent().ref("resources")
		source_res = source_res.ref(resource_group_name)
		source_res = source_res.ref("{}.in".format(path))
		
		target_res = self.__resource_group_res(resource_group_name)
		target_res = target_res.ref(path)
		
		source_file = source_res.open("r")
		target_file = target_res.open("w")
		util.resolve(source_file, target_file, config_vars)
		source_file.close()
		target_file.close()
		
	def configure(self, context, props):
	
		pass
		
	def destroy(self, context):
	
		pass
		
	def configure_old(self):
	
		packer_res = self.__resource_group_res("packer")
		docker_res = self.__resource_group_res("docker")
		
		p_props = {
			"packer_dir": packer_res.path,
			"docker_dir": docker_res.path,
			"box_name": "storm/debian",
			"debian_iso_checksum": "{}{}{}{}".format(
				"923cd1bfbfa62d78aecaa92d919ee54a",
				"95c8fca834b427502847228cf06155e7",
				"243875f59279b0bf6bfd1b579cbe2f1b",
				"c80528a265dafddee9a9d2a197ef3806"
			),
			"debian_iso_checksum_type": "sha512",
			"debian_version": "8.2.0",
			"admin_user": "vagrant",
			"domain_ns": "ns.#{domain}",
			"domain_docker": "docker.#{domain}",
			"docker_port": "4243",
			"docker_registry_port": "5000",
			"project": "storm",
			"registry_cert": {
				"country": "ES",
				"locality": "Barcelona",
				"organization": "STORM Team"
			}
		}
		r_props = {}
		util.merge_dict(r_props, self.__props)
		plat_props = util.resolvable(plat_props, plat_props)
		self.__box_name = plat_props["box_name"]
		
		debian_version = plat_props["debian_version"]
		
		box_file_name = "debian-{}-amd64_virtualbox.box".format(debian_version)
		box_res = packer_res.ref(box_file_name)
		if not box_res.exists():
			resources = {
				"packer": [
					"http/preseed.cfg",
					"script/cleanup.sh",
					"script/docker.sh",
					"script/networking.sh",
					"script/sshd.sh",
					"script/sudoers.sh",
					"script/update.sh",
					"script/vagrant.sh",
					"script/vbaddguest.sh",
					"image.json"
				]
			}
			for res_group_name in sorted(resources):
				for path in sorted(resources[res_group_name]):
					self.__resource_build(res_group_name, path, plat_props)
					
			packer_res.ref("output-virtualbox-iso").delete()
			packer.build(packer_res.ref("image.json"))
			
		resources = {
			"vagrant": [
				"ddns.sh",
				"disco.sh",
				"domainup.sh",
				"fix-stdin.sh",
				"registry.sh",
				"trust-registry.sh",
				"Vagrantfile"
			],
			"docker": [
				"ddns/bind/named.conf",
				"ddns/bind/named.conf.local",
				"ddns/bind/named.conf.log",
				"ddns/bind/zones.conf",
				"ddns/web/domain.php",
				"ddns/web/index.php",
				"ddns/web/site.conf",
				"ddns/install.sh",
				"ddns/Dockerfile",
				"disco/Dockerfile"
			]
		}
		for res_group_name in sorted(resources):
			for path in sorted(resources[res_group_name]):
				self.__resource_build(res_group_name, path, plat_props)
				
	def destroy_old(self):
	
		vagrant.destroy(self.__resource_group_res("vagrant"))
		vagrant.box_remove(self.__box_name)
		self.__data_res.delete()
		
	def build(self, image):
	
		dep = self.__docker_endpoint()
		
		image_file = tempfile.NamedTemporaryFile(suffix=".tar")
		dep.build_file(image, image_file)
		
		self.__running()
		dep.build(image, image_file)
		
		image_file.close()
		
	def publish(self, image):
	
		# self.__running()
		pass
		
	def delete(self, image):
	
		# self.__running()
		pass
		
class DestroyTask:

	def __init__(self):
	
		pass
		
	def run(self, context):
	
		pass
		
	def cancel(self):
	
		pass

