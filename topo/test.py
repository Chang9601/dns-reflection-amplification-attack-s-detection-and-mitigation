#!/usr/bin/python

############################################################################
##
##     This file is part of Purdue CS 422.
##
##     Purdue CS 422 is free software: you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.
##
##     Purdue CS 422 is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.
##
##     You should have received a copy of the GNU General Public License
##     along with Purdue CS 422. If not, see <https://www.gnu.org/licenses/>.
##
#############################################################################

from mininet.topo import Topo


class TestTopo(Topo):
    """Test topology"""

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

        self.addSwitch('m1')  # grpc: 50001
        self.addSwitch('s1')  # grpc: 50002

        self.addHost('h1', ip="10.0.0.1", mac="00:00:00:00:00:01")
        self.addHost('h2', ip="10.0.0.2", mac="00:00:00:00:00:02")
        self.addHost('h3', ip="10.0.0.3", mac="00:00:00:00:00:03")
        self.addHost('h4', ip="10.0.0.4", mac="00:00:00:00:00:04")

        self.addLink('s1', 'h1')
        self.addLink('s1', 'h2')
        self.addLink('s1', 'h3')
        self.addLink('s1', 'h4')
        self.addLink('s1', 'm1')


topos = {'testtopo': (lambda: TestTopo())}

