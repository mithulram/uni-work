######################################################################################
# Configuration
source "./Rollout/config.sh"

######################################################################################
# ECUs
source "./Rollout/ecus.sh"

######################################################################################
# Request IP addresses of ECUs
source "./Rollout/IPRequest/ecu_ip_request.sh"

######################################################################################

# Start remote ECUs
y=5
ecu_addr=$(request_hosts $1)
i=0
x_diff=20

for d in ${all_ecus[@]}; do
	IFS=";" read -r -a arr <<< "${d}"
	username="${arr[0]}"
	hostname="${arr[1]}"
	ip=$(get_ecu_addr "${ecu_addr}" "${hostname}")
	
	if (( $i % 5 == 0 )) ; then
		if [[ ! ${i} -eq "0" ]]; then
			x_diff=$((x_diff + 800))
			y=5
		fi
	fi
	
	if [[ "${ip}" = "-1" ]]; then
		exit
	fi
	
	i=$((i + 1))
	
	gnome-terminal --geometry ${WIDTH}x${HEIGHT}+${x_diff}+${y} -- ssh -t ${username}@${ip} "cd asoa/demo; bash -l"
	y=$((y+${Y_DIFF}))
done

y=5
x_diff=950
gnome-terminal --geometry ${WIDTH}x${HEIGHT}+${x_diff}+${y} --working-directory="${DIR_DEMO}"
y=$((y+${Y_DIFF}))
gnome-terminal --geometry ${WIDTH}x${HEIGHT}+${x_diff}+${y} --working-directory="${DIR_DEMO}"
y=$((y+${Y_DIFF}))
gnome-terminal --geometry ${WIDTH}x${HEIGHT}+${x_diff}+${y} --working-directory="${DIR_DEMO}"
y=$((y+${Y_DIFF}))
gnome-terminal --geometry ${WIDTH}x${HEIGHT}+${x_diff}+${y} --working-directory="${DIR_DEMO}/ECUs/Orchestrator"

