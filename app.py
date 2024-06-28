
import os
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate
from datetime import datetime
import logging
from flask import Flask, render_template, request, redirect, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/Demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'pandiyank29112001@gmail.com'
app.config['MAIL_PASSWORD'] = 'kclj gfru vdlc optr'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    manager_email = db.Column(db.String(50))

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    status = db.Column(db.String(20))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_id = request.form['user_id'].strip()
    from_date = request.form['from_date']
    to_date = request.form['to_date']

    if not user_id or not user_id.isdigit():
        return jsonify({'status': 'error', 'message': 'User ID must be a valid number'})

    user_id = int(user_id)
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User ID does not exist'})

    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
    days_requested = (to_date_obj - from_date_obj).days + 1

    if days_requested > 2:
        return jsonify({'status': 'error', 'message': 'Cannot give more than two days'})

    current_month = datetime.now().month
    leave_requests = LeaveRequest.query.filter_by(user_id=user_id).all()
    days_taken = sum([(req.to_date - req.from_date).days + 1 for req in leave_requests if req.from_date.month == current_month])

    if days_taken + days_requested > 5:
        return jsonify({'status': 'error', 'message': 'Work from home balance exceeded for this month'})

    new_request = LeaveRequest(user_id=user_id, from_date=from_date_obj, to_date=to_date_obj, status='Pending')
    db.session.add(new_request)
    db.session.commit()

    try:
        msg = Message('Work From Home Request', sender=user.email, recipients=[user.manager_email])
        msg.body = f"{user.name} has requested work from home from {from_date} to {to_date}."
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Leave request submitted successfully'})
    except Exception as e:
        logging.error("Failed to send email", exc_info=e)
        return jsonify({'status': 'error', 'message': 'Failed to send email'})

if __name__ == '__main__':
    app.run(debug=True)