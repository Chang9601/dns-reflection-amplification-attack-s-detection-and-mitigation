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
from time import sleep

import random
from scapy.all import *


def SendDnsQuery(src_ip, dns_srv, sleep_time):
    random.seed()
    sleep(5)

    try:
        while True:
            qid = random.randint(0, 2 ** 16 - 1)
            p = (IP(src=src_ip, dst=dns_srv) / UDP(sport=random.randint(1025, 2 ** 16 - 1)) / DNS(id=qid, rd=0,
                                                                                                  qd=DNSQR(qtype="ANY",
                                                                                                           qname="cs422.net")))
            send(p)
            sleep(sleep_time)
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_dns_query.py src_ip dns_srv_ip sleep_time")
        sys.exit(0)

    SendDnsQuery(sys.argv[1], sys.argv[2], float(sys.argv[3]))
