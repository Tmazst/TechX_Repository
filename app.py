
from flask import Flask,render_template,url_for,redirect,request,flash
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from Forms import *
from models import *
from flask_bcrypt import Bcrypt
import Users_Data
import secrets
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker



#Did latest commit with the requirement file

#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdsdjfe832j2rj_32j"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///techx_db.db"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:tmazst41@localhost/techxolutions_db"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED"] = 'static/uploads'

db.init_app(app)

application = app

login_manager = LoginManager(app)

# Log in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


ALLOWED_EXTENSIONS = {"txt", "xlxs",'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Func to check if the file has an allowed extension
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
            file_saved = file.save(os.path.join(app.config["UPLOADED"],new_file_name))
            flash(f"File Upload Successful!!", "success")
            return new_file_name

        else:
            return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"


def createall(db_):
    db_.create_all()

encry_pw = Bcrypt()

@app.context_processor
def inject_ser():
    # ser = Serializer(app.config['SECRET_KEY'])  # Define or retrieve the value for 'ser'
    # count_jobs = count_ads()

    return dict()

def mail_enqueries(contact_form):

    def send_link():
        app.config["MAIL_SERVER"] = "techxolutions.com"
        app.config["MAIL_PORT"] = 465
        app.config["MAIL_USE_TLS"] = True
        em = app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_INFO")
        app.config["MAIL_PASSWORD"] = os.environ.get("TX_PWD")

        mail = Mail(app)

        msg = Message(contact_form.subject.data, sender=contact_form.email.data, recipients=[em])
        msg.body = f"""{contact_form.message.data}\n
{contact_form.email.data}\n
<p style="font-size:25px;color:red">This is a Test</p>
                    """

        # try:
        mail.send(msg)
        flash("Your Message has been Successfully Sent!!", "success")
        return f"Email Sent Successfully"
        # except Exception as e:
        #     flash(f'Ooops Something went wrong!! Please Retry', 'error')
        #     return f"The mail was not sent"

        # Send the pwd reset request to the above email
    send_link()




@app.route("/", methods=['POST','GET'])
def home():
    logo_options = Logo_Options()
    poster_options = Poster_Options()
    flyer_options = Flyer_Options()
    brochure_options = Brochure_Options()
    db.create_all()
    contact_form = Contact_Form()
    title = "Tech Xolutions (TechX)"

    contact_form = Contact_Form()

    if request.method == "POST":
        if contact_form.validate_on_submit():
            mail_enqueries(contact_form)
        else:
            return flash("Ooops!! Please be sure to fill both email & message fields, correctly","error")
        # soup = bs(request.form, "html.parser")

    return render_template("index.html",title=title,contact_form=contact_form,logo_options=logo_options,
                           poster_options=poster_options,brochure_options=brochure_options,flyer_options=flyer_options)



# Method to store logo quotation requests from a home popup function
def quotations(logo_options):

    logo_quote_dict = {}

    logo_quote_dict['Email Sign'] = logo_options.email_signature.data
    logo_quote_dict['letterhead'] = logo_options.letterhead.data
    logo_quote_dict['mock_up'] = logo_options.mock_up.data
    logo_quote_dict['artwork'] = logo_options.artwork.data
    logo_quote_dict['file_types'] = logo_options.file_types.data

    for key,details in logo_quote_dict.items():
        print("CHECK DICT: ",key,' : ',details)

    Users_Data.users_data().project_data("logo_quote_popup_" + str(datetime.utcnow()), logo_quote_dict)


@app.route("/free_icons", methods=["POST","GET"])
def free_icons():
    
    return render_template('techxicons.html')


@app.route("/user_section", methods=["POST","GET"])
def user_section():

    return render_template("user_section.html")


@app.route("/graphic_design", methods=["POST","GET"])
def graphic_design():

    return render_template("graphic_design.html")


@app.route("/project_order_data", methods=["POST","GET"])
def project_order_data():

    brief = Project_Form()

    return render_template("project_order_data.html",brief=brief)


@app.route("/logo_brief", methods=["POST", "GET"])
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

@app.route("/profile_brief", methods=["POST", "GET"])
def profile_brief():

    brief = Project_Form()

    # color_picker = colorpicker(app=app)

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


@app.route("/web_development", methods=["POST","GET"])
def web_app_dev():

    if request.method == "POST":
        pass

    return render_template("web_development.html")


@app.route("/web_design_brief", methods=["POST","GET"])
def web_design_brief():

    web_brief = Web_Design_Brief()

    if request.method == "POST":
        pass

    return render_template("web_design_brief.html",web_brief=web_brief)


@app.route("/client_signup", methods=["POST","GET"])
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

@app.route("/client_user_acc", methods=["POST","GET"])
@login_required
def client_user_acc():

    signup = Register()

    user_acc = User.query.get(current_user.id)

    if request.method == "POST":
         update_acc = client_user(
             contacts=signup.contacts.data,
             date_of_birth = db.Column(db.DateTime()),
             address = signup.address.data,
             other = signup.zip_code.data  # Zip Code
         )

         db.session.add(update_acc)
         db.session.commit()

    return render_template("client_user_acc.html",user_acc=user_acc,signup=signup)


@app.route("/login", methods=["POST","GET"])
def login():

    login = Login()

    print(f"Submtion: ")


    if login.validate_on_submit():


        if request.method == 'POST':

            user_login = User.query.filter_by(email=login.email.data).first()
            # flash(f"Hey! {user_login.password} Welcome", "success")
            if user_login and encry_pw.check_password_hash(user_login.password, login.password.data):
                login_user(user_login)
                # print("Creditantials are ok")
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


@app.route('/cashbook',methods=['POST','GET'])
def cashbook():

    cashbook_form = CashBookForm()

    if request.method == 'POST':
        if cashbook_form.validate_on_submit():
            entry = CashBook(
                entry_date=cashbook_form.entry_date.data,
                description=cashbook_form.description.data,
                amount=cashbook_form.amount.data,
                exp_or_income=cashbook_form.exp_or_income.data,
                timestamp=datetime.now()
            )

            db.session.add(entry)
            db.session.commit()
            flash('Entry Successfully Recorded','success')

    return render_template('cashbook_form.html',cashbook_form=cashbook_form)


@app.route('/cashbooktable',methods=['POST','GET'])
def cashbook_table():

    cashbook_form = CashBookForm()
    cb_entries = CashBook.query.all()

    if request.method == 'POST':
        if cashbook_form.validate_on_submit():

            cb_entries.entry_date=cashbook_form.entry_date.data,
            cb_entries.description=cashbook_form.description.data,
            cb_entries.amount=cashbook_form.amount.data,
            cb_entries.exp_or_income=cashbook_form.exp_or_income.data

            db.session.commit()
            flash('Update Successfully','success')

    return render_template('cashbook_table.html',cb_entries=cb_entries,cashbook_form=cashbook_form)

@app.route('/logout')
def log_out():
    logout_user()
    return redirect(url_for('home'))


@app.route('/about')
def about():

    return render_template('about.html')

@app.route("/contact", methods=["POST", "GET"])
def contact_us():
    # print("DEBUG EMAIL: ",os.environ.get("EMAIL_INFO"))
    contact_form = Contact_Form()
    if request.method == "POST":
        if contact_form.validate_on_submit():
            def send_link():
                app.config["MAIL_SERVER"] = "techxolutions.com"
                app.config["MAIL_PORT"] = 465
                app.config["MAIL_USE_TLS"] = True
                em = app.config["MAIL_USERNAME"] = os.environ.get("EMAIL")
                app.config["MAIL_PASSWORD"] = os.environ.get("TX_PWD")

                # print("DEBUG EMAIL1: ",em)
                # print("DEBUG EMAILP: ",app.config["MAIL_PASSWORD"])

                mail = Mail(app)

                msg = Message(contact_form.subject.data, sender=contact_form.email.data, recipients=[em])
                msg.body = f"""{contact_form.message.data}\n
{contact_form.email.data}\n
<p style="font-size:25px;color:red">This is a Test</p>
                    """

                # try:
                mail.send(msg)
                flash("Your Message has been Successfully Sent!!", "success")
                return "Email Sent"
                # except Exception as e:
                #     # print(e)
                #     flash(f'Ooops Something went wrong!! Please Retry', 'error')
                #     return "The mail was not sent"

                # Send the pwd reset request to the above email
            send_link()

            #print("Posted")
        else:
            for error in contact_form.errors:
                print('Form Error: ',error)
            flash("Ooops!! Please be sure to fill both email & message fields, correctly","error")

    return render_template("contact.html",contact_form=contact_form)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
