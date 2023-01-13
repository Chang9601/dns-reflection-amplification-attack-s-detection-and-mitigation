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

package org.dataplane.pipelines.forward;

import org.onosproject.net.pi.model.PiPipeconfId;
import org.onosproject.net.pi.model.PiActionId;
import org.onosproject.net.pi.model.PiActionParamId;
import org.onosproject.net.pi.model.PiActionProfileId;
import org.onosproject.net.pi.model.PiMeterId;
import org.onosproject.net.pi.model.PiPacketMetadataId;
import org.onosproject.net.pi.model.PiCounterId;
import org.onosproject.net.pi.model.PiMatchFieldId;
import org.onosproject.net.pi.model.PiTableId;

/**
 * Constants for pipeline.
 */
public final class Constants {

    // hide default constructor
    private Constants() {
    }

    public static final String APP_NAME = "org.dataplane.pipelines.forward";

    // Header field IDs
    public static final PiMatchFieldId HDR_HDR_IPV4_PROTOCOL =
            PiMatchFieldId.of("hdr.ipv4.protocol");
    public static final PiMatchFieldId HDR_HDR_IPV4_SRC_ADDR =
            PiMatchFieldId.of("hdr.ipv4.src_addr");
    public static final PiMatchFieldId HDR_HDR_ETHERNET_ETHER_TYPE =
            PiMatchFieldId.of("hdr.ethernet.ether_type");
    public static final PiMatchFieldId HDR_HDR_ETHERNET_SRC_ADDR =
            PiMatchFieldId.of("hdr.ethernet.src_addr");
    public static final PiMatchFieldId HDR_LOCAL_METADATA_L4_DST_PORT =
            PiMatchFieldId.of("local_metadata.l4_dst_port");
    public static final PiMatchFieldId HDR_LOCAL_METADATA_L4_SRC_PORT =
            PiMatchFieldId.of("local_metadata.l4_src_port");
    public static final PiMatchFieldId HDR_STANDARD_METADATA_INGRESS_PORT =
            PiMatchFieldId.of("standard_metadata.ingress_port");
    public static final PiMatchFieldId HDR_HDR_IPV4_DST_ADDR =
            PiMatchFieldId.of("hdr.ipv4.dst_addr");
    public static final PiMatchFieldId HDR_HDR_ETHERNET_DST_ADDR =
            PiMatchFieldId.of("hdr.ethernet.dst_addr");
    // Table IDs
    public static final PiTableId INGRESS_FORWARD_TABLE =
            PiTableId.of("IngressPipeImpl.forward_control.forward_table");
    // Action IDs
    public static final PiActionId INGRESS_DROP =
            PiActionId.of("IngressPipeImpl.forward_control.drop");
    public static final PiActionId NO_ACTION =
            PiActionId.of("NoAction");
    public static final PiActionId INGRESS_SET_OUTPUT_PORT =
            PiActionId.of("IngressPipeImpl.forward_control.set_output_port");
    public static final PiActionId INGRESS_SEND_TO_CPU =
            PiActionId.of("IngressPipeImpl.forward_control.send_to_cpu");
    // Action Param IDs
    public static final PiActionParamId PORT_NUM =
            PiActionParamId.of("port_num");
    // Packet Metadata IDs
    public static final PiPacketMetadataId INGRESS_PORT =
            PiPacketMetadataId.of("ingress_port");
    public static final PiPacketMetadataId EGRESS_PORT =
            PiPacketMetadataId.of("egress_port");

    // Switch-specific settings
    public static final PiPipeconfId BMV2_PIPECONF_ID = new PiPipeconfId(APP_NAME + ".bmv2");
    public static final String BMV2_P4INFO_PATH = "/bmv2/p4info.txt";
    public static final String BMV2_JSON_PATH = "/bmv2/bmv2.json";
    public static final String BMV2_CPU_PORT_PATH = "/bmv2/cpu_port.txt";

    public static final int DEFAULT_FLOW_RULE_PRIORITY = 10;

    public static final int INT_SWITCH_PORT = 5;
    public static final int INT_CLONE_SESSION_ID = 500;
}
