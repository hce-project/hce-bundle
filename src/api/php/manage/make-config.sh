#!/bin/bash

TEMPLATES=templates
TMP=/tmp/
TMPDIR=/tmp/$TEMPLATES
SINGLE=single
MULTI=multi
ALLHOSTDIR=allhost
RMHOST=router_manager
DATAHOSTDIR=datahost
BUNDLE=hce-node-bundle
CFG=$BUNDLE/api/php/cfg
INI=$BUNDLE/api/php/ini

RED='\e[1;31m'
BLUE='\e[1;34m'
DEF='\e[0m'

NODESREG='^[1-9]$|^10$'
HOSTSREG='^[0-9]+$'
OCTET='(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])'
IPREG='^\$OCTET\.\$OCTET\.\$OCTET\.\$OCTET$'
REPLICAS_POOL_ADMIN_PORTS_N=5530
REPLICAS_POOL_ADMIN_PORTS_M=5630
REPLICAS_POOL_ADMIN_PORTS_R=5730
TITLE='Make Config For HCE-NODE'

DIALOG=${DIALOG=dialog}
TEMPFILE=`mktemp /tmp/make-config.XXXXXX`
trap "rm -f $TEMPFILE" 0 1 2 5 15


# FINCTIONS #
function infoDialog() {
    $DIALOG --title "$TITLE" \
            --colors --msgbox "$1" 5 80
    clear
}

function validIp() {
    local  ip=$1
    local  stat=1
    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
    then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

function removeCurrentCfg() {
    $DIALOG --title "$TITLE" \
            --yesno "\n\n\n\n\nCreate new ../cfg/current_cfg.sh?" 20 80
    case $? in
        0)
            RMCURCFG=new;;
        1)
            RMCURCFG=use;;
        255)
            clear && infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function tmpPath() {
    $DIALOG --title "$TITLE" \
            --inputbox "Path for created files" 20 80 $TMPDIR 2> $TEMPFILE
    RETVAL=$?
    case $RETVAL in
        0)
            TMPDIR=$(cat $TEMPFILE | sed 's/\/$//');;
        1)
            infoDialog "Cancel. Exit" && exit 1;;
        255)
            infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function ipOfHosts() {
    $DIALOG --title "$TITLE" \
            --inputbox "IP for host number $COUNTER" 20 80 "127.0.0.1" 2> $TEMPFILE
    RETVAL=$?
    case $RETVAL in
        0)
            IPTMP1=$(cat $TEMPFILE)
            if validIp $IPTMP1
            then
                IPTMP=$IPTMP1
            else
                infoDialog "\Z5IP address is not valid. \Zb\Z1Exit\Zn" && exit 1
            fi;;
        1)
            infoDialog "Cancel. Exit" && exit 1;;
        255)
            infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function ipOfRouter() {
    $DIALOG --title "$TITLE" \
            --inputbox "IP for router" 20 80 "${IP[1]}" 2> $TEMPFILE
    RETVAL=$?
    case $RETVAL in
        0)
            IPTMP=$(cat $TEMPFILE)
            if validIp $IPTMP
            then
                ROUTER_IP=$IPTMP
            else
                infoDialog "\Z5IP address is not valid. \Zb\Z1Exit\Zn" && exit 1
            fi;;
        1)
            infoDialog "Cancel. Exit" && exit 1;;
        255)
            infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function ipOfManager() {
    $DIALOG --title "$TITLE" \
            --inputbox "IP for manager" 20 80 "${IP[1]}" 2> $TEMPFILE
    RETVAL=$?
    case $RETVAL in
        0)
            IPTMP=$(cat $TEMPFILE)
            if validIp $IPTMP
            then
                MANAGER_IP=$IPTMP
            else
                infoDialog "\Z5IP address is not valid. \Zb\Z1Exit\Zn" && exit 1
            fi;;
        1)
            infoDialog "Cancel. Exit" && exit 1;;
        255)
            infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function numberOfHosts() {
    $DIALOG --title "$TITLE" \
            --inputbox "Number of hosts" 20 80 1 2> $TEMPFILE
    RETVAL=$?
    case $RETVAL in
        0)
            HOSTSTMP=$(cat $TEMPFILE)
            if [[ $HOSTSTMP =~ $HOSTSREG ]]
            then
                HOSTS=$HOSTSTMP
            else
                clear && echo -e $RED"Invalid number of hosts. Exit"$DEF && exit 1
            fi;;
        1)
            clear && infoDialog "Cancel. Exit" && exit 1;;
        255)
            clear && infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function numberOfNodes() {
    # $1 - type of manager
    if
        [[ $1 == 'r' ]]
    then
        $DIALOG --title "$TITLE" \
                --inputbox "Number of nodes (4 - 10)" 20 80 4 2> $TEMPFILE
        RETVAL=$?
        case $RETVAL in
            0)
                NODESTMP1=$(cat $TEMPFILE)
                if [[ $NODESTMP1 -ge 4 && $NODESTMP1 =~ $NODESREG ]]
                then
                    NODESTMP=$NODESTMP1
                else
                    clear && echo -e $RED"Nodes may be greater or equal 4. Exit"$DEF && exit 1
                fi;;
            1)
                clear && infoDialog "Cancel. Exit" && exit 1;;
            255)
                clear && infoDialog "Cancel. Exit" && exit 1;;
        esac
    else
        $DIALOG --title "$TITLE" \
                --inputbox "Number of nodes (1 - 10)" 20 80 1 2> $TEMPFILE
        RETVAL=$?
        case $RETVAL in
            0)
                NODESTMP1=$(cat $TEMPFILE)
                if [[ $NODESTMP1 =~ $NODESREG ]]
                then
                    NODESTMP=$NODESTMP1
                else
                    clear && echo -e $RED"Nodes may be from 1 to 10. Exit"$DEF && exit 1
                fi;;
            1)
                clear && infoDialog "Cancel. Exit" && exit 1;;
            255)
                clear && infoDialog "Cancel. Exit" && exit 1;;
        esac
    fi
}

