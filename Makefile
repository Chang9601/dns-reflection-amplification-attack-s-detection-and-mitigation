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

PYTHON2_OK := $(shell python2 --version 2>&1)
PYTHON3_OK := $(shell python3 --version 2>&1)
ifeq ('$(PYTHON3_OK)','')
	ifeq ('$(PYTHON2_OK)','')
		$(error package 'python 2 or 3' not found)
	else
		PYTHON = python2
		PYTHON_PKG = python
	endif
else
	PYTHON = python3
	PYTHON_PKG = python3
endif

SCRIPTS = ./scripts

export name ?=

.PHONY: mininet controller netcfg cli host

mininet:
	$(SCRIPTS)/mn-stratum --custom topo/test.py --topo testtopo
	make clean

controller:
	make .onos-controller

netcfg:
	make .onos-app-reload
	sleep 1
	make .onos-netcfg

cli:
	make .onos-cli

setup: .setup

start-monitor: .start-monitor

stop-monitor: .stop-monitor

plots: .plots

# Usage: make host name=h1
host:
	$(SCRIPTS)/utils/mn-stratum/exec $(name)

clean: .p4-clean .onos-app-clean .setup-clean

####################################################################
# ONOS Controller and Application
####################################################################

.onos-controller:
	ONOS_APPS=gui,proxyarp,drivers.bmv2,lldpprovider,hostprovider,fwd  \
	$(SCRIPTS)/onos

.onos-cli:
	$(SCRIPTS)/onos-cli

.onos-netcfg:
	$(SCRIPTS)/onos-netcfg onos/cfg/netcfg.json

.onos-app-build: .p4-build
	cd onos/app && ../../$(SCRIPTS)/maven clean package

.onos-app-reload: .onos-app-build
	$(SCRIPTS)/onos-app reinstall! onos/app/target/forward-1.0-SNAPSHOT.oar

.onos-app-clean:
	sudo rm -rf onos/app/target

####################################################################
# Build P4
####################################################################

.p4-build:
	mkdir -p .build-p4/bmv2 onos/app/src/main/resources
	$(SCRIPTS)/p4c p4c-bm2-ss --arch v1model -o .build-p4/bmv2/bmv2.json \
		-DTARGET_BMV2 -DCPU_PORT=255 \
		--p4runtime-files .build-p4/bmv2/p4info.txt \
		p4-src/main.p4
	# Copy the relevant files to the pipeconf resources
	cp -r .build-p4/bmv2 onos/app/src/main/resources
	echo "255" > onos/app/src/main/resources/bmv2/cpu_port.txt
	sudo rm -rf .build-p4

.p4-clean:
	sudo rm -rf onos/app/src/main/resources/*
	sudo rm -rf .build-p4

####################################################################
# Setup Configs
####################################################################

.setup: .mininet-install-prereqs \
		.config-hosts \
		.dns \
		.victim-host \
		.regular-host \
		.attacker

.mininet-install-prereqs:
	docker exec -it mn-stratum bash -c \
		"apt-get update ; \
		 apt-get -y --allow-unauthenticated install bind9 dnsutils python-scapy python-requests"

.config-hosts:
	for i in 1 2 3 4 ; do \
        $(SCRIPTS)/utils/mn-stratum/exec-script h$$i \
        	"sysctl -w net.ipv6.conf.all.disable_ipv6=1 && \
        	 sysctl -w net.ipv6.conf.default.disable_ipv6=1 && \
        	 sysctl -w net.ipv6.conf.lo.disable_ipv6=1"; \
    done

.dns:
	# h1 is the domain name server
	$(SCRIPTS)/utils/mn-stratum/exec-d-script h1 \
		"/etc/init.d/bind9 stop &> /dev/null 2> /dev/null && \
		 /etc/init.d/bind9 start &> /dev/null 2> /dev/null"
	sleep 1

.victim-host:
	# h2 is the victim
	$(SCRIPTS)/utils/mn-stratum/exec-d-script h2 \
		"python py-src/legit_dns_traffic.py 10.0.0.1 5 > /dev/null & \
		 ping 10.0.0.1 -i 2 > logs/h2_ping.txt & \
		 python py-src/test_dns_traffic.py h2-eth0 00:00:00:00:00:02 > logs/h2_test.txt &"
	sleep 1

.regular-host:
	# h3 is a regular host
	$(SCRIPTS)/utils/mn-stratum/exec-d-script h3 \
		"python py-src/legit_dns_traffic.py 10.0.0.1 5 > /dev/null & \
		 ping 10.0.0.1 -i 2 > logs/h3_ping.txt & \
		 python py-src/test_dns_traffic.py h3-eth0 00:00:00:00:00:03 > logs/h3_test.txt &"
	sleep 1

.attacker:
	# h4 is the attacker
	$(SCRIPTS)/utils/mn-stratum/exec-d-script h4 \
		"python py-src/send_dns_query.py 10.0.0.2 10.0.0.1 0.5 > /dev/null"

.start-monitor:
	# m1 is the monitor, which interacts with ONOS
	$(SCRIPTS)/utils/mn-stratum/exec-script m1 \
		"cd py-src && python start_dns_monitor.py"

.stop-monitor:
	$(SCRIPTS)/utils/mn-stratum/exec-script m1 \
		"pkill -f start_dns_monitor"

MATPLOTLIB_PKG_OK := $(strip $(shell dpkg-query -l | grep $(PYTHON_PKG)-matplotlib | wc -l))
.plots-prereqs:
    ifeq ('$(MATPLOTLIB_PKG_OK)','0')
		sudo apt-get update
		sudo apt-get --yes install $(PYTHON_PKG)-matplotlib
    endif

.plots: .plots-prereqs
	$(PYTHON) py-src/plot_dns_results.py --list logs/h2_test.txt logs/h3_test.txt --output logs/dns_response_rates.png

.setup-clean:
	sudo rm -rf logs/*
