from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, threads
import time, psutil, os, json, socket
from uuid import getnode as get_mac


class ClientProtocol(DatagramProtocol):
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
        status = (hostname, mac, avai, "Off")
        result = json.dumps(status)
        self.transport.write(result)

    def doStop(self):
        hostname = gethostname()
        mac = getmac()
        status = (hostname, mac, "Down")
        result = json.dumps(status)
        self.transport.write(result)
        print "Client Stopped"

    def stopProtocol(self):
        print 'client stopped'

    def datagramReceived(self, datagram, (host, port)):
        command = json.loads(datagram)
        print 'Datagram received: ', repr(command)
        handler = Handler(self.transport, host, port)
        d = threads.deferToThread(handler.handleMessage, command)
        duration = ((command[5] - command[4]) / command[3])

        for i in range(duration):
            if command[2] == 1:
                d.addCallback(handler.sendRes)
            elif command[2] == 2:
                d.addCallback(handler.sendNetwork)
                # time.sleep(command[3])
            elif command[2] == 3:
                d.addCallback(handler.sendPing)
            elif command[2] == 4:
                # for i in range(duration):
                d.addCallback(handler.sendDisk)
                # print command[3]
                # time.sleep(command[3])
            print "data sent"
            time.sleep(command[3])

            # print command[3]


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
    status = (_type, getmac(), host, avai)
    result = json.dumps(status)
    return result


def getNetwork():
    _type = 2
    bytesent = psutil.net_io_counters().bytes_sent
    byterecv = psutil.net_io_counters().bytes_recv
    pktsent = psutil.net_io_counters().packets_sent
    pktrcv = psutil.net_io_counters().packets_recv

    net = (_type, getmac(), bytesent, byterecv, pktsent, pktrcv)
    result = json.dumps(net)

    return result


def getResource():
    _type = 1
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().available
    usedmem = psutil.virtual_memory().used
    swap = psutil.swap_memory().free
    res = (_type, getmac(), cpu, memory, usedmem, swap)
    res_2 = {
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
    disk = (_type, getmac(), disk_used, disk_free, read_bytes, write_bytes)
    result = json.dumps(disk)
    return result


class Handler():
    def __init__(self, transport, host, port):
        self.host = host
        self.port = port
        self.transport = transport

    def handleMessage(self, command):
        print 'Handler Message: ', repr(command)
        # print command[3]
        # return command[3]

    def sendRes(self, *arg):
        # handler = Handler()
        # interval=handler.handleMessage(self.transport,host,port)
        # time.sleep(10)
        # print type(getResource())
        self.transport.write(getResource())

    def sendNetwork(self, *arg):
        # time.sleep(10)
        # print type(getNetwork())
        self.transport.write(getNetwork())

    def sendPing(self, *arg):
        # time.sleep(10)
        self.transport.write(ping())

    def sendDisk(self, *arg):
        # time.sleep(10)
        # print type(getDisk())
        self.transport.write(getDisk())

    def postHandle(self, arg):
        print 'post handling'


def main():
    protocol = ClientProtocol()
    reactor.listenUDP(0, protocol)
    reactor.run()


if __name__ == '__main__':
    main()
