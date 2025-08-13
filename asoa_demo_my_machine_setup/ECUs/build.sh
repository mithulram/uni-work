#!/bin/bash

######################################################################################
# Load configuration
source "build_config.sh"
######################################################################################

function validate_return_code() {
	if [[ ! "$1" = 0 ]]; then
		echo "Exiting with error from build.sh"
		exit $1
	fi
}

if [[ $1 = "--help" ]]; then
	printf "USAGE: ./build.sh [ARCHITECTURE] [ASOA_SECURITY] [BUILD_TYPE] [PACKAGING] [UPDATE_TOOLCHAIN]\n\nARCHITECTURE:     amd64|x86_64 rspi|armhf petalinux|armhf cortexr5|armr5\nASOA_SECURITY:    sec nosec\nBUILD_TYPE:       release relwithdebinfo\nPACKAGING:        package\nUPDATE_TOOLCHAIN: updatetoolchain\n"
	exit
fi

export AARCH64_ROOTFS=${DIR_TOOLCHAIN_AARCH64}/rootfs
export ARMHF_ROOTFS=${DIR_TOOLCHAIN_ARMHF}/rootfs
export ESP32_ROOTFS=${DIR_TOOLCHAIN_ESP32}/rootfs
export ARMR5_ROOTFS=${DIR_TOOLCHAIN_ARMR5}/rootfs

export DIR_XILINX_PLATFORM_PROJ=${DIR_XILINX_HEADERS}
export DIR_ESP32_PLATFORM_PROJ=${DIR_ESP32_HEADERS}

# Parse undefined number of arguments
while [[ $# -gt 0 ]]; do
	echo $1
	case "$1" in 
		release | Release)
			BUILD_TYPE="release"
			shift
		;;
		relwithdebinfo | RelWithDebInfo)
			BUILD_TYPE="relwithdebinfo"
			shift
		;;
		debug)
			BUILD_TYPE="debug"
			shift
		;;
		rspi | armhf)
			ARCHITECTURE="armhf"
			DIR_TOOLCHAIN=${DIR_TOOLCHAIN_ARMHF}
			CMAKE_TOOLCHAIN_FILE="-DCMAKE_TOOLCHAIN_FILE=${DIR_TOOLCHAIN}/toolchain_armhf.cmake"
			shift
		;;
		amd64 | x86_64)
			ARCHITECTURE="amd64"
			shift
		;;
		petalinux | aarch64)
			ARCHITECTURE="aarch64"
			DIR_TOOLCHAIN=${DIR_TOOLCHAIN_AARCH64}
			CMAKE_TOOLCHAIN_FILE="-DCMAKE_TOOLCHAIN_FILE=${DIR_TOOLCHAIN}/toolchain_aarch64.cmake"
			shift
		;;
		cortexr5 | armr5)
			ARCHITECTURE="armr5"
			DIR_TOOLCHAIN=${DIR_TOOLCHAIN_ARMR5}
			CMAKE_TOOLCHAIN_FILE="-DCMAKE_TOOLCHAIN_FILE=${DIR_TOOLCHAIN}/toolchain_armr5.cmake"
			shift
		;;
		esp32)
			ARCHITECTURE="esp32"
			DIR_TOOLCHAIN=${DIR_TOOLCHAIN_ESP32}
			CMAKE_TOOLCHAIN_FILE="-DCMAKE_TOOLCHAIN_FILE=${DIR_TOOLCHAIN}/toolchain_esp32.cmake"
			shift
		;;
		*)
			if [[ $1 == ecu* ]]; then
				ecu_name=(${1//=/ })
				ECU_NAME=${ecu_name[1]}
				if [[ -z ${ECU_NAME} || ! -d ${ECU_NAME} ]]; then
					echo "Unknown ECU \"${ECU_NAME}\""
					exit 1;
				fi
			else
				echo "Unknown argument: $1"
				exit 1
			fi
			shift
	esac
done


if [[ -z "${BUILD_TYPE}" ]]; then
	BUILD_TYPE="release"
	BUILD_DEFAULT="(default)"
fi

if [[ -z "${ARCHITECTURE}" ]]; then
	ARCHITECTURE=${DEFAULT_ARCHITECTURE}
	ARCHITECTURE_DEFAULT="(default)"
fi

if [[ (! -d "${DIR_TOOLCHAIN}" || -z "${DIR_TOOLCHAIN}") && "${ARCHITECTURE}" != "${DEFAULT_ARCHITECTURE}" ]]; then
	printf "Toolchain not found at %s\n" ${DIR_TOOLCHAIN}
	exit 1
fi

echo '----------------------------------'
printf "BUILD CONFIGURATION:\n\n"
printf '%-15s%s\n' "ECU:" "${ECU_NAME}"
printf '%-15s%s\n' "Architecture:" "${ARCHITECTURE} ${ARCHITECTURE_DEFAULT}"
printf '%-15s%s\n' "Build Type:" "${BUILD_TYPE} ${BUILD_DEFAULT}"
echo "----------------------------------"

#sleep 2

CMAKE_BUILD_PATH_SERVICE="${ECU_NAME}/${DIR_BUILD}/${ARCHITECTURE}/${BUILD_TYPE}"
CMAKE_BUILD_PATH_CONFIG="${ECU_NAME}/config/${DIR_BUILD}/${ARCHITECTURE}/${BUILD_TYPE}"


# build precompiled configuration
if [[ "${ARCHITECTURE}" = "esp32" || ${ARCHITECTURE} = "armr5" ]]; then
	printf "\nNow building the security configuration...\n\n"
	sleep 2
	cmake -B ${CMAKE_BUILD_PATH_CONFIG} -S "${ECU_NAME}/${DIR_CONFIG}" -DARCHITECTURE=${ARCHITECTURE} -DCMAKE_BUILD_TYPE=${BUILD_TYPE} ${CMAKE_TOOLCHAIN_FILE}
	make -C ${CMAKE_BUILD_PATH_CONFIG}
fi

# build ASOA services
if [[ "${ARCHITECTURE}" = "esp32" ]]; then
	printf "\nNow building the ASOA services...\n\n"
#	sleep 2
	. /opt/toolchains/cross-esp32/export.sh
	idf.py -B ${CMAKE_BUILD_PATH_SERVICE} -C ${ECU_NAME} build
elif [[ ! "${ARCHITECTURE}" = "armr5" ]]; then
	printf "\nNow building the ASOA services...\n\n"
#	sleep 2
	cmake -B ${CMAKE_BUILD_PATH_SERVICE} -S ${ECU_NAME} -DCMAKE_BUILD_TYPE=${BUILD_TYPE} ${CMAKE_TOOLCHAIN_FILE}
	validate_return_code $?

	make -j${NUM_CORES} -C ${CMAKE_BUILD_PATH_SERVICE} ${PACKAGING}
	validate_return_code $?
fi


