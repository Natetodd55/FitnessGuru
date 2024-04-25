from flask import Flask, request, redirect
from flask.templating import render_template
from flask_login import login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_simple_crypt import SimpleCrypt

############################# flask_sql #############################
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

########################### flask_login ############################
app.config['SECRET_KEY'] = "FitnessGuruProject"
lm = LoginManager(app)
lm.init_app(app)

########################### flask_encryption #############################
cipher = SimpleCrypt()
cipher.init_app(app)

############################## tables ##############################
class Member(UserMixin, db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(75), nullable=False)
    phone = db.Column(db.String(10))
    authenticated = db.Column(db.Boolean, default=False, nullable=False)
    membership = db.relationship('Membership', backref='member', uselist=False)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False

class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.String(10), nullable=False)
    expiration_date = db.Column(db.String(10), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    benefits = db.relationship('Benefit', backref='membership')

class Benefit(db.Model):
    __tablename__ = 'benefits'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'), nullable=False)
    services = db.relationship('Service', backref='benefit')

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    instructor = db.Column(db.String(50), nullable=False)
    benefit_id = db.Column(db.Integer, db.ForeignKey('benefits.id'), nullable=False)




######################### Helper_Functions ###################################
def get_member_services(member):
    print(f"Member found: {member.first_name} {member.last_name} (ID: {member.id})")
    services = []
    membership = member.membership
    if membership:
        print("membership ID: ", membership.id)
        benefits = membership.benefits
        print("Benefits attached to membership: ", benefits)
        for benefit in benefits:
            print(f"Benefit(ID={benefit.id}) is {benefit.name}")
            print(f"Benefit services: {benefit.services}")
            servs = Service.query.all()
            print(f"Services:  {servs}")
            for serv in servs:
                print(f"Service(ID={serv.id}) is {serv.name} with benefit_id = {serv.benefit_id} associated to Benefit(ID={benefit.id})")
                print(f"Service.benefit_id({serv.benefit_id}) == benefit.id({benefit.id})  -> {serv.benefit_id == benefit.id}")
                if serv.benefit_id == benefit.id:
                    print(f"Service(ID={serv.id}) is attached to {benefit.name}")
                    services.extend(Service.query.filter_by(id=serv.id))
    if len(services) == 0:
        return None
    return services

@lm.user_loader
def load_user(uid):
    return Member.query.get(uid)

# from app import db, User
# db.create_all()

############################ flask_routes ###########################
@app.route("/")
def home():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method=="POST"):
        email = request.form['email']
        member = Member.query.filter_by(email=email).first()
        if member:
            if request.form['password'] == cipher.decrypt(member.password).decode('utf-8'):
                member.authenticated = True
                db.session.add(member)
                db.session.commit()
                login_user(member, remember=True)
                return render_template('dashboard.html')

    return render_template('login.html')

@app.route("/create_member", methods=["GET", "POST"])
def create_member():
    message = None
    if (request.method=="POST"):
        f_name = request.form['first_name']
        l_name = request.form['last_name']
        email = request.form['email']
        if Member.query.filter_by(email=email).first() == None:
            member_pass = cipher.encrypt(request.form['password'])
            member = Member(first_name = f_name, last_name=l_name, email=email, password=member_pass, authenticated=True)
            db.session.add(member)
            db.session.commit()
            login_user(member, remember=True)
            return render_template('dashboard.html')
        else:
            message = "Member already registered with email: "+email

    return render_template('create_member.html', message=message)

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template('dashboard.html')


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/membership")
def membership():
    return render_template("membership.html", outline="outline1.html")

@app.route("/training")
def training():
    services = get_member_services(current_user)

    return render_template("training.html", services=services)

if __name__ == "__main__":
    app.run(debug=True)

