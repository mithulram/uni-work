#!/bin/bash

######################################################################################
# Build config
source "./Rollout/config.sh"

######################################################################################
# ECUs
source "./Rollout/ecus.sh"

######################################################################################
# Request IP addresses of ECUs

source "./Rollout/IPRequest/ecu_ip_request.sh"

######################################################################################

ARM_TOOLCHAIN_ROOT=/opt/toolchains/cross-armhf
NUM_CORES=8

ecu_addr=$(request_hosts $2)

is_in_arr () {
	e="$2"
	match="$1"
	for e; do [[ "$e" == "$match" ]] && return 0; done
	return 1
}

function sync_packages() {

	architecture=$1
	username=$2
	ip=$3
	
	build_dir="${ASOA_DIR}/build/${architecture}/${SEC_NO_SEC}/${REL_MODE}"

	echo "Sending packages to ${hostname} at ${ip}"
		
	for current_package in "${PACKAGES[@]}"
	do
		scp "${build_dir}/${current_package}" "${username}@${ip}:/home/pi/asoa/demo" &
	done
}

function sync_services() {


	architecture=$1
	build_service=$2
	files_to_transmit=$3
	username=$4
	ip=$5
	
	if [ ${architecture} = "armhf" ]; then
		export ARMHF_ROOTFS=${ARM_TOOLCHAIN_ROOT}/rootfs
		FLAGS="-DCMAKE_TOOLCHAIN_FILE=${ARM_TOOLCHAIN_ROOT}/toolchain_armhf.cmake "
	fi


	if [[ ${build_service} == "yes" ]]; then
		cd ECUs
		./build.sh ${REL_MODE} ${architecture} ecu="${ecu_name}"
		cd ..
	fi

	# do not send anything to embedded devices
	if [[ ${architecture} = "armr5" ||  ${architecture} = "esp32" ]]; then
		continue
	fi

	# write IP address of the authentication server to the configuration files
	IFS='|' read -ra files_to_transmit <<< "${files_to_transmit}"
	for file in "${files_to_transmit[@]}"; do
		if [[ ${file} = "config/${ASOA_CONFIG_NAME}" ]]; then
			sed -i -e 's/fallback_ip = .*/fallback_ip = \"'${AUTH_SERVER_IP}'\"/g' "${ecu_location}/${file}"
		fi
		echo "Sending ${ecu_location}/${file} to ${hostname} at ${ip}"
		scp "${ecu_location}/${file}" "${username}@${ip}:/home/pi/asoa/demo" 
			
	done
}

for d in ${all_ecus[@]}; do
	IFS=";" read -r -a arr <<< "${d}"
	username="${arr[0]}"
	hostname="${arr[1]}"

	ip=$(get_ecu_addr "${ecu_addr}" "${hostname}")

	if [[ "${ip}" = "-1" ]]; then
		exit
	fi

	# read ECU parameters
	ecu_name=${arr[2]}
	ecu_location="ECUs/${ecu_name}"
	architecture="${arr[3]}"
	build_service="${arr[4]}"
	files_to_transmit="${arr[5]}"

	if [[ "$1" = "packages" ]]; then
		sync_packages  ${architecture} ${username} ${ip}

	elif [[ "$1" = "services" ]]; then
		
		sync_services ${architecture} ${build_service} ${files_to_transmit} ${username} ${ip}
	else 
		echo "Unknown option: Please either chose \"services\" or \"packages\"."
		exit
	fi
done


if [[ ! -z ${authserver+x} && "$1" = "services" ]]; then
	echo "Sending data to the security platform:";
	IFS=";" read -r -a arr <<< "${authserver}"
	address="${arr[0]}"
	hostname="${arr[1]}"
	path="${arr[2]}"
	scp -r "SecurityPlatform/." "${username}@${ip}:${path}"

fi
