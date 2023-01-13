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

import argparse
import binascii
import json
import socket

import requests

AUTH = ('onos', 'rocks')

DEVICE_ID = "device:s1"
DEFAULT_PRIORITY = 40
DEFAULT_TABLE = "IngressPipeImpl.forward_control.forward_table"

RESTFUL_BASE_URL = "http://127.0.0.1:8181/onos/v1"
RESTFUL_GETPOST_FLOW_URL = RESTFUL_BASE_URL + "/flows"
RESTFUL_GETPOST_GROUP_URL = RESTFUL_BASE_URL + "/groups"


def set_device_id(id):
    global DEVICE_ID
    DEVICE_ID += id


def install_rule(table=DEFAULT_TABLE,
                 priority=DEFAULT_PRIORITY,
                 timeout=1,
                 is_permanent=False,
                 ingress_port=None,
                 egress_port=None,
                 eth_dst=None,
                 eth_src=None,
                 eth_type=None,
                 ipv4_src=None,
                 ipv4_dst=None,
                 ipv4_proto=None,
                 l4_src=None,
                 l4_dst=None,
                 dns_id=None,
                 output=None,
                 monitor=None,
                 noop=None):
    TABLE_ID = DEFAULT_TABLE
    if table == "forward":
        TABLE_ID = "IngressPipeImpl.forward_control.forward_table"
    elif table == "monitor":
        TABLE_ID = "IngressPipeImpl.monitor_control.monitor_table"

    matches_list = []
    if ingress_port:
        matches_list += [{
            "field": "standard_metadata.ingress_port",
            "match": "ternary",
            "value": "{:02x}".format(ingress_port),
            "mask": "ff"
        }]
    if egress_port:
        matches_list += [{
            "field": "standard_metadata.egress_port",
            "match": "ternary",
            "value": "{:02x}".format(egress_port),
            "mask": "ff"
        }]
    if eth_dst:
        matches_list += [{
            "field": "hdr.ethernet.dst_addr",
            "match": "ternary",
            "value": eth_dst.translate({ord(':'): None}).lower(),
            "mask": "ffffffffffff"
        }]
    if eth_src:
        matches_list += [{
            "field": "hdr.ethernet.src_addr",
            "match": "ternary",
            "value": eth_src.translate({ord(':'): None}).lower(),
            "mask": "ffffffffffff"
        }]
    if eth_type:
        matches_list += [{
            "field": "hdr.ethernet.ether_type",
            "match": "ternary",
            "value": "{:04x}".format(eth_type),
            "mask": "ffff"
        }]
    if ipv4_dst:
        matches_list += [{
            "field": "hdr.ipv4.dst_addr",
            "match": "ternary",
            "value": str(binascii.b2a_hex(socket.inet_aton(ipv4_dst))),
            "mask": "ffffffff"
        }]
    if ipv4_src:
        matches_list += [{
            "field": "hdr.ipv4.src_addr",
            "match": "ternary",
            "value": str(binascii.b2a_hex(socket.inet_aton(ipv4_src))),
            "mask": "ffffffff"
        }]
    if ipv4_proto:
        matches_list += [{
            "field": "local_metadata.ip_proto",
            "match": "ternary",
            "value": "{:02x}".format(ipv4_proto),
            "mask": "ff"
        }]
    if l4_src:
        matches_list += [{
            "field": "local_metadata.l4_src_port",
            "match": "ternary",
            "value": "{:04x}".format(l4_src),
            "mask": "ffff"
        }]
    if l4_dst:
        matches_list += [{
            "field": "local_metadata.l4_dst_port",
            "match": "ternary",
            "value": "{:04x}".format(l4_dst),
            "mask": "ffff"
        }]
    if dns_id:
        matches_list += [{
            "field": "local_metadata.dns_id",
            "match": "ternary",
            "value": "{:04x}".format(dns_id),
            "mask": "ffff"
        }]

    instructions_list = []

    if table == "forward":
        if output:
            instructions_list += [{
                "type": "PROTOCOL_INDEPENDENT",
                "subtype": "ACTION",
                "actionId": "IngressPipeImpl.forward_control.set_output_port",
                "actionParams": {
                    "port_num": format(output, 'x')
                }
            }]
        elif noop:
            instructions_list += [{
                "type": "PROTOCOL_INDEPENDENT",
                "subtype": "ACTION",
                "actionId": "IngressPipeImpl.forward_control.noop",
                "actionParams": { }
            }]
        else:
            instructions_list += [{
                "type": "PROTOCOL_INDEPENDENT",
                "subtype": "ACTION",
                "actionId": "IngressPipeImpl.forward_control.drop",
                "actionParams": {}
            }]
    elif table == "monitor":
        if monitor:
            instructions_list += [{
                "type": "PROTOCOL_INDEPENDENT",
                "subtype": "ACTION",
                "actionId": "IngressPipeImpl.monitor_control.clone_packet",
                "actionParams": {}
            }]
        elif noop:
            instructions_list += [{
                "type": "PROTOCOL_INDEPENDENT",
                "subtype": "ACTION",
                "actionId": "IngressPipeImpl.monitor_control.noop",
                "actionParams": {}
            }]
        else:
            instructions_list += [{
                "type": "PROTOCOL_INDEPENDENT",
                "subtype": "ACTION",
                "actionId": "IngressPipeImpl.monitor_control.drop",
                "actionParams": {}
            }]
    else:
        pass  # install NoAction

    if is_permanent:
        is_permanent = "true"
    else:
        is_permanent = "false"

    json_data = {
        "priority": priority,
        "timeout": timeout,
        "isPermanent": is_permanent,
        "deviceId": DEVICE_ID,
        "tableId": TABLE_ID,
        "treatment": {
            "instructions": instructions_list
        },
        "selector": {
            "criteria": [
                {
                    "type": "PROTOCOL_INDEPENDENT",
                    "matches": matches_list
                }
            ]
        }
    }

    # print(json_data)
    response = requests.post(RESTFUL_GETPOST_FLOW_URL + "/" + DEVICE_ID, data=json.dumps(json_data), auth=AUTH)
    print("Install Rule: Response is: {0}".format(response))


