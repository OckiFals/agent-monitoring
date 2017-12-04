#! /usr/bin/env pyhton
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import time, psutil, os, json, socket
from uuid import getnode as get_mac
from datetime import datetime


class ClientProtocol(DatagramProtocol):
    counter = 0

    def startProtocol(self):
        print 'client started'
        host = "127.0.0.1"
        self.transport.connect('127.0.0.1', 9964)
        mac = getmac()
        hostname = gethostname()
        response = os.system("ping -c 1 " + host)
        if response == 0:
            avai = "Up"
        else:
            avai = "Down"
        data = {
            'hostname': hostname,
            'mac': mac,
            'status': avai,
            'phase': 'Off'
        }
        result = json.dumps(data)
        self.transport.write(result)

    def doStop(self):
        hostname = gethostname()
        mac = getmac()
        data = {
            'hostname': hostname,
            'mac': mac,
            'status': "Down"
        }
        result = json.dumps(data)
        self.transport.write(result)
        print "Client Stopped"

    def stopProtocol(self):
        print 'client stopped'

    def datagramReceived(self, datagram, (host, port)):
        command = json.loads(datagram)
        print 'Datagram received: ', repr(command)

        break_interupt = False

        # FIXME kalau tabel monitor kosong gak mau jalan
        if None is not command:
            starttime = datetime.strptime(command[4], "%Y/%m/%d %H:%M:%S.%f")
            endtime = datetime.strptime(command[5], "%Y/%m/%d %H:%M:%S.%f")
            now = datetime.now()

            if command[2] == 1:
                callback = getResource()
            elif command[2] == 2:
                callback = getNetwork()
            elif command[2] == 3:
                callback = ping()
            else:  # command[2] == 4
                callback = getDisk()

            while starttime < now < endtime and 'active' == command[7]:
                now = datetime.now()
                self.counter += 1
                if 0 == self.counter % 3:
                    print 'exiting for loop'
                    break_interupt = True
                    break
                print 'sending...'
                self.transport.write(callback)
                time.sleep(command[3])
        print 'waitting command'
        self.transport.write(json.dumps({'type': 5}))

        if not break_interupt:
            time.sleep(command[3])
        else:
            time.sleep(1)

def getmac():
    mac = get_mac()
    macstring = ':'.join(("%012X" % mac)[i:i + 2] for i in range(0, 12, 2))
    return macstring


def gethostname():
    hostname = socket.gethostname()
    return hostname


def ping():
    _type = 3
    host = "127.0.0.1"
    response = os.system("ping -c 1 " + host)
    if response == 0:
        avai = "Device is up"
    else:
        avai = "Device is down"
    status = {
        'type': _type,
        'mac': getmac(),
        'host': host,
        'avai': avai
    }
    result = json.dumps(status)
    return result


def getNetwork():
    _type = 2
    bytesent = psutil.net_io_counters().bytes_sent
    byterecv = psutil.net_io_counters().bytes_recv
    pktsent = psutil.net_io_counters().packets_sent
    pktrcv = psutil.net_io_counters().packets_recv

    net = {
        'type': _type,
        'mac': getmac(),
        'bytesent': bytesent,
        'byterecv': byterecv,
        'pktsent': pktsent,
        'pktrcv': pktrcv
    }
    result = json.dumps(net)

    return result


def getResource():
    _type = 1
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().available
    usedmem = psutil.virtual_memory().used
    swap = psutil.swap_memory().free
    res = {
        'type': _type,
        'mac': get_mac(),
        'cpu': cpu,
        'memory': memory,
        'usedmem': usedmem,
        'swap': swap
    }
    result = json.dumps(res)
    return result


def getDisk():
    _type = 4
    disk_used = (psutil.disk_usage('/')[1]) / 1024
    disk_free = (psutil.disk_usage('/')[2]) / 1024
    read_bytes = psutil.disk_io_counters(perdisk=False)[2] / 1024
    write_bytes = psutil.disk_io_counters(perdisk=False)[3] / 1024
    disk = {
        'type': _type,
        'mac': get_mac(),
        'disk_used': disk_used,
        'disk_free': disk_free,
        'read_bytes': read_bytes,
        'write_bytes': write_bytes
    }
    result = json.dumps(disk)
    return result


def main():
    protocol = ClientProtocol()
    reactor.listenUDP(0, protocol)
    reactor.run()


if __name__ == '__main__':
    main()
