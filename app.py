
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,abort
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from Forms import *
from models import *
from flask_bcrypt import Bcrypt
import Users_Data
import secrets
import os
import re
import json
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker
from domain_dns import (
    DnsServiceError,
    DnsValidationError,
    build_record_payload,
    cloudflare_configured,
    cloudflare_create_record,
    cloudflare_delete_record,
    cloudflare_find_records,
    cloudflare_update_record
)



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
login_manager.login_view = 'login'

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


@app.route("/brand-support")
def brand_support():
    return render_template("brand_support.html")

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


ESWTN_RESERVED_LABELS = {
    'www', 'mail', 'smtp', 'imap', 'pop', 'admin', 'api', 'billing',
    'support', 'techx', 'cloudflare', 'ns1', 'ns2', 'ftp', 'status'
}
ESWTN_LABEL_PATTERN = re.compile(
    r'^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'
)


def ensure_domain_tables():
    """Create Phase 1 and Phase 2 tables without altering existing customer data."""
    for model in (DomainRequest, DomainAccount, ManagedDnsRecord, DnsAuditLog):
        model.__table__.create(bind=db.engine, checkfirst=True)


def is_domain_admin():
    configured_emails = {
        email.strip().lower()
        for email in os.environ.get('DOMAIN_ADMIN_EMAILS', '').split(',')
        if email.strip()
    }
    return (
        current_user.is_authenticated
        and current_user.email
        and current_user.email.strip().lower() in configured_emails
    )


def domain_admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not is_domain_admin():
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def eswtn_name_status(raw_label):
    label = (raw_label or '').strip().lower()
    if not ESWTN_LABEL_PATTERN.fullmatch(label):
        return label, False, 'Use 1–63 letters, numbers or hyphens. The name cannot start or end with a hyphen.'
    if label in ESWTN_RESERVED_LABELS:
        return label, False, 'This name is reserved for TechX infrastructure.'
    existing_request = DomainRequest.query.filter_by(requested_label=label).filter(
        DomainRequest.status.in_(['pending', 'approved', 'active'])
    ).first()
    existing_account = DomainAccount.query.filter_by(label=label).filter(
        DomainAccount.status.in_(['active', 'suspended'])
    ).first()
    if existing_request or existing_account:
        return label, False, 'This name already has an active or pending request.'
    return label, True, 'This name is preliminarily available.'


def owned_domain_account(account_id):
    account = DomainAccount.query.get_or_404(account_id)
    owner_email = (current_user.email or '').strip().lower()
    owns_account = (
        account.user_id == current_user.id
        or account.owner_email.strip().lower() == owner_email
    )
    if not owns_account and not is_domain_admin():
        abort(403)
    return account


def record_snapshot(record):
    return {
        'type': record.record_type,
        'name': record.name,
        'content': record.content,
        'ttl': record.ttl,
        'proxied': record.proxied,
        'priority': record.priority
    }


def add_dns_audit(account, action, record_name=None, before=None, after=None):
    db.session.add(DnsAuditLog(
        domain_account_id=account.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        record_name=record_name,
        before_value=json.dumps(before, sort_keys=True) if before is not None else None,
        after_value=json.dumps(after, sort_keys=True) if after is not None else None,
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr or '')[:64]
    ))


@app.route('/domain-support', methods=['GET', 'POST'])
def domain_support():
    ensure_domain_tables()
    form = DomainInterestForm()

    if request.method == 'GET' and current_user.is_authenticated and not form.email.data:
        form.email.data = current_user.email

    if form.validate_on_submit():
        label, available, message = eswtn_name_status(form.requested_label.data)
        if not available:
            flash(message, 'error')
        else:
            domain_request = DomainRequest(
                user_id=current_user.id if current_user.is_authenticated else None,
                requested_label=label,
                email=form.email.data.strip().lower(),
                request_type=form.request_type.data,
                intended_use=form.intended_use.data.strip(),
                status='pending'
            )
            db.session.add(domain_request)
            db.session.commit()
            flash(f'{label}.eswtn.com has been submitted for review.', 'success')
            if current_user.is_authenticated:
                return redirect(url_for('domain_portal'))
            return redirect(url_for('domain_support', requested=label))

    return render_template(
        'domain_support.html',
        title='eswtn.com Domain Support | Tech Xolutions',
        form=form
    )


@app.route('/api/domain-availability')
def domain_availability():
    ensure_domain_tables()
    label, available, message = eswtn_name_status(request.args.get('name'))
    return jsonify({
        'label': label,
        'fqdn': f'{label}.eswtn.com' if label else '',
        'available': available,
        'message': message
    })