def get_flow_id(table=DEFAULT_TABLE,
                ingress_port=None,
                egress_port=None,
                eth_dst=None,
                eth_src=None,
                eth_type=None,
                ipv4_src=None,
                ipv4_dst=None,
                ipv4_proto=None,
                l4_src=None,
                l4_dst=None,
                dns_id=None):
    response = requests.get(RESTFUL_GETPOST_FLOW_URL, auth=AUTH)
    response_json = response.json()
    flows = response_json["flows"]

    TABLE_ID = DEFAULT_TABLE
    if table == "forward":
        TABLE_ID = "IngressPipeImpl.forward_control.forward_table"
    elif table == "monitor":
        TABLE_ID = "IngressPipeImpl.monitor_control.monitor_table"

    matches_dict = dict()
    if ingress_port:
        matches_dict["standard_metadata.ingress_port"] = "{:02x}".format(ingress_port)
    if egress_port:
        matches_dict["standard_metadata.egress_port"] = "{:02x}".format(egress_port)
    if eth_dst:
        matches_dict["hdr.ethernet.dst_addr"] = eth_dst.translate({ord(':'): None}).lower()
    if eth_src:
        matches_dict["hdr.ethernet.src_addr"] = eth_src.translate({ord(':'): None}).lower()
    if eth_type:
        matches_dict["hdr.ethernet.ether_type"] = "{:04x}".format(eth_type)
    if ipv4_dst:
        matches_dict["hdr.ipv4.dst_addr"] = str(binascii.b2a_hex(socket.inet_aton(ipv4_dst)))
    if ipv4_src:
        matches_dict["hdr.ipv4.src_addr"] = str(binascii.b2a_hex(socket.inet_aton(ipv4_src)))
    if ipv4_proto:
        matches_dict["local_metadata.ip_proto"] = "{:02x}".format(ipv4_proto)
    if l4_src:
        matches_dict["local_metadata.l4_src_port"] = "{:04x}".format(l4_src)
    if l4_dst:
        matches_dict["local_metadata.l4_dst_port"] = "{:04x}".format(l4_dst)
    if dns_id:
        matches_dict["local_metadata.dns_id"] = "{:04x}".format(dns_id)

    # TODO: refine this further
    for flow in flows:
        if flow["tableId"] == TABLE_ID:
            for criteria in flow["selector"]["criteria"]:
                if criteria["type"] == "PROTOCOL_INDEPENDENT":
                    matches = criteria["matches"]
                    if len(matches) == len(matches_dict):
                        num_matches = 0
                        for match in matches:
                            if match["field"] in matches_dict and matches_dict[match["field"]] == match["value"]:
                                num_matches += 1
                        if num_matches == len(matches_dict):
                            return flow["id"]

    return None


def delete_rule(table=DEFAULT_TABLE,
                ingress_port=None,
                egress_port=None,
                eth_dst=None,
                eth_src=None,
                eth_type=None,
                ipv4_src=None,
                ipv4_dst=None,
                ipv4_proto=None,
                l4_src=None,
                l4_dst=None,
                dns_id=None):
    flow_id = get_flow_id(table, ingress_port, egress_port, eth_dst, eth_src, eth_type, ipv4_src, ipv4_dst,
                          ipv4_proto, l4_src, l4_dst, dns_id)
    if flow_id:
        response = requests.delete(RESTFUL_GETPOST_FLOW_URL + "/" + DEVICE_ID + "/" + flow_id, auth=AUTH)
        print("Delete Rule: Response is: {0}".format(response))


