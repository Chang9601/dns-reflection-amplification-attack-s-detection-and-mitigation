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

import sys
from subprocess import call
from time import sleep


def SendDnsQuery(dns_srv, sleep_time):
    sleep(5)

    try:
        while True:
            call(["dig", "@%s" % dns_srv, "ANY", "cs422.net"])
            sleep(sleep_time)
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python legit_dns_traffic.py dns_srv_ip sleep_time")
        sys.exit(0)
    SendDnsQuery(sys.argv[1], float(sys.argv[2]))