function isData() {
    $DIALOG --title "$TITLE" \
            --yesno "Data on this host?" 20 80
    case $? in
        0)
            ISDATATMP=Y;;
        1)
            ISDATATMP=N;;
        255)
            clear && infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function typeOfManager() {
    $DIALOG --title "$TITLE" \
            --menu "Type of manager" 20 80 8 \
            "n" "rmanager-rnd (sends to one of random client)" \
            "m" "smanager (sends to all connected)" \
            "r" "rmanager-rnd (sends to one of random client)" 2> $TEMPFILE
    RETVAL=$?
    case $RETVAL in
        0)
            MANAGER_TYPE=$(cat $TEMPFILE);;
        1)
            clear && infoDialog "Cancel. Exit" && exit 1;;
        255)
            clear && infoDialog "Cancel. Exit" && exit 1;;
    esac
}

function checkCreateIni() {
    # $1 - type of manager
    case $1 in
        n|r)
            $DIALOG --title "$TITLE" \
                    --yesno "Create ini files?" 20 80
            case $? in
                0)
                    CREATE_INI=Y;;
                1)
                    CREATE_INI=N;;
                255)
                    clear && infoDialog "Cancel. Exit" && exit 1;;
            esac;;
        m)
            $DIALOG --title "$TITLE" \
                    --defaultno --yesno "Create ini files?" 20 80
            case $? in
                0)
                    CREATE_INI=Y;;
                1)
                    CREATE_INI=N;;
                255)
                    clear && infoDialog "Cancel. Exit" && exit 1;;
            esac;;
    esac
}

function replicasPoolAdminPorts () {
    # $1 - name of manager, $2 - count of nodes
    for (( COUNT=0; COUNT<$2; COUNT++ ))
    do
        PORT=$[$1+$COUNT]
        if [[ ! $PORTS ]]
        then
            PORTS=$PORT
        else
            PORTS=${PORTS}' '$PORT
        fi
    done
    echo $PORTS
}

function search () {
    # $1 - filename, where search
    # $2 - search string
    while read line
    do
        if [[ $line == $2 ]]
        then
            echo true
            exit 1
        fi
    done < $1
}
# END OF FINCTIONS #

# CHECK DIALOG INSTALL #
if [[ -z $(which $DIALOG) ]]
then
    if [[ -f '/etc/debian_version' ]]
    then
        echo -e $RED"Dialog is not installed, install dialog ("$BLUE"sudo apt-get install dialog"$RED") and run "$BLUE"$0"$RED" again"$DEF
        exit 1
    elif [[ -f '/etc/redhat-release' || '/etc/centos-release' ]]
    then
        echo -e $RED"Dialog is not installed, install dialog ("$BLUE"sudo yum install dialog"$RED") and run "$BLUE"$0"$RED" again"$DEF
        exit 1
    else
        echo -e $RED"Dialog is not installed, install dialog and run "$BLUE"$0"$RED" again"$DEF
        exit 1
    fi
