#!/usr/bin/env python

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

import threading
from collections import defaultdict

from scapy.all import *
from utils.rest import install_rule, delete_rule, install_group

dns_port = 53

class PacketHandler:

    def __init__(self, intf, mac_map, ip_map):
        self.intf = intf
        self.mac_map = mac_map
        self.ip_map = ip_map
        # TODO: Create and initialize additional instance variables
        #       for detection and mitigation
        # add code here ...

        self.threshold = 50 # Threshold value
        self.counter = {} # Keep track of the total number of unmatched responses sent to each host, up to 50
        self.id_ip = {} # Map a request's DNS identification number to its source IP

    def start(self):
        t = threading.Thread(target=self._sniff, args=(self.intf,))
        t.start()

    def incoming(self, pkt, intf):
        macs = self.mac_map[intf]

        res = (pkt[Ether].src in macs or
               pkt[Ether].dst in macs)
        return res

    def handle_packet(self, pkt):
        # TODO: process the packet and install flow rules to perform DNS reflection
        #       attack detection and mitigation
        # add code here ...

        # Check whether pkt is an DNS packet
        if DNS in pkt:

            # Check if it is a request or a response
            is_request = pkt[DNS].qr == 0
            is_response = pkt[DNS].qr == 1

            dns_id = pkt[DNS].id

            # Reflection Attack Detection
            if is_request == True:
                # Record a mapping from the request's DNS identification number to its source IP
                src_ip = pkt[IP].src
                self.id_ip[dns_id] = src_ip

                #print("Req: src_ip={0}, dns_id={1}".format(src_ip, dns_id))
            
            if is_response == True:
                dst_ip = pkt[IP].dst

                # Check if there has been a request with the same identification number from the destination IP of the response
                # If not, increase the counter of unmatched responses sent to each host
                if dst_ip not in self.counter:
                    self.counter[dst_ip] = 0

                if dns_id not in self.id_ip:
                    self.counter[dst_ip] = self.counter[dst_ip] + 1
                    
                    # Reflection Attack Mitigation
                    # If the counter of any host passes the threshold (50), install a flow rule to drop all DNS responses headed for the victim host 
                    if self.counter[dst_ip] > self.threshold:
                        install_rule(table="forward",
                                     ipv4_dst=dst_ip,
                                     l4_src=dns_port)
                    # However, if it is a legitimate response, delete a flow rlue to allow legitimate responses to pass through
                else:
                    delete_rule(table="forward",
                                ipv4_dst=dst_ip,
                                l4_src=dns_port)

                #print("Res: dst_ip={0}, dns_id={1} counter={2}".format(dst_ip, dns_id, self.counter[dst_ip] if self.counter.get(dst_ip) != None else 0))

    def _sniff(self, intf):
        sniff(iface=intf, prn=lambda x: self.handle_packet(x),
              lfilter=lambda x: self.incoming(x, intf))


if __name__ == "__main__":
    # TODO: Install flow rules to clone DNS packets from the switch to the monitor
    # add code here ...

    intf = "m1-eth1"
    mac_map = {intf: ["00:00:00:00:00:02", "00:00:00:00:00:03"]}
    ip_map = {intf: ["10.0.0.2", "10.0.0.3"]}

    # Flow Rule = Match-Action pair
    # DNS request's dest port must be dns_port as it is sent to DNS server
    # DNS response's src port must be dns_port as it is sent from DNS server
    # See Wireshark DNS page and Scapy documentation
    install_rule(table="monitor",
                 ipv4_src=ip_map[intf][0],
                 l4_dst=dns_port,
                 monitor=True)
    
    install_rule(table="monitor",
                 ipv4_dst=ip_map[intf][0],
                 l4_src=dns_port,
                 monitor=True)

    install_rule(table="monitor",
                 ipv4_src=ip_map[intf][1],
                 l4_dst=dns_port,
                 monitor=True)

    install_rule(table="monitor",
                 ipv4_dst=ip_map[intf][1],
                 l4_src=dns_port,
                 monitor=True)
    handler = PacketHandler(intf, mac_map, ip_map)
    handler.start()
