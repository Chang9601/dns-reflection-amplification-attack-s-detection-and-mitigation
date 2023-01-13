/*****************************************************************************
 *
 *     This file is part of Purdue CS 422.
 *
 *     Purdue CS 422 is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation, either version 3 of the License, or
 *     (at your option) any later version.
 *
 *     Purdue CS 422 is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License
 *     along with Purdue CS 422. If not, see <https://www.gnu.org/licenses/>.
 *
 *****************************************************************************/

#ifndef __FORWARD__
#define __FORWARD__

#include "headers.p4"
#include "defines.p4"

control forward_control(inout parsed_headers_t hdr,
                        inout local_metadata_t local_metadata,
                        inout standard_metadata_t standard_metadata) {

    direct_counter(CounterType.packets_and_bytes) foward_counter;

    action noop() { }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action set_output_port(port_num_t port_num) {
        standard_metadata.egress_spec = port_num;
    }

    action send_to_cpu() {
        standard_metadata.egress_spec = CPU_PORT;
    }

    table forward_table {
        key = {
            standard_metadata.ingress_port: ternary;
            hdr.ethernet.dst_addr: ternary;
            hdr.ethernet.src_addr: ternary;
            hdr.ethernet.ether_type: ternary;
            hdr.ipv4.dst_addr: ternary;
            hdr.ipv4.src_addr: ternary;
            local_metadata.ip_proto: ternary;
            local_metadata.icmp_type: ternary;
            local_metadata.l4_src_port: ternary;
            local_metadata.l4_dst_port: ternary;
            local_metadata.dns_id: ternary;
        }
        actions = {
            noop;
            drop;
            set_output_port;
            send_to_cpu;
        }
        const default_action = drop;
        counters = foward_counter;
    }

    apply {
        forward_table.apply();
     }
}

#endif
