#username, hostname, folder, architecture, build_target?, files to be transmitted
radar="pi;ecu6;Radar;armhf;yes;build/armhf/${REL_MODE}/main|config/asoa_security.conf"
sensormodule="pi;ecu15;SensorModule;armhf;yes;build/armhf/${REL_MODE}/main|config/asoa_security.conf"
cerebrum="pi;ecu4;Cerebrum;armhf;yes;build/armhf/${REL_MODE}/main|config/asoa_security.conf"
dynamicmodule="pi;ecu12;DynamicModule;armhf;yes;build/armhf/${REL_MODE}/main|config/asoa_security.conf"
dashboard="pi;ecu2;Dashboard;armhf;yes;build/armhf/${REL_MODE}/main|config/asoa_security.conf"
# orchestrator="pi;ecu10;Orchestrator;armhf;no;asoa_security.conf|StartDemo|StopDemo"
# authserver="10.0.0.1;root;/home/root/asoa/demo/authserver"

all_ecus=(${radar} ${sensormodule} ${cerebrum} ${dynamicmodule} ${dashboard} ${orchestrator})
#all_ecus=(${radar})

