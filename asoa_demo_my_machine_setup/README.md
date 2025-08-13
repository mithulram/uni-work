# ASOA Demo

# TODO: add armr5 documentation

This is a small demonstrative implementation of some services communicating using [ASOA](https://fimgit.fim.uni-passau.de/puellen/asoa).
To run the demo, one first has to clone and build the ASOA repository. In the asoa repository, run `./build.sh amd64 deb`, `./build.sh armhf deb` and `./build.sh armr5`
to build the asoa libraries and packages. Also execute `python3 toolchains/update_toolchains.py`. The services of this demo link to those libraries. The corresponding toolchains can be found here:
- [amrr5](https://asoasecurity.seceng.fim.uni-passau.de/toolchains/armr5.zip)
- [armhf](https://asoasecurity.seceng.fim.uni-passau.de/toolchains/armhf.zip)
- [aarch64/amd64](https://asoasecurity.seceng.fim.uni-passau.de/toolchains/aarch64.zip)

Store the toolchains in `/opt/toolchains`

## Preparations
The demonstator setup contains Raspberry Pis and the Cortexr5 Brainstem, which act as the vehicle ECUs. To connect to the demonstrator, plug in the network cable and create a network profile with the following settings:
- Manual DHCP
- IP address: `10.0.0.28` (Addresses .1 to .16 are used by the ECUs, .27 is used by the Pi inside the small monitor on top of the demonstrator. This Pi is not used in this demo)
- Subnet: `225.255.255.224`

Then generate a public ssh key if you don't have one already and use 
- `ssh-copy-id -i pubkey.pub pi@ecu2.local`
- `ssh-copy-id -i pubkey.pub pi@ecu4.local`
- `ssh-copy-id -i pubkey.pub pi@ecu5.local`
- ...

for the Pis, which are `ecu2`, `ecu4`, `ecu5`, `ecu6`, `ecu8`, `ecu10`, `ecu12`, `ecu14`, `ecu15`, `ecu16`.
The local ip addresses of the Pis are `10.0.0.[ECU ID]`. You can see the IDs on the stickers next to the devices.
The password for the Pis is `vecsec_passau_ecu[ECU ID]`, e.g. vecsec_passau_ecu2, vecsec_passau_ecu4, ...

If you want to run the Demo servers Security Platform, Log Server and Service Configurator and the Orchestrator on your host system, install the `.deb` files built in the asoa:
- `sudo dpkg -i asoa_security-0.4.0.deb asoa_core-0.4.0.deb asoa_orchestrator-0.4.0.deb` 

## Adjust the config files
Adjust the `Rollout/config.sh` such that ASOA_DIR and DEMO_DIR are set correctly. Also adjust the `ECUs/build_config.sh` to update the paths to the Xilinx and ESP headers. Depending on which terminal your host system has, you may also have to change the `demo.sh`.
In the Security Platform, Log Server and Service Configurator folders make sure that the `server_config.xml` files contain the correct host ip address. In the `Rollout/ecus.sh` you can define whih device should run which service. 
## Run the demo (Only host system and Raspberry Pis)
- Run `./rollout.sh packages` to send the `.deb` asoa packages to the devices defined in `Rollout/ecus.sh`
- Run `./rollout.sh services` to build the services and to send the binary and the ECU config to the devices.
- Run `./demo.sh`, which opens several terminal windows. For each ECU, a terminal window with an open ssh connestion is opened. Also four empty terminal windows are opened.

On the ECUs, you first install the asoa packages using:
- `sudo dpkg -i asoa_security-0.4.0.deb asoa_core-0.4.0.deb asoa_orchestrator-0.4.0.deb` (You may have to uninstall existing asoa packages before doing that)

Then you can start the Servers:
- On one of the empty terminals, run `asoa_security_platform SecurityPlatform/` to start the Security Platform, which takes the path to the Security Platform configuration folder.
- On one of the empty terminals, run `asoa_log_server LogServer/` to start the Log Server, which takes the path to the Log Server configuration folder.
- On one of the empty terminals, run `asoa_service_configurator ServiceConfigurator/` to start the Service Configurator, which takes the path to the Service Configurator configuration folder.
- On one of the empty terminals, move into the `ECUs/Orchestrator` directory and run `asoa_orchestrator`

Then you can start the ECUs. On all terminal windows for the Pis, run `./main`

After the key distibution has finished, you can start the demo by typing into the Orchestrator `mk StartDemo`. If you now press the button on the breadboard, the needles should start to move.
Pause the Demo by typing into the orchestrator `mk StopDemo`
