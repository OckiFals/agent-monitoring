#! /usr/bin/env pyhton
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, threads
import time, json, sqlite3


class ServerProtocol(DatagramProtocol):
    def __init__(self, name, host, port):
        self.name = name
        self.loopObj = None
        self.host = host
        self.port = port

    def startProtocol(self):
        print 'server started'

    def stopProtocol(self):
        print 'server stoped'

    def datagramReceived(self, data, (host, port)):
        handler = Handler(self.transport, host, port)
        result = json.loads(data)
        d = threads.deferToThread(handler.handleMessage, result[0])
        db = sqlite3.connect("monitor.db")
        cursor = db.cursor()

        if result[0] == 1:
            cursor.execute('''INSERT INTO resource(host,date,time,cpu,memory_avail,memory_used,swap_free)
            VALUES (?,?,?,?,?,?,?);''', (
            result[1], str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")), result[2], result[3], result[4],
            result[5]))
            print "resource has been inserted to database"
            print "result %r " % (result)
        elif result[0] == 2:
            cursor.execute('''INSERT INTO network(host,date,time,byte_sent,byte_receive,packet_sent,packet_receive)
                            VALUES (?,?,?,?,?,?,?);''', (
                result[1], str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")), result[2], result[3],
                result[4], result[5]))
            print "network has been inserted to database"
            print "result %r " % (result)
        elif result[0] == 3:
            cursor.execute('''INSERT INTO availability(host,date,time,status)
                                            VALUES (?,?,?,?);''',
                           (result[1], str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")), result[3]))
            print "this is availability"
            print "result %r " % (result)
            print type(result)
        elif result[0] == 4:
            cursor.execute('''INSERT INTO disk(host,date,time,disk_used,disk_free,read_bytes,write_bytes)
                            VALUES (?,?,?,?,?,?,?);''', (
                result[1], str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")), result[2], result[3],
                result[4], result[5]))
            print "disk has been inserted to database"
            print "result %r " % (result)

        else:
            print "received from host %r , %s:%d" % (result[1], host, port)
            t = (result[1],)  # s = (result[1],)
            query = cursor.execute('''SELECT * FROM Host WHERE host=?''', t)
            count = len(query.fetchall())

            if count == 0:
                cursor.execute('''INSERT INTO host(hostname,host,status,phase) VALUES (?,?,?,?);''',
                               (result[0], result[1], result[2], result[3]))
                print "insert"
            else:
                cursor.execute('''UPDATE host SET status = ? WHERE Host = ?;''', (result[2], result[1]))
                print "update"
            print "host has been recorded"
        db.commit()
        db.close()
        d.addCallback(handler.postHandle)
        # time.sleep(10)


class Handler():
    def __init__(self, transport, host, port):
        self.host = host
        self.port = port
        self.transport = transport

    def handleMessage(self, host):
        db = sqlite3.connect("monitor.db", timeout=20)
        cursor = db.cursor()
        row = cursor.execute('''SELECT * FROM monitor ORDER BY createdat DESC ''')
        selection = row.fetchone()
        # newhost=(host,)
        # active_host=cursor.execute('''SELECT phase FROM host WHERE host=?''', newhost)
        command = json.dumps(selection)
        # c=active_host.fetchone()
        # if c[0]=='active':
        db.commit()
        db.close()
        print "confirm : "
        selection = raw_input()
        if selection == 'y':
            self.transport.write(command, (self.host, self.port))
            # cursor.execute('''UPDATE host SET phase = ? WHERE host = ?''', ('Off', host))
            print "this " + command + " has been sent "

    def postHandle(self, arg):
        print 'server post handling'


def main():
    reactor.listenUDP(9964, ServerProtocol('server', '127.0.0.1', 9964))
    reactor.run()


if __name__ == '__main__':
    main()
