
from flask import Flask,render_template,url_for,redirect,request,flash
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from Forms import Register, Login,Contact_Form, Project_Form, Web_Design_Brief
from models import *
from flask_bcrypt import Bcrypt
import Users_Data
import secrets
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from flask_colorpicker import colorpicker



 #project cloned from git
#Change App
application = Flask(__name__)
application.config['SECRET_KEY'] = "sdsdjfe832j2rj_32j"
application.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:tmazst41@localhost/techxol_clients"
application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
application.config["SQLALCHEMY_POOL_RECYCLE"] = 299
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config["UPLOADED"] = 'static/uploads'

db.init_app(application)

login_manager = LoginManager(application)

# Log in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


ALLOWED_EXTENSIONS = {"txt", "xlxs",'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file has an allowed extension
def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_file(file):

        filename = secure_filename(file)

        _img_name, _ext = os.path.splitext(file.filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext

        if file.filename == '':
            return 'No selected file'

        if file.filename and allowed_files(file):
            file_saved = file.save(os.path.join(application.config["UPLOADED"],new_file_name))
            flash(f"File Upload Successful!!", "success")
            return new_file_name

        else:
            return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"



def createall(db_):
    db_.create_all()

encry_pw = Bcrypt()

@application.route("/")
def home():

    db.create_all()
    contact_form = Contact_Form()
    title = "Tech Xolutions (TechX)"


    return render_template("index.html",title=title,contact_form=contact_form)



@application.route("/user_section", methods=["POST","GET"])
def user_section():


    return render_template("user_section.html")


@application.route("/graphic_design", methods=["POST","GET"])
def graphic_design():


    return render_template("graphic_design.html")


@application.route("/project_order_data", methods=["POST","GET"])
def project_order_data():

    brief = Project_Form()

    return render_template("project_order_data.html",brief=brief)


@application.route("/logo_brief", methods=["POST", "GET"])
def logo_brief():

    brief = Project_Form()

    gen_token = secrets.token_hex(8)
    time_stamp = datetime.utcnow()
    proj_name = ""
    brief_dict = {}
    createall(db)

    if request.method == "GET":
        proj_name = request.args.get("proj_name")

    if request.method == "POST":

        proj_name = request.form['project-name']
        brief_dict['target_audience'] = brief.target_audience.data
        brief_dict['display_name'] = brief.artwork_name.data
        brief_dict['slogan'] = brief.slogan.data
        brief_dict['proj_deadline'] = brief.proj_deadline.data.strftime("%Y-%m-%d %H:%M:%S")
        brief_dict['comments'] = brief.comments.data
        brief_dict['projectuid_token'] = gen_token
        brief_dict['time_stamp'] = f"{time_stamp}"

        project = Project_Brief(name=proj_name, user_id=current_user.id, brief_date=time_stamp,
                                token=gen_token)  # token = gen_token (Token to be used to match project details between database and json

        db.session.add(project)
        db.session.commit()

        Users_Data.users_data().project_data("logo_design_"+str(time_stamp),brief_dict)

        print(f"LOGO BRIEF: Dict:{brief_dict} TimeStamp:{time_stamp} Project_Name:{proj_name} ")

        return redirect(url_for("logo_brief"))


    gen_token = ""

    return render_template("logo_brief.html", brief=brief)

@application.route("/profile_brief", methods=["POST", "GET"])
def profile_brief():

    brief = Project_Form()

    # color_picker = colorpicker(application=application)

    gen_token = secrets.token_hex(8)
    time_stamp = datetime.utcnow()
    proj_name = ""
    brief_dict = {}
    createall(db)

    if request.method == "GET":
        proj_name = request.args.get("proj_name")

    if request.method == "POST":

        proj_name = request.form['project-name']
        brief_dict['target_audience_ages'] = brief.target_audience.data
        brief_dict['targetm_Area'] = brief.targetm_area.data
        brief_dict['targetm_segment'] = brief.targetm_segment.data
        brief_dict['display_name'] = brief.artwork_name.data
        brief_dict['colors_1'] = request.form.get('color_1')
        brief_dict['colors_2'] =  request.form.get('color_2')
        brief_dict['slogan'] = brief.slogan.data
        brief_dict['proj_deadline'] = brief.proj_deadline.data.strftime("%Y-%m-%d %H:%M:%S")
        brief_dict['comments'] = brief.comments.data
        brief_dict['projectuid_token'] = gen_token
        brief_dict['time_stamp'] = f"{time_stamp}"

        print("DEBUG COLOR: ",brief_dict['colors_1'])

        project = Project_Brief(name=proj_name, user_id=current_user.id, brief_date=time_stamp,
                                token=gen_token)  # token = gen_token (Token to be used to match project details between database and json

        if brief.upload_profile.data:
            profile_upload = process_file(brief.upload_profile.data)
            project.upload_profile = profile_upload

        if brief.company_document.data:
            upload = process_file(brief.company_document .data)
            project.company_document  = upload

        if brief.upload_logo.data:
            upload = process_file(brief.upload_logo.data)
            project.upload_logo  = upload

        db.session.add(project)
        db.session.commit()

        Users_Data.users_data().project_data("logo_design_"+str(time_stamp),brief_dict)

        print(f"LOGO BRIEF: Dict:{brief_dict} TimeStamp:{time_stamp} Project_Name:{proj_name} ")

        return redirect(url_for("logo_brief"))

    gen_token = ""

    return render_template("profile_brief.html", brief=brief)


@application.route("/web_development", methods=["POST","GET"])
def web_app_dev():

    if request.method == "POST":
        pass

    return render_template("web_development.html")


@application.route("/web_design_brief", methods=["POST","GET"])
def web_design_brief():

    web_brief = Web_Design_Brief()

    if request.method == "POST":
        pass

    return render_template("web_design_brief.html",web_brief=web_brief)

@application.route("/client_signup", methods=["POST","GET"])
def sign_up():

    register = Register()

    db.create_all()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    image_fl = url_for('static', filename='images/image.jpg')

    if register.validate_on_submit():

        #print(f"Account Successfully Created for {register.name.data}")
        if request.method == 'POST':
            # context

            hashd_pwd = encry_pw.generate_password_hash(register.password.data).decode('utf-8')
            # Base.metadata.create_all()
            # ....user has inherited the Base class
            # db.create_all()
            user1 = User(name=register.name.data, email=register.email.data, password=hashd_pwd,
                         confirm_password=hashd_pwd,image="default.jpg")

            # db.rollback()
            try:
                db.session.add(user1)
                db.session.commit()
                flash(f"Account Successfully Created for {register.name.data}", "success")
                return redirect(url_for('login'))
            except: # IntegrityError:
                flash(f"Something went wrong, check for errors", "success")
                Register().validate_email(register.email.data)


            # #print(register.name.data,register.email.data)
    elif register.errors:
        flash(f"Account Creation Unsuccessful ", "error")
        #print(register.errors)



    # from myproject.models import user
    return render_template("client_signup.html",register=register)

@application.route("/login", methods=["POST","GET"])
def login():

    login = Login()

    print(f"Submtion: ")




    if login.validate_on_submit():


        if request.method == 'POST':

            user_login = User.query.filter_by(email=login.email.data).first()
            # flash(f"Hey! {user_login.password} Welcome", "success")
            if user_login and encry_pw.check_password_hash(user_login.password, login.password.data):
                login_user(user_login)
                print("Creditantials are ok")
                # if not user_login.verified:
                #     return redirect(url_for('verification'))
                # else:
                    # After login required prompt, take me to the page I requested earlier
                print("No Verification Needed: ", user_login.verified)
                req_page = request.args.get('next')
                flash(f"Hey! {user_login.name.title()} You're Logged In!", "success")
                return redirect(req_page) if req_page else redirect(url_for('home'))
            else:
                flash(f"Login Unsuccessful, please use correct email or password", "error")
                # print(login.errors)
    else:
        print("No Validation")
        if login.errors:
            for error in login.errors:
                print("Errors: ", error)
        else:
            print("No Errors found", login.email.data, login.password.data)

    return render_template("login.html",login=login)


@application.route('/logout')
def log_out():
    logout_user()
    return redirect(url_for('home'))


@application.route("/contact", methods=["POST", "GET"])
def contact_us():

    contact_form = Contact_Form()
    if request.method == "POST":
        if contact_form.validate_on_submit():
            def send_link():
                application.config["MAIL_SERVER"] = "smtp.googlemail.com"
                application.config["MAIL_PORT"] = 587
                application.config["MAIL_USE_TLS"] = True
                em = application.config["MAIL_USERNAME"] = os.environ.get("EMAIL")
                application.config["MAIL_PASSWORD"] = os.environ.get("PWD")

                mail = Mail(application)

                msg = Message(contact_form.subject.data, sender=contact_form.email.data, recipients=[em])
                msg.body = f"""{contact_form.message.data}
{contact_form.email.data}
                    """

                try:
                    mail.send(msg)
                    flash("Your Message has been Successfully Sent!!", "success")
                    return "Email Sent"
                except Exception as e:
                    # print(e)
                    flash(f'Ooops Something went wrong!! Please Retry', 'error')
                    return "The mail was not sent"

                # Send the pwd reset request to the above email
            send_link()

            #print("Posted")
        else:
            flash("Ooops!! Please be sure to fill both email & message fields, correctly","error")

    return render_template("contact.html",contact_form=contact_form)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    application.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