@app.route('/domain-portal')
@login_required
def domain_portal():
    ensure_domain_tables()
    owner_email = (current_user.email or '').strip().lower()
    domain_requests = DomainRequest.query.filter(
        (DomainRequest.user_id == current_user.id) |
        (DomainRequest.email == owner_email)
    ).order_by(DomainRequest.created_at.desc()).all()

    admin_view = is_domain_admin() and request.args.get('admin_view') == '1'
    requested_account_id = request.args.get('account', type=int)
    if admin_view and requested_account_id:
        selected_account = DomainAccount.query.get_or_404(requested_account_id)
        accounts = [selected_account]
    else:
        accounts = DomainAccount.query.filter(
            (DomainAccount.user_id == current_user.id) |
            (DomainAccount.owner_email == owner_email)
        ).order_by(DomainAccount.created_at.desc()).all()
        selected_account = next(
            (item for item in accounts if item.id == requested_account_id),
            accounts[0] if accounts else None
        )

    dns_records = []
    audit_logs = []
    if selected_account:
        dns_records = ManagedDnsRecord.query.filter_by(
            domain_account_id=selected_account.id
        ).order_by(ManagedDnsRecord.record_type, ManagedDnsRecord.name).all()
        audit_logs = DnsAuditLog.query.filter_by(
            domain_account_id=selected_account.id
        ).order_by(DnsAuditLog.created_at.desc()).limit(12).all()

    return render_template(
        'domain_portal.html',
        title='My eswtn.com Domains | Tech Xolutions',
        domain_requests=domain_requests,
        accounts=accounts,
        selected_account=selected_account,
        dns_records=dns_records,
        audit_logs=audit_logs,
        record_form=DnsRecordForm(),
        delete_form=DnsDeleteForm(),
        dns_configured=cloudflare_configured(),
        domain_admin=is_domain_admin(),
        admin_view=admin_view
    )


@app.route('/domain-portal/<int:account_id>/records', methods=['POST'])
@login_required
def domain_record_create(account_id):
    ensure_domain_tables()
    account = owned_domain_account(account_id)
    form = DnsRecordForm()

    if account.status != 'active':
        flash('DNS records cannot be changed while this namespace is not active.', 'error')
        return redirect(url_for('domain_portal', account=account.id))
    if not cloudflare_configured():
        flash('DNS automation is not configured on the server yet.', 'error')
        return redirect(url_for('domain_portal', account=account.id))
    if ManagedDnsRecord.query.filter_by(domain_account_id=account.id).count() >= account.record_limit:
        flash(f'This account has reached its limit of {account.record_limit} DNS records.', 'error')
        return redirect(url_for('domain_portal', account=account.id))

    if form.validate_on_submit():
        try:
            payload = build_record_payload(
                form.record_type.data,
                form.name.data,
                form.content.data,
                form.ttl.data,
                form.proxied.data,
                form.priority.data,
                account.fqdn
            )
            provider_record = cloudflare_create_record(payload)
            dns_record = ManagedDnsRecord(
                domain_account_id=account.id,
                provider_record_id=provider_record['id'],
                record_type=provider_record.get('type', payload['type']),
                name=provider_record.get('name', payload['name']),
                content=provider_record.get('content', payload['content']),
                ttl=provider_record.get('ttl', payload['ttl']),
                proxied=provider_record.get('proxied', payload['proxied']),
                priority=provider_record.get('priority', payload.get('priority'))
            )
            db.session.add(dns_record)
            add_dns_audit(account, 'record_created', dns_record.name, after=payload)
            db.session.commit()
            flash(f'{dns_record.record_type} record created successfully.', 'success')
        except (DnsValidationError, DnsServiceError) as error:
            flash(str(error), 'error')
    else:
        flash('Please correct the DNS record form and try again.', 'error')

    return redirect(url_for('domain_portal', account=account.id) + '#dns-records')


