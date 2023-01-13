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

package org.dataplane.pipelines.forward.common;

import org.onosproject.core.ApplicationId;
import org.onosproject.net.DeviceId;
import org.onosproject.net.PortNumber;
import org.onosproject.net.flow.DefaultFlowRule;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.FlowRule;
import org.onosproject.net.flow.criteria.PiCriterion;
import org.onosproject.net.group.DefaultGroupBucket;
import org.onosproject.net.group.DefaultGroupDescription;
import org.onosproject.net.group.DefaultGroupKey;
import org.onosproject.net.group.GroupBucket;
import org.onosproject.net.group.GroupBuckets;
import org.onosproject.net.group.GroupDescription;
import org.onosproject.net.group.GroupKey;
import org.onosproject.net.pi.model.PiActionProfileId;
import org.onosproject.net.pi.model.PiTableId;
import org.onosproject.net.pi.runtime.PiAction;
import org.onosproject.net.pi.runtime.PiGroupKey;
import org.onosproject.net.pi.runtime.PiTableAction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.ByteBuffer;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static org.onosproject.net.group.DefaultGroupBucket.createAllGroupBucket;
import static org.onosproject.net.group.DefaultGroupBucket.createCloneGroupBucket;
import static org.dataplane.pipelines.forward.Constants.DEFAULT_FLOW_RULE_PRIORITY;

public final class Utils {

    private static final Logger log = LoggerFactory.getLogger(Utils.class);

    public static GroupDescription buildMulticastGroup(
            ApplicationId appId,
            DeviceId deviceId,
            int groupId,
            Collection<PortNumber> ports) {
        return buildReplicationGroup(appId, deviceId, groupId, ports, false);
    }

    public static GroupDescription buildCloneGroup(
            ApplicationId appId,
            DeviceId deviceId,
            int groupId,
            Collection<PortNumber> ports) {
        return buildReplicationGroup(appId, deviceId, groupId, ports, true);
    }

    private static GroupDescription buildReplicationGroup(
            ApplicationId appId,
            DeviceId deviceId,
            int groupId,
            Collection<PortNumber> ports,
            boolean isClone) {

        checkNotNull(deviceId);
        checkNotNull(appId);
        checkArgument(!ports.isEmpty());

        final GroupKey groupKey = new DefaultGroupKey(
                ByteBuffer.allocate(4).putInt(groupId).array());

        final List<GroupBucket> bucketList = ports.stream()
                .map(p -> DefaultTrafficTreatment.builder()
                        .setOutput(p).build())
                .map(t -> isClone ? createCloneGroupBucket(t)
                        : createAllGroupBucket(t))
                .collect(Collectors.toList());

        return new DefaultGroupDescription(
                deviceId,
                isClone ? GroupDescription.Type.CLONE : GroupDescription.Type.ALL,
                new GroupBuckets(bucketList),
                groupKey, groupId, appId);
    }

    public static FlowRule buildFlowRule(DeviceId switchId, ApplicationId appId,
                                         String tableId, PiCriterion piCriterion,
                                         PiTableAction piAction) {
        return DefaultFlowRule.builder()
                .forDevice(switchId)
                .forTable(PiTableId.of(tableId))
                .fromApp(appId)
                .withPriority(DEFAULT_FLOW_RULE_PRIORITY)
                .makePermanent()
                .withSelector(DefaultTrafficSelector.builder()
                        .matchPi(piCriterion).build())
                .withTreatment(DefaultTrafficTreatment.builder()
                        .piTableAction(piAction).build())
                .build();
    }

    public static GroupDescription buildSelectGroup(DeviceId deviceId,
                                                    String tableId,
                                                    String actionProfileId,
                                                    int groupId,
                                                    Collection<PiAction> actions,
                                                    ApplicationId appId) {

        final GroupKey groupKey = new PiGroupKey(
                PiTableId.of(tableId), PiActionProfileId.of(actionProfileId), groupId);
        final List<GroupBucket> buckets = actions.stream()
                .map(action -> DefaultTrafficTreatment.builder()
                        .piTableAction(action).build())
                .map(DefaultGroupBucket::createSelectGroupBucket)
                .collect(Collectors.toList());
        return new DefaultGroupDescription(
                deviceId,
                GroupDescription.Type.SELECT,
                new GroupBuckets(buckets),
                groupKey,
                groupId,
                appId);
    }

    public static void sleep(int millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            log.error("Interrupted!", e);
            Thread.currentThread().interrupt();
        }
    }
}
