# Python Modules
from flask import Flask, redirect, url_for, request, render_template
import jinja2

# Google Modules
from google.appengine.api import users

# personal moduls
from adams_module import *


#################################################################################
#
# instantiate the app
#
#################################################################################

app = Flask(__name__)



#################################################################################
#
# function for landing page
#
#################################################################################

@app.route('/', methods=['GET'])
def landing_page():
	user = users.get_current_user()

	if user:
		nickname = user.nickname()
		return redirect(url_for('user_summary_page', nickname=nickname))
	else:
		login_logout_url = users.create_login_url('/')
		return "<html><body>Welcome Unkown User.  Please <a href={}>log in</a> so we know who you are.</body></html>".format(login_logout_url)





#################################################################################
#
# function for user summary page
#
#################################################################################

@app.route('/user/<nickname>', methods=['GET'])
def user_summary_page(nickname):
	user = users.get_current_user()

	if user:
		login_logout_url = users.create_logout_url('/')

		# binding condition: if current user is requesting their page allow; else redirect
		if nickname == user.nickname():
			# query the datastore
			opp_query = Opportunity.query( ancestor=create_opportunity_key(nickname))
			opps_to_render = opp_query.fetch(limit=10)
			# supply to frontend
			return render_template('user_summary_page.html', nickname=nickname, login_logout_url=login_logout_url, opps_to_render=opps_to_render)
		else:
			# flash message 'You are not authorized to view this page'
			return redirect(url_for('landing_page'))
	else:
		login_logout_url = users.create_login_url('/')
		return "<html><body>Welcome Unkown User.  Please <a href={}>log in</a> so we know who you are.</body></html>".format(login_logout_url)


#################################################################################
#
# function for adding opportunities
#
#################################################################################

@app.route('/<nickname>/add_opportunity', methods=['GET','POST'])
def add_opportunity(nickname):
	user = users.get_current_user()

	if user:
		login_logout_url = users.create_logout_url('/')

		# binding condition: cannot enter an opportunity for another user
		if nickname == user.nickname():
			if request.method == 'GET':
				return render_template('add_opportunity.html', nickname=nickname, login_logout_url=login_logout_url)

			if request.method == 'POST':
				# generate payload
				payload = dict()
				payload['nickname'] = nickname
				payload['company_name'] = request.form['inp_company_name']
				payload['opp_start_date'] = request.form['inp_start_date']
				payload['unit_name'] = request.form['inp_unit_name']
				payload['num_units'] = int(request.form['inp_num_units'])
				payload['existing_customer'] = request.form['inp_existing_customer']
				payload['notes'] = request.form['inp_ae_notes']
				payload['milestone'] = int(request.form['inp_milestone'])

				# write data to database
				create_opportunity(httpmeth='get', opp_id=None,  **payload)
				del payload

				# redirect back to user page
				return redirect(url_for('user_summary_page', nickname=nickname))
		else:
			#flash('You cannot enter an opportunity for another user.')
			return redirect(url_for('user_summary_page', nickname=nickname))
	else:
		login_logout_url = users.create_login_url('/')
		return "<html><body>Welcome Unkown User.  Please <a href={}>log in</a> so we know who you are.</body></html>".format(login_logout_url)






#################################################################################
#
# function for editing opportunities
#
#################################################################################

@app.route('/<nickname>/edit_opportunity/<opp_id>', methods=['GET','POST'])
def edit_opportunity(nickname, opp_id):
	user = users.get_current_user()
	if user:
		login_logout_url = users.create_logout_url('/')

		if nickname == user.nickname():
			if request.method == 'GET':
				# query datastore using  key and parent - get_by_id fails without parents specified
				opp=Opportunity.get_by_id(int(opp_id), parent=create_opportunity_key(nickname=nickname))
				return render_template('edit_opportunity.html', nickname=nickname, login_logout_url=login_logout_url, opp=opp)
			else:
				# generate payload
				payload = dict()
				payload['nickname'] = nickname
				payload['company_name'] = request.form['inp_company_name']
				payload['opp_start_date'] = request.form['inp_start_date']
				payload['unit_name'] = request.form['inp_unit_name']
				payload['num_units'] = int(request.form['inp_num_units'])
				payload['existing_customer'] = request.form['inp_existing_customer']
				payload['notes'] = request.form['inp_ae_notes']
				payload['milestone'] = int(request.form['inp_milestone'])
				
				# write data to database
				create_opportunity(httpmeth='post', opp_id=int(opp_id),**payload)
				del payload

				# redirect back to user page
				return redirect(url_for('user_summary_page', nickname=nickname))
		else:
			#flash 'You cannot edit someone elses opportunities'
			return redirect(url_for('user_summary_page', nickname=nickname))





#################################################################################
#
# function for deal summary page
#
#################################################################################
@app.route('/DealsSummary', methods=['GET','POST'])
def deal_summary():
	# require user to login
	user = users.get_current_user()
	# If user is logged in
	if user:
		nickname = users.nickname()
		login_logout_url = users.create_logout_url('/')
		# instantiate a query object
		query = Opportunity.query()
		# filter: only obs from current year
		query = query.filter(Opportunity.entity_creation_date.year == datetime.datetime.now().year)
		# sort by deal size
		query = query.order(-Opportunity.num_units)
		# query the database
		query = query.fetch()
		# return the template
		return render_template("deal_summary.html", nickname = nickname, login_logout_url = login_logout_url, data=query)
	else:
		login_logout_url = users.create_login_url('/')
		return "<html><body>Welcome Unkown User.  Please <a href={}>log in</a> so we know who you are.</body></html>".format(login_logout_url)