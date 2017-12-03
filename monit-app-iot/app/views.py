from flask import render_template
from flask import request, redirect
from . import app
import models
import datetime
from sqlalchemy.orm import load_only


@app.route('/')
@app.route('/index')
def index():
    rows = models.Host.query.all()
    host = models.Host.query.options(load_only('host'))
    return render_template('index.html', title='Home', rows=rows, host=host)


@app.route('/monitor', methods=['POST'])
def monitor():
    selection = request.form['host']
    # host = models.Host.query.options(load_only('host'))
    return render_template('monitor.html', host=selection)


# return selection
@app.route('/host')
def host():
    host = models.Host.query.options(load_only('host'))
    rows = models.Resource.query.filter_by(host=host)
    rows2 = models.Network.query.filter_by(host=host)
    rows3 = models.Availability.query.filter_by(host=host)
    return render_template('host_monit.html', rows=rows, rows2=rows2, rows3=rows3)


@app.route('/history')
def history():
    user = {'nickname': 'Frondy'}
    return render_template('history.html', title='history', user=user)


@app.route('/res')
def getres():
    host = models.Host.query.first()
    return redirect('/res/' + str(host.id) + '/1')


@app.route('/res/<id>/<category>')
def getHost(id, category):
    host_list = models.Host.query.all()
    host = models.Host.query.filter_by(id=id).options(load_only('host'))
    if category == '1':
        rows = models.Resource.query.filter_by(host=host).with_entities(
            models.Resource.host, models.Resource.date,
            models.Resource.time, models.Resource.cpu
        ).all()
        title = "CPU Usage"
    elif category == '2':
        rows = models.Resource.query.filter_by(host=host).with_entities(
            models.Resource.host, models.Resource.date,
            models.Resource.time,
            models.Resource.memory_avail
        ).all()
        title = "Memory Available"
    elif category == '3':
        rows = models.Resource.query.filter_by(host=host).with_entities(
            models.Resource.host, models.Resource.date,
            models.Resource.time,
            models.Resource.memory_used
        ).all()
        title = "Memory Used"
    elif category == '4':
        rows = models.Resource.query.filter_by(host=host).with_entities(
            models.Resource.host, models.Resource.date,
            models.Resource.time,
            models.Resource.swap_free
        ).all()
        title = "Swap Free"
    return render_template(
        'res.html', rows=rows, host_list=host_list, host_id=id,
        category=category, length=len(rows), title=title
    )


@app.route('/net')
def getnet():
    host = models.Host.query.first()
    return redirect('/net/' + str(host.id) + '/1')


@app.route('/net/<id>/<category>')
def getAllNet(id, category):
    host_list = models.Host.query.all()
    host = models.Host.query.filter_by(id=id).options(load_only('host'))
    if category == '1':
        rows = models.Network.query.filter_by(host=host).with_entities(
            models.Network.host, models.Network.byte_receive,
            models.Network.byte_sent
        ).all()
        title = "Byte Traffic"
        cat = ("Byte Sent", "Byte Receive")
    elif category == '2':
        rows = models.Network.query.filter_by(host=host).with_entities(
            models.Network.host,
            models.Network.packet_receive,
            models.Network.packet_sent
        ).all()
        title = "Packet Traffic"
        cat = ("Packet Sent", "Packet Receive")
    return render_template(
        'net.html', rows=rows, host_list=host_list, host_id=id,
        category=category, length=len(rows), title=title, cat=cat
    )


@app.route('/available')
def getstatus():
    rows = models.Availability.query.all()
    return render_template('avail.html', rows=rows)


@app.route('/disk')
def getdisk():
    rows = models.Disk.query.all()
    return render_template('disk.html', rows=rows)


@app.route('/add_monitor', methods=['POST'])
def add_monitor():
    _host = request.form['host']
    monitype = request.form['monitype']
    interval = request.form['interval']
    starttime = request.form['starttime'] + ':00'
    endtime = request.form['endtime'] + ':00'
    timestamp = datetime.datetime.now()
    if _host == 'All':
        all_host = models.Host.query.all()
        for i in range(len(all_host)):
            one_host = all_host[i]
            one_host.phase = "active"
            models.db.session.commit()
    else:
        active_host = models.Host.query.filter_by(host=_host).first()
        active_host.phase = "active"
        models.db.session.commit()
    query = models.Monitor(_host, monitype, interval, starttime, endtime, timestamp)
    models.db.session.add(query)
    models.db.session.commit()
    # return all_host
    return redirect('/res')


@app.route('/delete_host', methods=['POST'])
def delete_host():
    # query=models.Host.query.all()
    # models.db.session.delete(query)
    host = request.form['host']
    models.Host.query.filter(models.Host.host == host).delete()
    models.db.session.commit()
    return redirect('/')

# return render_template('index.html',title='Home', user=user, rows=rows, host=host)
