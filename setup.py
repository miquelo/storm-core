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

from setuptools import setup, find_packages

setup(
	name="storm-core",
	version="0.1.0",
	
	author="STORM Team",
	author_email="miquel.ferran.gonzalez@gmail.com",
	
	packages=find_packages("packages"),
	namespace_packages=[
		"storm",
		"storm.application",
		"storm.provider",
		"storm.provider.platform",
		"storm.provider.resource"
	],
	package_dir={
		"": "packages"
	},
	install_requires={
		"storm": [
			"storm>=0.1.0"
		]
	},
	extras_require={
		"shell-color": [
			"colorama>=0.3.3"
		],
		"gtk": [
			"gi>=3.0"
		]
	},
	
	entry_points={
		"console_scripts": [
			"storm=storm.application.shell:main"
		],
		"gui_scripts": [
			"storm-gtk=storm.application.gtk:main"
		]
	},
	url="http://pypi.python.org/pypi/storm_core_0.1.0/",
	
	license="LICENSE.txt",
	description="STORM core applications and providers.",
	long_description=open("README.md").read()
)

