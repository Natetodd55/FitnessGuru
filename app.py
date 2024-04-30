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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(75), nullable=False)
    phone = db.Column(db.String(10))
    authenticated = db.Column(db.Boolean, default=False, nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'member' or 'staff'
    membership = db.relationship('Membership', backref='user', uselist=False)
    services = db.relationship('Service', backref='instructor', lazy='dynamic')

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    benefits = db.relationship('MembershipBenefit', back_populates='membership')

class Benefit(db.Model):
    __tablename__ = 'benefits'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    membership_benefits = db.relationship('MembershipBenefit', back_populates='benefit')
    services = db.relationship('Service', backref='benefit', lazy='dynamic')

class MembershipBenefit(db.Model):
    __tablename__ = 'membership_benefits'
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'), primary_key=True)
    benefit_id = db.Column(db.Integer, db.ForeignKey('benefits.id'), primary_key=True)
    membership = db.relationship('Membership', back_populates='benefits')
    benefit = db.relationship('Benefit', back_populates='membership_benefits')

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    benefit_id = db.Column(db.Integer, db.ForeignKey('benefits.id'), nullable=False)


######################### Helper_Functions ###################################
def get_benefit_names_from_id(membership_benefits):
    benefit_names = []
    for mb in membership_benefits:
        b = Benefit.query.filter_by(id = mb.benefit_id).first()
        benefit_names.append(b.name)
    print(benefit_names)
    return benefit_names
    
def benefits_from_member(member):
    # print(f"Member found: {member.first_name} {member.last_name} (ID: {member.id})")
    benefits = None
    membership = member.membership
    if membership:
        # print("membership ID: ", membership.id)
        benefits = membership.benefits
        # print("benefits: ", benefits)
    return benefits


def get_all_available_benefit_names():
    benefits = []
    for benefit in Benefit.query.distinct(Benefit.name):
        benefits.append(benefit.name)
    return benefits


def add_service_to_benefit(name, time, date, instructor_id):
    benefit = Benefit.query.filter_by(name=name).first()
    new_service = Service(
        name=name,
        time=time,
        date=date,
        instructor_id = instructor_id,
        benefit=benefit
    )
    db.session.add(new_service)
    db.session.commit()


def get_services_from_attached_benefits(user):
    membership = Membership.query.filter_by(user_id = user.id).first()
    benefits_attached = MembershipBenefit.query.filter_by(membership_id = membership.id).all()
    services = []
    for benefit in benefits_attached:
        services_of_benefit = Service.query.filter_by(benefit_id = benefit.benefit_id).all()
        if len(services_of_benefit) != 0:
            services.append(services_of_benefit)

    return services


@lm.user_loader
def load_user(uid):
    return User.query.get(uid)

# from app import db, User
# db.create_all()

############################ flask_routes ###########################
@app.route("/")
def home():

    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method=="POST"):
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user: #member
            if request.form['password'] == cipher.decrypt(user.password).decode('utf-8'):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return render_template('dashboard.html')

    return render_template('login.html')

@app.route("/create_member", methods=["GET", "POST"])
def create_member():
    message = None
    if (request.method=="POST"):
        f_name = request.form['first_name']
        l_name = request.form['last_name']
        email = request.form['email']
        if User.query.filter_by(email=email).first() == None:
            member_pass = cipher.encrypt(request.form['password'])
            member = User(first_name = f_name, last_name=l_name, email=email, password=member_pass, user_type='Member' , authenticated=True)
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


@app.route("/membership", methods=["GET", "POST"])
@login_required
def membership():
    if (request.method=="POST"):
        if request.form["benefit-selected"] != "None":
            print(benefits_from_member(current_user))
            b = Benefit.query.filter_by(name=request.form["benefit-selected"]).first()
            add_benefits = MembershipBenefit(membership_id=current_user.membership.id, benefit_id=b.id)
            db.session.add(add_benefits)
            db.session.commit()
            return render_template("membership.html", membership=current_user.membership, benefits=get_benefit_names_from_id(benefits_from_member(current_user)), all_benefits=get_all_available_benefit_names())
        
        if request.form["Upgrade"] != "None":
            new_membership = Membership(type = request.form["Upgrade"], cost=0, purchase_date="04/30/2024", expiration_date="10/30/2024", user_id=current_user.id)
            db.session.add(new_membership)
            db.session.commit()
        
            return render_template("membership.html", membership=current_user.membership, benefits=get_benefit_names_from_id(benefits_from_member(current_user)), all_benefits=get_all_available_benefit_names())
    else: 
        if current_user.membership == None:
            return render_template("membership.html", membership=None)
        else:
            return render_template("membership.html", membership=current_user.membership, benefits=get_benefit_names_from_id(benefits_from_member(current_user)), all_benefits=get_all_available_benefit_names())

@app.route("/add_services", methods = ["GET", "POST"])
@login_required
def add_services():
    all_benefit_names = get_all_available_benefit_names()
    if request.method == "POST":
        #TODO: handle form
        if request.form:
            # TODO: Attach new service to all benefits with name 'benefit-selected'
            name = request.form['benefit-selected']
            time = request.form['time']
            date = request.form['date']
            instructor_id = current_user.id
            add_service_to_benefit(name, time, date, instructor_id)

    return render_template("add_services.html", all_benefits=all_benefit_names)


@app.route("/view_services")
@login_required
def view_services():
    #TODO Get all Member services from Member's purchased benefits
    all_services = get_services_from_attached_benefits(current_user)
    return render_template("view_services.html", all_services=all_services)


if __name__ == "__main__":
    app.run(debug=True)

