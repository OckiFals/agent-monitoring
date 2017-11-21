from . import db


class Host(db.Model):
    id = db.Column(db.Integer, index=True, unique=True)
    hostname = db.Column(db.String(64))
    host = db.Column(db.String(64), primary_key=True)
    status = db.Column(db.String(64))
    phase = db.Column(db.String(64))


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    host = db.Column(db.String(64))
    date = db.Column(db.String(64))
    time = db.Column(db.String(64))
    cpu = db.Column(db.Integer)
    memory_avail = db.Column(db.Integer)
    memory_used = db.Column(db.Integer)
    swap_free = db.Column(db.Integer)


class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    host = db.Column(db.String(64))
    date = db.Column(db.String(64))
    time = db.Column(db.String(64))
    byte_sent = db.Column(db.Integer)
    byte_receive = db.Column(db.Integer)
    packet_sent = db.Column(db.Integer)
    packet_receive = db.Column(db.Integer)


class Disk(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    host = db.Column(db.String(64))
    date = db.Column(db.String(64))
    time = db.Column(db.String(64))
    disk_used = db.Column(db.Integer)
    disk_free = db.Column(db.Integer)
    read_bytes = db.Column(db.Integer)
    write_bytes = db.Column(db.Integer)


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    host = db.Column(db.String(64))
    date = db.Column(db.String(64))
    time = db.Column(db.String(64))
    status = db.Column(db.String(64))


class Monitor(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    host = db.Column(db.String(64))
    monitype = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    createdat = db.Column(db.String(64))

    def __init__(self, host, monitype, interval, start, end, createdat):
        self.host = host
        self.monitype = monitype
        self.interval = interval
        self.start = start
        self.end = end
        self.createdat = createdat
