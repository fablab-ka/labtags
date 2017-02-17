#first time: git clone https://github.com/fablab-ka/labtags.git
#cron: 
#
#

case "$1" in
start)
    echo "Starting BLE/iTag Gateway"
    cd /usr/local/lib/python2.7/dist-packages/labtags/blot-gateway
    python gateway.py &
 ;;
stop)
    echo "Stopping BLE/iTag Gateway"
    sudo pkill -f gateway.py
;;
update)
    echo "Stopping BLE/iTag Gateway"
	sudo pkill -f gateway.py
	echo "Update BLE Gateway"
	git pull
;;
auto)
    echo "Stopping BLE/iTag Gateway"
	sudo pkill -f gateway.py
	echo "Update BLE Gateway"
	git pull
	echo "Starting BLE/iTag Gateway"
	python ./blot-gateway/gateway.py &
;;
*)
    echo "Usage: /etc/init.d/xxxx {start|stop|update|auto}"
    exit 1
;;
esac

exit 0