fi

# CHECK ARCHIVE WITH TEMPLATES #
if [[ ! -d $TEMPLATES ]]
then
    infoDialog "\Z5Directory with templates not found. \Z1Aborting\Zn"
    clear
    exit
fi
# END OF CHECK ARCHIVE WITH TEMPLATES #

# GET VARIABLES #
if [[ $# -ne 0 ]]
then
# FROM FILES #
    FILE=$1
    if [[ -a $FILE ]]
    then
        while read line
        do
            echo > /dev/null
        done < $FILE
    fi
else
# FROM STDIN #
    # REMOVE CURRENT CFG OR NOT #
    removeCurrentCfg
    # GET OUT PATH #
    tmpPath
    COUNTER=1
    typeOfManager
    numberOfHosts
    if [[ $HOSTS -eq 1 ]]
    then
        numberOfNodes $MANAGER_TYPE
        NODES=$NODESTMP
        checkCreateIni $MANAGER_TYPE
    else
        while [[  $COUNTER -le $HOSTS ]]
        do
            ipOfHosts
            IP[$COUNTER]=$IPTMP
            isData
            ISDATA[$COUNTER]=$ISDATATMP
            if [[ $ISDATATMP == 'Y' ]]
            then
                numberOfNodes $MANAGER_TYPE
                NODES[$COUNTER]=$NODESTMP
            fi
            let COUNTER=COUNTER+1
        done
        ipOfRouter
        ipOfManager
        checkCreateIni $MANAGER_TYPE

    fi
fi
# END OF GET VARIABLES #

# CREATE CONFIGS #
# DELETE OLD CONFIGS #
rm -rf $TMPDIR

if [[ $HOSTS -eq 1 ]]
then
# SINGLE SYSTEM #
    N_NAME=localhost_n_cfg.sh
    M_NAME=localhost_m_cfg.sh
    R_NAME=localhost_r_cfg.sh
    mkdir -p $TMPDIR/$CFG
    mkdir -p $TMPDIR/$INI
    # CP current_cfg.sh TO TEMPLATES #
    if [[ -f ../cfg/current_cfg.sh && $RMCURCFG == use ]]
    then
        cp ../cfg/current_cfg.sh $TMPDIR/$CFG
    else
        cp $TEMPLATES/$SINGLE/$CFG/current_cfg.sh $TMPDIR/$CFG/
    fi
    if [[ $MANAGER_TYPE == n ]]
    then
        # SEARCH IN current_cfg.sh DUBLE CONFIG #
        DUBLE=$(search $TMPDIR/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
        if [[ -z $DUBLE ]]
        then
            # ADD TO current_cfg.sh #
            sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/g' $TMPDIR/$CFG/current_cfg.sh
        fi
        # COPY N-CONFIG TO TEMPLATE DIRECTORY #
        cp $TEMPLATES/$SINGLE/$CFG/n_cfg.sh $TMPDIR/$CFG/$N_NAME
        # PORTS OF NODES #
        PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_N $NODES)
        sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/$CFG/$N_NAME
        # NODE_APP_LOG_PREFIX #
        sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-\"/' $TMPDIR/$CFG/$N_NAME
        # MAKE node_poolX.ini #
        for (( COUNTNODES=1; COUNTNODES<=$NODES; COUNTNODES++ ))
        do
            if [[ -z $RPORT ]]
            then
                RPORT=$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))
            else
                RPORT="$RPORT,$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))"
            fi
            if [[ $CREATE_INI == 'Y' ]]
            then
                cp $TEMPLATES/$SINGLE/$INI/node_poolX.ini $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NODE_HOST_#/localhost/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))'/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NOTIFICATIONIP_#/localhost/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NOTIFICATIONPORT_#/5500/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
            fi
        done
        sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"localhost\""'/' $TMPDIR/$CFG/$N_NAME
        sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/$CFG/$N_NAME
    elif [[ $MANAGER_TYPE == m ]]
    then
        # SEARCH IN current_cfg.sh DUBLE CONFIG #
        DUBLE=$(search $TMPDIR/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
        if [[ -z $DUBLE ]]
        then
            # ADD TO current_cfg.sh #
            sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/g' $TMPDIR/$CFG/current_cfg.sh
        fi
        DUBLE=$(search $TMPDIR/$CFG/current_cfg.sh "source ../cfg/$M_NAME")
        if [[ -z $DUBLE ]]
        then
            # ADD TO current_cfg.sh #
            sed -i 's/#_CONFIGFILE_M_#/'"source ..\/cfg\/$M_NAME\n  #_CONFIGFILE_M_#"'/g' $TMPDIR/$CFG/current_cfg.sh
        fi
        # COPY M-CONFIG TO TEMPLATE DIRECTORY #
        cp $TEMPLATES/$SINGLE/$CFG/n_cfg.sh $TMPDIR/$CFG/$N_NAME
        cp $TEMPLATES/$SINGLE/$CFG/m_cfg.sh $TMPDIR/$CFG/$M_NAME
        # PORTS OF NODES #
        PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_N $NODES)
        sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/$CFG/$N_NAME
        PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_M $NODES)
        sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/$CFG/$M_NAME
        # NODE_APP_LOG_PREFIX #
        sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-\"/' $TMPDIR/$CFG/$N_NAME
        sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"m-\"/' $TMPDIR/$CFG/$M_NAME
        # MAKE node_poolX.ini #
        for (( COUNTNODES=1; COUNTNODES<=$NODES; COUNTNODES++ ))
        do
            if [[ -z $RPORT ]]
            then
                RPORT=$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))
            else
                RPORT="$RPORT,$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))"
            fi
            if [[ $CREATE_INI == 'Y' ]]
            then
                cp $TEMPLATES/$SINGLE/$INI/node_poolX.ini $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NODE_HOST_#/localhost/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))'/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NOTIFICATIONIP_#/localhost/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
                sed -i 's/#_NOTIFICATIONPORT_#/5500/' $TMPDIR/$INI/node_pool$COUNTNODES.ini
            fi
        done
        sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"localhost\""'/' $TMPDIR/$CFG/$M_NAME
        sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/$CFG/$M_NAME
    elif [[ $MANAGER_TYPE == r ]]
    then
        # SEARCH IN current_cfg.sh DUBLE CONFIG #
        DUBLE=$(search $TMPDIR/$CFG/current_cfg.sh "source ../cfg/$R_NAME")
        if [[ -z $DUBLE ]]
        then
            # ADD TO current_cfg.sh #
            sed -i 's/#_CONFIGFILE_R_#/'"source ..\/cfg\/$R_NAME\n  #_CONFIGFILE_R_#"'/g' $TMPDIR/$CFG/current_cfg.sh
        fi
        # COPY R-CONFIG TO TEMPLATE DIRECTORY #
        cp $TEMPLATES/$SINGLE/$CFG/r_cfg.sh $TMPDIR/$CFG/$R_NAME
        # PORTS OF NODES #
        PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_R $NODES)
        sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/$CFG/$R_NAME
        # NODE_APP_LOG_PREFIX #
        sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"NODE_APP_LOG_PREFIX=\"r-\"/' $TMPDIR/$CFG/$R_NAME
        # MAKE node_pool_rX.ini #
        for (( COUNTNODES=1; COUNTNODES<=$NODES; COUNTNODES++ ))
        do
            if [[ -z $RPORT ]]
            then
                RPORT=$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))
            else
                RPORT="$RPORT,$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))"
            fi
            if [[ $CREATE_INI == 'Y' ]]
            then
                cp $TEMPLATES/$SINGLE/$INI/node_pool_rX.ini $TMPDIR/$INI/node_pool_r$COUNTNODES.ini
                sed -i 's/#_NODE_HOST_#/localhost/' $TMPDIR/$INI/node_pool_r$COUNTNODES.ini
                sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))'/' $TMPDIR/$INI/node_pool_r$COUNTNODES.ini
                sed -i 's/#_NOTIFICATIONIP_#//' $TMPDIR/$INI/node_pool_r$COUNTNODES.ini
                sed -i 's/#_NOTIFICATIONPORT_#//' $TMPDIR/$INI/node_pool_r$COUNTNODES.ini
            fi
        done
        sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"localhost\""'/' $TMPDIR/$CFG/$R_NAME
        sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/$CFG/$R_NAME
    else
        infoDialog "\Z5Fail\Zn"
        clear
        exit 1
    fi
