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

from storm.module import util

def up(vagrant_res):

	util.call(
		vagrant_res.path,
		[
			"vagrant", 
			"up"
		],
		"Could not run platform with vagrant"
	)
	
def destroy(vagrant_res):

	util.call(
		vagrant_res.path,
		[
			"vagrant", 
			"destroy",
			"-f"
		],
		"Could not destroy vagrant virtual machines"
	)
	
def box_remove(box_name):

	util.call(
		None,
		[
			"vagrant", 
			"box",
			"remove",
			box_name
		],
		"Could not destroy vagrant virtual machines"
	)