@app.route('/domain-portal/records/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def domain_record_edit(record_id):
    ensure_domain_tables()
    dns_record = ManagedDnsRecord.query.get_or_404(record_id)
    account = owned_domain_account(dns_record.domain_account_id)
    form = DnsRecordForm()

    if request.method == 'GET':
        form.record_type.data = dns_record.record_type
        form.name.data = dns_record.name
        form.content.data = dns_record.content
        form.ttl.data = dns_record.ttl
        form.proxied.data = dns_record.proxied
        form.priority.data = dns_record.priority if dns_record.priority is not None else 10

    if form.validate_on_submit():
        if account.status != 'active':
            flash('DNS records cannot be changed while this namespace is not active.', 'error')
            return redirect(url_for('domain_portal', account=account.id))
        if not cloudflare_configured():
            flash('DNS automation is not configured on the server yet.', 'error')
            return redirect(url_for('domain_portal', account=account.id))

        before = record_snapshot(dns_record)
        try:
            payload = build_record_payload(
                form.record_type.data,
                form.name.data,
                form.content.data,
                form.ttl.data,
                form.proxied.data,
                form.priority.data,
                account.fqdn
            )
            provider_record = cloudflare_update_record(dns_record.provider_record_id, payload)
            dns_record.record_type = provider_record.get('type', payload['type'])
            dns_record.name = provider_record.get('name', payload['name'])
            dns_record.content = provider_record.get('content', payload['content'])
            dns_record.ttl = provider_record.get('ttl', payload['ttl'])
            dns_record.proxied = provider_record.get('proxied', payload['proxied'])
            dns_record.priority = provider_record.get('priority', payload.get('priority'))
            add_dns_audit(account, 'record_updated', dns_record.name, before=before, after=payload)
            db.session.commit()
            flash('DNS record updated successfully.', 'success')
            return redirect(url_for('domain_portal', account=account.id) + '#dns-records')
        except (DnsValidationError, DnsServiceError) as error:
            flash(str(error), 'error')

    return render_template(
        'domain_record_edit.html',
        title=f'Edit DNS Record | {account.fqdn}',
        account=account,
        dns_record=dns_record,
        form=form
    )


@app.route('/domain-portal/records/<int:record_id>/delete', methods=['POST'])
@login_required
def domain_record_delete(record_id):
    ensure_domain_tables()
    dns_record = ManagedDnsRecord.query.get_or_404(record_id)
    account = owned_domain_account(dns_record.domain_account_id)
    form = DnsDeleteForm()

    if not form.validate_on_submit():
        abort(400)
    if account.status != 'active':
        flash('DNS records cannot be changed while this namespace is not active.', 'error')
        return redirect(url_for('domain_portal', account=account.id))
    if not cloudflare_configured():
        flash('DNS automation is not configured on the server yet.', 'error')
        return redirect(url_for('domain_portal', account=account.id))

    before = record_snapshot(dns_record)
    try:
        cloudflare_delete_record(dns_record.provider_record_id)
        add_dns_audit(account, 'record_deleted', dns_record.name, before=before)
        db.session.delete(dns_record)
        db.session.commit()
        flash('DNS record deleted successfully.', 'success')
    except DnsServiceError as error:
        flash(str(error), 'error')

    return redirect(url_for('domain_portal', account=account.id) + '#dns-records')


@app.route('/domain-admin')
@domain_admin_required
def domain_admin():
    ensure_domain_tables()
    pending_requests = DomainRequest.query.filter_by(status='pending').order_by(
        DomainRequest.created_at.asc()
    ).all()
    accounts = DomainAccount.query.order_by(DomainAccount.created_at.desc()).all()
    return render_template(
        'domain_admin.html',
        title='eswtn.com Administration | Tech Xolutions',
        pending_requests=pending_requests,
        accounts=accounts,
        action_form=DomainAdminActionForm(),
        dns_configured=cloudflare_configured()
    )


@app.route('/domain-admin/requests/<int:request_id>/approve', methods=['POST'])
@domain_admin_required
def domain_request_approve(request_id):
    ensure_domain_tables()
    form = DomainAdminActionForm()
    if not form.validate_on_submit():
        abort(400)
    if not cloudflare_configured():
        flash('Configure the Cloudflare token and zone ID before activating namespaces.', 'error')
        return redirect(url_for('domain_admin'))

    domain_request_item = DomainRequest.query.get_or_404(request_id)
    if domain_request_item.status != 'pending':
        flash('This request has already been reviewed.', 'error')
        return redirect(url_for('domain_admin'))

    fqdn = f'{domain_request_item.requested_label}.eswtn.com'
    existing_account = DomainAccount.query.filter(
        (DomainAccount.request_id == domain_request_item.id) |
        (DomainAccount.label == domain_request_item.requested_label)
    ).first()
    if existing_account:
        flash('An account already exists for this request or namespace.', 'error')
        return redirect(url_for('domain_admin'))

    try:
        provider_records = cloudflare_find_records(fqdn)
    except DnsServiceError as error:
        flash(str(error), 'error')
        return redirect(url_for('domain_admin'))
    if provider_records:
        flash(f'{fqdn} already has Cloudflare DNS records. Review it manually before approval.', 'error')
        return redirect(url_for('domain_admin'))

    linked_user = User.query.filter_by(email=domain_request_item.email).first()
    account = DomainAccount(
        request_id=domain_request_item.id,
        user_id=domain_request_item.user_id or (linked_user.id if linked_user else None),
        owner_email=domain_request_item.email.strip().lower(),
        label=domain_request_item.requested_label,
        fqdn=fqdn,
        plan=domain_request_item.request_type,
        status='active',
        record_limit=25,
        activated_at=datetime.utcnow()
    )
    domain_request_item.status = 'active'
    domain_request_item.reviewed_at = datetime.utcnow()
    db.session.add(account)
    db.session.flush()
    add_dns_audit(account, 'account_activated', fqdn, after={
        'plan': account.plan,
        'owner_email': account.owner_email,
        'record_limit': account.record_limit
    })
    db.session.commit()
    flash(f'{fqdn} is active and ready for customer DNS management.', 'success')
    return redirect(url_for('domain_admin'))


@app.route('/domain-admin/requests/<int:request_id>/reject', methods=['POST'])
@domain_admin_required
def domain_request_reject(request_id):
    ensure_domain_tables()
    form = DomainAdminActionForm()
    if not form.validate_on_submit():
        abort(400)

    domain_request_item = DomainRequest.query.get_or_404(request_id)
    if domain_request_item.status != 'pending':
        flash('This request has already been reviewed.', 'error')
        return redirect(url_for('domain_admin'))

    domain_request_item.status = 'rejected'
    domain_request_item.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash(f'{domain_request_item.fqdn} was rejected.', 'success')
    return redirect(url_for('domain_admin'))


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
