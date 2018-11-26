from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from startup_setup import Startup, Founder, Base

app = Flask(__name__)

engine = create_engine('sqlite:///startup.db',connect_args={'check_same_thread': False}, echo=True)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/startups/JSON')
def showstartupsJSON():
    startups = session.query(Startup).all()
    return jsonify(startups=[s.serialize for s in startups])

@app.route('/')
@app.route('/startups')
def showStartups():
    startups = session.query(Startup).all()
    return render_template('list.html', startups=startups)

@app.route('/startups/<int:startup_id>/details/JSON')
def showDetailsJSON(startup_id):
    startup = session.query(Startup).filter_by(id=startup_id).one()
    founders = session.query(Founder).filter_by(startup_id=startup_id).all()
    return jsonify(Founder=[i.serialize for i in founders])

@app.route('/startups/<int:startup_id>/')
@app.route('/startups/<int:startup_id>/details/')
def showDetails(startup_id):
    startups = session.query(Startup).filter_by(id=startup_id).one()
    founders = session.query(Founder).filter_by(startup_id=startup_id).all()
    return render_template('details.html', founders=founders, startups=startups)

@app.route('/startups/<int:startup_id>/details/add/', methods=['GET', 'POST'])
def newFounder(startup_id):
    startups = session.query(Startup).filter_by(id=startup_id).one()
    founders = session.query(Founder).filter_by(startup_id=startup_id).all()
    if request.method == 'POST':
        newFounder = Founder(name=request.form['name'],bio=request.form[
                           'bio'], startup_id=startup_id)
        session.add(newFounder)
        session.commit()
        flash('New Founder %s  Successfully Created' % (newFounder.name))
        return redirect(url_for('showDetails', startup_id=startup_id))
    else:
        return render_template('newfounder.html', startup_id=startup_id,founders=founders)

@app.route('/startups/<int:startup_id>/details/<int:founder_id>/edit/', methods=['GET', 'POST'])
def editFounder(startup_id, founder_id):
    editedfounders = session.query(Founder).filter_by(id=founder_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedfounders.name = request.form['name']
        if request.form['bio']:
            editedfounders.bio = request.form['bio']

        session.add(editedfounders)
        session.commit()
        flash('Founder Successfully Edited')
        return redirect(url_for('showDetails', startup_id=startup_id))
    else:
        return render_template('editfounder.html', startup_id=startup_id,founders=editedfounders)

@app.route('/startups/<int:startup_id>/details/<int:founder_id>/delete/', methods=['GET', 'POST'])
def deleteFounder(startup_id, founder_id):
    startup = session.query(Startup).filter_by(id=startup_id).one()
    deletedfounders = session.query(Founder).filter_by(id=founder_id).one()
    if request.method == 'POST':
        session.delete(deletedfounders)
        session.commit()
        flash('Founder Successfully Deleted')
        return redirect(url_for('showDetails', startup_id=startup_id))
    else:
        return render_template('deletefounder.html', startup_id=startup_id,founders=deletedfounders)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
