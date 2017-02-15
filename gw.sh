#first time: git clone https://github.com/fablab-ka/labtags.git
#cron: 
#
#

case "$1" in
start)
    echo "Starting BLE Gateway"
    cd /usr/local/lib/python2.7/dist-packages/labtags/blot-gateway
    python gateway.py &
 ;;
stop)
    echo "Stopping BLE Gateway"
    sudo pkill -f gateway.py
;;
update)
    echo "Stopping BLE Gateway"
    #sudo killall gateway
	sudo pkill -f gateway.py
	echo "Update BLE Gateway"
	git pull
;;
*)
    echo "Usage: /etc/init.d/xxxx {start|stop}"
    exit 1
;;
esac

exit 0





