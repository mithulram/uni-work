ASOA_DIR="/home/technischeinfo/Desktop/ASOA/asoa"
ASOA_VERSION="0.4.0"
SEC_NO_SEC="sec"  # sec vs. nosec
REL_MODE="release"

if [[ ${SEC_NO_SEC} = "sec" ]]; then
	PACKAGES=("asoa_core-${ASOA_VERSION}.deb" "asoa_security-${ASOA_VERSION}.deb")
elif [[ ${SEC_NO_SEC} = "nosec" ]]; then
	PACKAGES=("asoa_core-${ASOA_VERSION}.deb")
fi

NETWORK_MODE="demonstrator_local"
AUTH_SERVER_IP="10.0.0.28"
ASOA_CONFIG_NAME="asoa_security.conf"


# WINDOW SETTING
WIDTH=100
HEIGHT=12
Y_DIFF=285

DIR_DEMO="/home/dominik/Desktop/Demo"


if [[ "${NETWORK_MODE}" = "office" ]]; then 
	subnet="132.231.14."
	ip_start=104
	ip_end=108
elif [[ "${NETWORK_MODE}" = "demonstrator" ]]; then 
	subnet="132.231.14."
	ip_start=1 # 130
	ip_end=126 # 190
elif [[ "${NETWORK_MODE}" = "demonstrator_local" ]]; then 
	subnet="10.0.0."
	ip_start=1
	ip_end=16
else
	echo "Unknown network mode: ${NETWORK_MODE}"
	exit
fi