def install_group(group_id, output):
    json_data = {
        "type": "ALL",
        "appCookie": "0x{:08x}".format(group_id),
        "groupId": str(group_id),
        "buckets": [
            {
                "treatment": {
                    "instructions": [
                        {
                            "type": "OUTPUT",
                            "port": str(output)
                        }
                    ]
                }
            }
        ]
    }

    print(json_data)
    response = requests.post(RESTFUL_GETPOST_GROUP_URL + "/" + DEVICE_ID, data=json.dumps(json_data), auth=AUTH)
    print("Install Group: Response is: {0}".format(response))


def delete_group(group_id):
    app_cookie = "0x{:08x}".format(group_id)
    response = requests.delete(RESTFUL_GETPOST_GROUP_URL + "/" + DEVICE_ID + "/" + app_cookie, auth=AUTH)
    print("Delete Group:Response is: {0}".format(response))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Config Script')
    parser.add_argument('--switch-type', type=str, action="store", default="bmv2")
    parser.add_argument('--bypass', action="store_true", default=False)
    parser.add_argument('--clear', action="store_true", default=False)
    args = parser.parse_args()

    DEVICE_ID += args.switch_type


    def clear():
        delete_rule(table="forward", ingress_port=44, eth_dst="3c:fd:fe:e9:77:60")
        delete_rule(table="forward", ingress_port=36, eth_dst="3c:fd:fe:e9:73:b8")


    if args.clear:
        clear()

    if args.bypass:
        install_rule(table="forward", ingress_port=44, eth_dst="3c:fd:fe:e9:77:60", output=36)
        install_rule(table="forward", ingress_port=36, eth_dst="3c:fd:fe:e9:73:b8", output=44)

##############################################################################################
# Rest API Usage:
##############################################################################################

# Installing rules:
# - install_rule(table=(string)<table name>, 
#                priority=(int)<bigger number gets higher priority>,
#                timeout=(int)<timeout value of the rule>,
#                is_permanent=(True|False)<rule never times out>,
#                ingress_port=(int)<ingress port number>, 
#                egress_port=(int)<egress port number>, 
#                eth_dst=(string)<destination MAC address>, 
#                eth_src=(string)<source MAC address>, 
#                eth_type=(int)<MAC type>, 
#                ipv4_src=(string)<source IP address>, 
#                ipv4_dst=(string)<destination IP address>, 
#                ipv4_proto=(int)<IP protocol>, 
#                l4_src=(int)<layer-4 source port>,
#                l4_dst=(int)<layer-4 destination port>, 
#                dns_id=(int)<DNS identification number>, 
#                output=(int)<output port number ... to send the packet out on>,
#                monitor=(True|False)<clone to monitor>,
#                noop=(True|False)<no operation>
#               )
# - Examples:
#   - Rule in `forward` table with priority 400 that matches on ingress port, eth_src/dst, ipv4_src/dst, and forwards to port 3. 
#     install_rule(table="forward",
#                  priority=400,
#                  ingress_port=1,
#                  eth_src="00:00:00:00:00:1a", eth_dst="00:00:00:00:00:1b", eth_type=0x800,
#                  ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2",
#                  output=3)
#   - Rule in `monitor` table with priority 4000 that matches on ipv4_src/dst, l4_src/dst, and clones to monitoring server. Note: this rule has a higher priority (4000) than the above rule (400), i.e., if both this and the above rule match, this one gets the priority.
#     install_rule(table="monitor",
#                  priority=4000,
#                  ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2",
#                  l4_src=80, l4_dst=80,
#                  monitor=True)
#   - Match on ipv4_src/dst in `monitor` table, and perform noop.
#     install_rule(table="monitor",
#                  ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2",
#                  noop=True)    

# Deleting rules:
# - delete_rule(table=(string)<table name>, 
#               ingress_port=(int)<ingress port number>, 
#               egress_port=(int)<egress port number>, 
#               eth_dst=(string)<destination MAC address>, 
#               eth_src=(string)<source MAC address>, 
#               eth_type=(int)<MAC type>, 
#               ipv4_src=(string)<source IP address>, 
#               ipv4_dst=(string)<destination IP address>, 
#               ipv4_proto=(int)<IP protocol>, 
#               l4_src=(int)<layer-4 source port>,
#               l4_dst=(int)<layer-4 destination port>, 
#               dns_id=(int)<DNS identification number>
#               )
# - Examples:
#   - Match on ingress port, eth_src/dst, ipv4_src/dst in `forward` table, and delete the rule. 
#     delete_rule(table="forward",
#                 ingress_port=1,
#                 eth_src="00:00:00:00:00:1a", eth_dst="00:00:00:00:00:1b", eth_type=0x800,
#                 ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2")
#   - Match on ipv4_src/dst, l4_src/dst in `monitor` table, and delete the rule. 
#     delete_rule(table="monitor",
#                 ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2",
#                 l4_src=80, l4_dst=80)
#   - Match on ipv4_src/dst in `monitor` table, and delete the rule. 
#     delete_rule(table="monitor",
#                 ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2")    
