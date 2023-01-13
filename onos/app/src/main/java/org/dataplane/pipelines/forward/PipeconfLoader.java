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

import com.google.common.collect.ImmutableList;
import org.onosproject.core.CoreService;
import org.onosproject.net.behaviour.Pipeliner;
import org.onosproject.net.driver.DriverAdminService;
import org.onosproject.net.driver.DriverProvider;
import org.onosproject.net.pi.model.DefaultPiPipeconf;
import org.onosproject.net.pi.model.PiPipeconf;
import org.onosproject.net.pi.model.PiPipeconfId;
import org.onosproject.net.pi.model.PiPipelineInterpreter;
import org.onosproject.net.pi.model.PiPipelineModel;
import org.onosproject.net.pi.service.PiPipeconfService;
import org.onosproject.p4runtime.model.P4InfoParser;
import org.onosproject.p4runtime.model.P4InfoParserException;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URL;
import java.util.List;
import java.util.Collection;
import java.util.stream.Collectors;

import static org.onosproject.net.pi.model.PiPipeconf.ExtensionType.*;

/**
 * Component that produces and registers the basic pipeconfs when loaded.
 */
@Component(immediate = true)
public final class PipeconfLoader {

    private final Logger log = LoggerFactory.getLogger(getClass());

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private PiPipeconfService piPipeconfService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private CoreService coreService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private DriverAdminService driverAdminService;

    @Activate
    public void activate() {
        coreService.registerApplication(Constants.APP_NAME);
        // Registers all pipeconf at component activation.
        if (piPipeconfService.getPipeconf(Constants.BMV2_PIPECONF_ID).isPresent()) {
            piPipeconfService.unregister(Constants.BMV2_PIPECONF_ID);
        }
        removePipeconfDrivers(Constants.BMV2_PIPECONF_ID);

        piPipeconfService.register(buildBmv2Pipeconf());
    }

    @Deactivate
    public void deactivate() {
        if (piPipeconfService.getPipeconf(Constants.BMV2_PIPECONF_ID).isPresent()) {
            piPipeconfService.unregister(Constants.BMV2_PIPECONF_ID);
        }
        removePipeconfDrivers(Constants.BMV2_PIPECONF_ID);
    }

    private static PiPipeconf buildBmv2Pipeconf() {
        final URL p4InfoUrl = PipeconfLoader.class.getResource(Constants.BMV2_P4INFO_PATH);
        final PiPipelineModel pipelineModel = parseP4Info(p4InfoUrl);

        return DefaultPiPipeconf.builder()
                .withId(Constants.BMV2_PIPECONF_ID)
                .withPipelineModel(pipelineModel)
                .addBehaviour(PiPipelineInterpreter.class, InterpreterImpl.class)
                .addBehaviour(Pipeliner.class, PipelinerImpl.class)
                .addExtension(P4_INFO_TEXT, p4InfoUrl)
                .addExtension(BMV2_JSON,
                        PipeconfLoader.class.getResource(Constants.BMV2_JSON_PATH))
                .addExtension(CPU_PORT_TXT,
                        PipeconfLoader.class.getResource(Constants.BMV2_CPU_PORT_PATH))
                .build();
    }

    private static PiPipelineModel parseP4Info(URL p4InfoUrl) {
        try {
            return P4InfoParser.parse(p4InfoUrl);
        } catch (P4InfoParserException e) {
            throw new IllegalStateException(e);
        }
    }

    private void removePipeconfDrivers(PiPipeconfId piPipeconfId) {
        List<DriverProvider> driverProvidersToRemove = driverAdminService
                .getProviders().stream()
                .filter(p -> p.getDrivers().stream()
                        .anyMatch(d -> d.name().endsWith(piPipeconfId.id())))
                .collect(Collectors.toList());

        if (driverProvidersToRemove.isEmpty()) {
            return;
        }

        log.info("Found {} outdated drivers for pipeconf '{}', removing...",
                driverProvidersToRemove.size(), piPipeconfId);

        driverProvidersToRemove.forEach(driverAdminService::unregisterProvider);
    }

}
