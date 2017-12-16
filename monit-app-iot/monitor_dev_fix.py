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
        db = sqlite3.connect("monitor.db")
        cursor = db.cursor()
        query = cursor.execute('''SELECT * FROM Host''')
        for host in query.fetchall():
            cursor.execute(
                '''UPDATE host SET status = ?, phase = ? WHERE Host = ?;''',
                ('Down', 'stopped', host[2])
            )
            db.commit()
        db.close()

    def stopProtocol(self):
        print 'server stoped'

    def datagramReceived(self, data, (host, port)):
        handler = Handler(self.transport, host, port)
        result = json.loads(data)
        args = result.get('type') if result.get('type') else result.get('hostname')
        d = threads.deferToThread(handler.handleMessage, args)
        db = sqlite3.connect("monitor.db")
        cursor = db.cursor()

        if result.get('type') == 1:
            cursor.execute('''INSERT INTO resource(host,date,time,cpu,memory_avail,memory_used,swap_free)
            VALUES (?,?,?,?,?,?,?);''', (
                result.get('mac'), str(time.strftime("%d-%m-%Y")),
                str(time.strftime("%H:%M:%S")), result.get('cpu'), result.get('memory'),
                result.get('usedmem'),
                result.get('swap')))
            print "resource has been inserted to database"
            print "result %r " % result
        elif result.get('type') == 2:
            cursor.execute(
                '''INSERT INTO network(host,date,time,byte_sent,byte_receive,packet_sent,packet_receive)
                VALUES (?,?,?,?,?,?,?);''', (
                    result.get('mac'),
                    str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")),
                    result.get('bytesent'),
                    result.get('byterecv'),
                    result.get('pktsent'),
                    result.get('pktrcv')
                )
            )
            print "network has been inserted to database"
            print "result %r " % (result)
        elif result.get('type') == 3:
            cursor.execute(
                '''INSERT INTO availability(host,date,time,status)
                VALUES (?,?,?,?);''',
                (result.get('mac'),
                 str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")),
                 result.get('avai'))
            )
            print "this is availability"
            print "result %r " % (result)
            print type(result)
        elif result.get('type') == 4:
            cursor.execute(
                '''INSERT INTO disk(host,date,time,disk_used,disk_free,read_bytes,write_bytes)
                VALUES (?,?,?,?,?,?,?);''', (
                    result.get('mac'), str(time.strftime("%d-%m-%Y")), str(time.strftime("%H:%M:%S")),
                    result.get('disk_used'), result.get('disk_free'),
                    result.get('read_bytes'), result.get('write_bytes'))
            )
            print "disk has been inserted to database"
            print "result %r " % result
        elif result.get('type') == 5:
            print 'agent wait for command'
        else:
            print "received from host %r , %s:%d" % (result.get('mac'), host, port)
            t = (result.get('mac'),)  # s = (result[1],)
            query = cursor.execute('''SELECT * FROM Host WHERE host=?''', t)
            count = len(query.fetchall())

            if count == 0:
                cursor.execute(
                    '''INSERT INTO host(hostname,host,status,phase) VALUES (?,?,?,?);''',
                    (result['hostname'], result['mac'], result['status'], result['phase'])
                )
                print "insert"
            else:
                cursor.execute(
                    '''UPDATE host SET status = ? WHERE Host = ?;''',
                    (result['status'], result['hostname'])
                )
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
        # FIXME kalau tabel host kosong error
        db = sqlite3.connect("monitor.db", timeout=20)
        cursor = db.cursor()
        # ambil data dari tabel monitor
        row_monitor = cursor.execute('''SELECT * FROM monitor ORDER BY createdat DESC ''')
        selection = list(row_monitor.fetchone()) or []

        db.commit()

        # ambil data dari tabel host
        row_host = cursor.execute('''SELECT phase FROM Host WHERE host = ? ''', (selection[1],))
        d = row_host.fetchone()[0]
        print d
        selection.append(d)

        # newhost=(host,)
        # active_host=cursor.execute('''SELECT phase FROM host WHERE host=?''', newhost)
        command = json.dumps(selection)
        # c=active_host.fetchone()
        # if c[0]=='active':
        db.commit()
        db.close()
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