# END OF SINGLE SYSTEM #

else
# MULTI SYSTEM #
    mkdir $TMPDIR
    for (( COUNT=1; COUNT<=$HOSTS; COUNT++ ))
    do
        mkdir -p $TMPDIR/${IP[$COUNT]}/$CFG
        mkdir -p $TMPDIR/${IP[$COUNT]}/$INI
        unset RPORT
        unset RHOST
        N_NAME=${IP[$COUNT]}_n_cfg.sh
        M_NAME=${IP[$COUNT]}_m_cfg.sh
        R_NAME=${IP[$COUNT]}_r_cfg.sh
        if [[ ${IP[$COUNT]} == $MANAGER_IP && ${IP[$COUNT]} == $ROUTER_IP && ${ISDATA[$COUNT]} == 'Y' ]]
        then
            # MANAGER + ROUTER + DATA HOST #
            # CP current_cfg.sh TO TEMPLATES #
            if [[ -f ../cfg/current_cfg.sh && $RMCURCFG == use ]]
            then
                cp ../cfg/current_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/
            else
                cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$CFG/current_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/
            fi
            if [[ $MANAGER_TYPE == n ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$CFG/n_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # PORTS OF NODES #
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_N ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"NODE_APP_LOG_PREFIX=\"n-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RHOSTTEMP
                    unset RPORTTEMP
                    if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                    then
                        for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                        do
                            if [[ -z $RPORTTEMP ]]
                            then
                                RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))
                            else
                                RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))"
                            fi
                            if [[ -z $RHOSTTEMP ]]
                            then
                                RHOSTTEMP=${IP[$COUNTHOSTS]}
                            else
                                RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                            fi
                        done
                        if [[ -z $RPORT ]]
                        then
                            RPORT=$RPORTTEMP
                        else
                            RPORT="$RPORT,$RPORTTEMP"
                        fi

                        if [[ -z $RHOST ]]
                        then
                            RHOST=$RHOSTTEMP
                        else
                            RHOST="$RHOST,$RHOSTTEMP"
                        fi
                    fi
                done
                sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # MAKE node_poolX.ini #
                if [[ $CREATE_INI == 'Y' ]]
                then
                    for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNT]}; COUNTNODES++ ))
                    do
                        cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$INI/node_poolX.ini $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_HOST_#/localhost/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONIP_#/localhost/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONPORT_#/5500/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                    done
                fi
            elif [[ $MANAGER_TYPE == m ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$M_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_M_#/'"source ..\/cfg\/$M_NAME\n  #_CONFIGFILE_M_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG AND N-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$CFG/n_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$CFG/m_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # PORTS OF NODES #
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_N ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_M ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"m-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RHOSTTEMP
                    unset RPORTTEMP
                    if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                    then
                        for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                        do
                            if [[ -z $RPORTTEMP ]]
                            then
                                RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))
                            else
                                RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))"
                            fi
                            if [[ -z $RHOSTTEMP ]]
                            then
                                RHOSTTEMP=${IP[$COUNTHOSTS]}
                            else
                                RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                            fi
                        done
                        if [[ -z $RPORT ]]
                        then
                            RPORT=$RPORTTEMP
                        else
                            RPORT="$RPORT,$RPORTTEMP"
                        fi

                        if [[ -z $RHOST ]]
                        then
                            RHOST=$RHOSTTEMP
                        else
                            RHOST="$RHOST,$RHOSTTEMP"
                        fi
                    fi
                done
                sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                unset RPORT
                unset RHOST
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RHOSTTEMP
                    unset RPORTTEMP
                    if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                    then
                        for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                        do
                            if [[ -z $RPORTTEMP ]]
                            then
                                RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))
                            else
                                RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))"
                            fi
                            if [[ -z $RHOSTTEMP ]]
                            then
                                RHOSTTEMP=${IP[$COUNTHOSTS]}
                            else
                                RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                            fi
                        done
                        if [[ -z $RPORT ]]
                        then
                            RPORT=$RPORTTEMP
                        else
                            RPORT="$RPORT,$RPORTTEMP"
                        fi

                        if [[ -z $RHOST ]]
                        then
                            RHOST=$RHOSTTEMP
                        else
                            RHOST="$RHOST,$RHOSTTEMP"
                        fi
                    fi
                done
                sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # MAKE node_poolX.ini #
                if [[ $CREATE_INI == 'Y' ]]
                then
                    for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNT]}; COUNTNODES++ ))
                    do
                        cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$INI/node_poolX.ini $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_HOST_#/localhost/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONIP_#/localhost/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONPORT_#/5500/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                    done
                fi
            elif [[ $MANAGER_TYPE == r ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$R_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_R_#/'"source ..\/cfg\/$R_NAME\n  #_CONFIGFILE_R_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY R-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$CFG/r_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # PORTS OF NODES #
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_R ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"r-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RHOSTTEMP
                    unset RPORTTEMP
                    if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                    then
                        for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                        do
                            if [[ -z $RPORTTEMP ]]
                            then
                                RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))
                            else
                                RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))"
                            fi
                            if [[ -z $RHOSTTEMP ]]
                            then
                                RHOSTTEMP=${IP[$COUNTHOSTS]}
                            else
                                RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                            fi
                        done
                        if [[ -z $RPORT ]]
                        then
                            RPORT=$RPORTTEMP
                        else
                            RPORT="$RPORT,$RPORTTEMP"
                        fi

                        if [[ -z $RHOST ]]
                        then
                            RHOST=$RHOSTTEMP
                        else
                            RHOST="$RHOST,$RHOSTTEMP"
                        fi
                    fi
                done
                sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # MAKE node_pool_rX.ini #
                if [[ $CREATE_INI == 'Y' ]]
                then
                    for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNT]}; COUNTNODES++ ))
                    do
                        cp $TEMPLATES/$MULTI/$ALLHOSTDIR/$INI/node_pool_rX.ini $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NODE_HOST_#/localhost/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONIP_#//' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONPORT_#//' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                    done
                fi
            else
                infoDialog "\Z5Fail\Zn"
                clear
                exit 1
            fi
        elif [[ ${IP[$COUNT]} == $MANAGER_IP && ${IP[$COUNT]} != $ROUTER_IP && ${ISDATA[$COUNT]} == 'Y' ]]
        then
            # MANAGER + DATA - ROUTER #
            infoDialog "\Z4manager+data-router\Zn"
        elif [[ ${IP[$COUNT]} != $MANAGER_IP && ${IP[$COUNT]} == $ROUTER_IP && ${ISDATA[$COUNT]} == 'Y' ]]
        then
            # ROUTER + DATA - MANAGER #
            infoDialog "\Z4router+data-manager\Zn"
        elif [[ ${IP[$COUNT]} != $MANAGER_IP && ${IP[$COUNT]} != $ROUTER_IP && ${ISDATA[$COUNT]} == 'Y' ]]
        then
            # DATA ONLY #
            # CP current_cfg.sh TO TEMPLATES #
            if [[ -f ../cfg/current_cfg.sh && $RMCURCFG == use ]]
            then
                cp ../cfg/current_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/
            else
                cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$CFG/current_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/
            fi
            if [[ $MANAGER_TYPE == n ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$CFG/n_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # PORTS OF NODES AND MANAGER #
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_N ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/__MANAGER__/'"\"$MANAGER_IP\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                sed -i 's/#_RHOST_#/REMOTE_HOSTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_RPORT_#/REMOTE_PORTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # MAKE node_poolX.ini #
                if [[ $CREATE_INI == 'Y' ]]
                then
                    for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNT]}; COUNTNODES++ ))
                    do
                        cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$INI/node_poolX.ini $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_HOST_#/'${IP[$COUNT]}'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONIP_#/'$MANAGER_IP'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONPORT_#/5500/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                    done
                fi
            elif [[ $MANAGER_TYPE == m ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$M_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_M_#/'"source ..\/cfg\/$M_NAME\n  #_CONFIGFILE_M_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG AND M-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$CFG/n_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$CFG/m_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # PORTS OF NODES AND MANAGER #
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_N ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/__MANAGER__/'"\"$MANAGER_IP\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_M ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                sed -i 's/__MANAGER__/'"\"$MANAGER_IP\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                sed -i 's/#_RHOST_#/REMOTE_HOSTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_RPORT_#/REMOTE_PORTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_RHOST_#/REMOTE_HOSTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                sed -i 's/#_RPORT_#/REMOTE_PORTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"m-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # MAKE node_poolX.ini #
                if [[ $CREATE_INI == 'Y' ]]
                then
                    for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNT]}; COUNTNODES++ ))
                    do
                        cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$INI/node_poolX.ini $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_HOST_#/'${IP[$COUNT]}'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONIP_#/'$MANAGER_IP'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONPORT_#/5500/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool$COUNTNODES.ini
                done
                fi
            elif [[ $MANAGER_TYPE == r ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$R_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_R_#/'"source ..\/cfg\/$R_NAME\n  #_CONFIGFILE_R_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY R-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$CFG/r_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # PORTS OF NODES AND MANAGER #
                PORTSLIST=$(replicasPoolAdminPorts REPLICAS_POOL_ADMIN_PORTS_R ${NODES[$COUNT]})
                sed -i 's/__PORTLIST__/'"$PORTSLIST"'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                sed -i 's/__MANAGER__/'"\"$MANAGER_IP\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME

                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                sed -i 's/#_RHOST_#/REMOTE_HOSTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                sed -i 's/#_RPORT_#/REMOTE_PORTS=""/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"r-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # MAKE node_poolX.ini #
                if [[ $CREATE_INI == 'Y' ]]
                then
                    for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNT]}; COUNTNODES++ ))
                    do
                        cp $TEMPLATES/$MULTI/$DATAHOSTDIR/$INI/node_pool_rX.ini $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NODE_HOST_#/'${IP[$COUNT]}'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NODE_PORT_#/'$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))'/' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONIP_#//' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                        sed -i 's/#_NOTIFICATIONPORT_#//' $TMPDIR/${IP[$COUNT]}/$INI/node_pool_r$COUNTNODES.ini
                    done
                fi
            else
                infoDialog "\Z5Fail\Zn"
                clear
                exit 1
            fi
        elif [[ ${IP[$COUNT]} == $MANAGER_IP && ${IP[$COUNT]} == $ROUTER_IP && ${ISDATA[$COUNT]} == 'N' ]]
        then
            # ROUTER+MANAGER ONLY #
            # CP current_cfg.sh TO TEMPLATES #
            if [[ -f ../cfg/current_cfg.sh && $RMCURCFG == use ]]
            then
                cp ../cfg/current_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/
            else
                cp $TEMPLATES/$MULTI/$RMHOST/$CFG/current_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/
            fi
            if [[ $MANAGER_TYPE == n ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$RMHOST/$CFG/n_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RPORT
                    unset RHOST
                    for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                    do
                        unset RHOSTTEMP
                        unset RPORTTEMP
                        if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                        then
                            for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                            do
                                if [[ -z $RPORTTEMP ]]
                                then
                                    RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))
                                else
                                    RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))"
                                fi
                                if [[ -z $RHOSTTEMP ]]
                                then
                                    RHOSTTEMP=${IP[$COUNTHOSTS]}
                                else
                                    RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                                fi
                            done
                            if [[ -z $RPORT ]]
                            then
                                RPORT=$RPORTTEMP
                            else
                                RPORT="$RPORT,$RPORTTEMP"
                            fi

                            if [[ -z $RHOST ]]
                            then
                                RHOST=$RHOSTTEMP
                            else
                                RHOST="$RHOST,$RHOSTTEMP"
                            fi
                        fi
                    done
                    sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                    sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                done
            elif [[ $MANAGER_TYPE == m ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$N_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_N_#/'"source ..\/cfg\/$N_NAME\n  #_CONFIGFILE_N_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$M_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_M_#/'"source ..\/cfg\/$M_NAME\n  #_CONFIGFILE_M_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$RMHOST/$CFG/n_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                cp $TEMPLATES/$MULTI/$RMHOST/$CFG/m_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"n-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"m-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RPORT
                    unset RHOST
                    for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                    do
                        unset RHOSTTEMP
                        unset RPORTTEMP
                        if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                        then
                            for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                            do
                                if [[ -z $RPORTTEMP ]]
                                then
                                    RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))
                                else
                                    RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_N+$COUNTNODES-1))"
                                fi
                                if [[ -z $RHOSTTEMP ]]
                                then
                                    RHOSTTEMP=${IP[$COUNTHOSTS]}
                                else
                                    RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                                fi
                            done
                            if [[ -z $RPORT ]]
                            then
                                RPORT=$RPORTTEMP
                            else
                                RPORT="$RPORT,$RPORTTEMP"
                            fi

                            if [[ -z $RHOST ]]
                            then
                                RHOST=$RHOSTTEMP
                            else
                                RHOST="$RHOST,$RHOSTTEMP"
                            fi
                        fi
                    done
                    sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                    sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$N_NAME
                    unset RPORT
                    unset RHOST
                    for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                    do
                        unset RHOSTTEMP
                        unset RPORTTEMP
                        if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                        then
                            for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                            do
                                if [[ -z $RPORTTEMP ]]
                                then
                                    RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))
                                else
                                    RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_M+$COUNTNODES-1))"
                                fi
                                if [[ -z $RHOSTTEMP ]]
                                then
                                    RHOSTTEMP=${IP[$COUNTHOSTS]}
                                else
                                    RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                                fi
                            done
                            if [[ -z $RPORT ]]
                            then
                                RPORT=$RPORTTEMP
                            else
                                RPORT="$RPORT,$RPORTTEMP"
                            fi

                            if [[ -z $RHOST ]]
                            then
                                RHOST=$RHOSTTEMP
                            else
                                RHOST="$RHOST,$RHOSTTEMP"
                            fi
                        fi
                    done
                    sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                    sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$M_NAME
                done
            elif [[ $MANAGER_TYPE == r ]]
            then
                # SEARCH IN current_cfg.sh DUBLE CONFIG #
                DUBLE=$(search $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh "source ../cfg/$R_NAME")
                if [[ -z $DUBLE ]]
                then
                    # ADD TO current_cfg.sh #
                    sed -i 's/#_CONFIGFILE_R_#/'"source ..\/cfg\/$R_NAME\n  #_CONFIGFILE_R_#"'/g' $TMPDIR/${IP[$COUNT]}/$CFG/current_cfg.sh
                fi
                # COPY N-CONFIG TO TEMPLATE DIRECTORY #
                cp $TEMPLATES/$MULTI/$RMHOST/$CFG/r_cfg.sh $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # NODE_APP_LOG_PREFIX #
                sed -i 's/#_NODE_APP_LOG_PREFIX_#/NODE_APP_LOG_PREFIX=\"r-'${#IP[@]}'h-'${IP[$COUNT]}'-\"/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                # CREATE RHOST AND RPORT FOR X_cfg.sh #
                for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                do
                    unset RPORT
                    unset RHOST
                    for (( COUNTHOSTS=1; COUNTHOSTS<=$HOSTS; COUNTHOSTS++ ))
                    do
                        unset RHOSTTEMP
                        unset RPORTTEMP
                        if [[ ${IP[$COUNTHOSTS]} != $MANAGER_IP ]]
                        then
                            for (( COUNTNODES=1; COUNTNODES<=${NODES[$COUNTHOSTS]}; COUNTNODES++ ))
                            do
                                if [[ -z $RPORTTEMP ]]
                                then
                                    RPORTTEMP=$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))
                                else
                                    RPORTTEMP="$RPORTTEMP,$(($REPLICAS_POOL_ADMIN_PORTS_R+$COUNTNODES-1))"
                                fi
                                if [[ -z $RHOSTTEMP ]]
                                then
                                    RHOSTTEMP=${IP[$COUNTHOSTS]}
                                else
                                    RHOSTTEMP="$RHOSTTEMP,${IP[$COUNTHOSTS]}"
                                fi
                            done
                            if [[ -z $RPORT ]]
                            then
                                RPORT=$RPORTTEMP
                            else
                                RPORT="$RPORT,$RPORTTEMP"
                            fi

                            if [[ -z $RHOST ]]
                            then
                                RHOST=$RHOSTTEMP
                            else
                                RHOST="$RHOST,$RHOSTTEMP"
                            fi
                        fi
                    done
                    sed -i 's/#_RHOST_#/'"REMOTE_HOSTS=\"$RHOST\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                    sed -i 's/#_RPORT_#/'"REMOTE_PORTS=\"$RPORT\""'/' $TMPDIR/${IP[$COUNT]}/$CFG/$R_NAME
                done
            else
                infoDialog "\Z5Fail\Zn"
                clear
                exit 1
            fi
        else
            # ALL IN SINGLE HOST #
            infoDialog "\Z4All in single host\Zn"
        fi
    done
fi

infoDialog 'Complete, config files in "'$TMPDIR'"'
#clear
exit 0
#echo -e $BLUE'Complete'$DEF