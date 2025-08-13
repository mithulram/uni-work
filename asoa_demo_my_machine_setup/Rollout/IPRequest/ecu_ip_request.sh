file_cached_ecu_addr="Rollout/IPRequest/.cached_addr"

function print_error() {
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	printf "${RED}$1${NC}\n" >&2
}

function print_warning() {
	ORANGE='\033[1;33m'
	NC='\033[0m' # No Color
	printf "${ORANGE}$1${NC}\n" >&2
}

function request_hosts() {
	force=$1
	if [[ -f ${file_cached_ecu_addr} && ${force} != "force" ]]; then
		read -r raw_addr < ${file_cached_ecu_addr}
		echo ${raw_addr}
	else
		raw_addr=$(python3 Rollout/IPRequest/request.py  --subnet ${subnet} --ip_start ${ip_start} --ip_end ${ip_end})
		echo ${raw_addr} | tee ${file_cached_ecu_addr}
		echo ${raw_addr}
	fi
}

function get_ecu_addr() {
	raw_addr=$1
	target_hostname=$2

	IFS='|' read -ra ecus <<< "${ecu_addr}"
	found=false
	warnings=()
	errors=()
	for ecu in "${ecus[@]}"; do
		IFS=';' read -ra ecu_addr <<< "${ecu}"
		hostname=${ecu_addr[0]}
		ip=${ecu_addr[1]}
		if [[ ${hostname} = ${target_hostname} ]]; then
			echo ${ip}
			found=true
			break
		elif [[ "${hostname}" = "error" ]]; then 
			errors+=("${ip}")
		elif [[ "${hostname}" = "warning" ]]; then 
			warnings+=("${ip}")
		fi 
	done

	if [[ ${found} != true ]]; then
		echo "Host ${target_hostname} not found. Please have a look at the following warnings and errors:" >&2
		rm -f ${file_cached_ecu_addr}
		for error in "${errors[@]}"; do : 
			print_error "${error}"; 
		done
		for warning in "${warnings[@]}"; do : 
			print_warning "${warning}"
		done
		echo "-1"
	fi
}
