
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,abort,session
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
from urllib.parse import urlsplit
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from account_email import (
    RESET_PASSWORD, VERIFY_EMAIL, consume_code, find_account, issue_code,
    normalize_email, send_site_email, session_version
)
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from business_email import MAIL_HOST, MAIL_SPF, has_verification_record, mail_dns_hosts, mail_dns_status, normalize_domain
from smtplib import SMTPException
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
app.config['SECRET_KEY'] = os.environ['TECHX_SECRET_KEY']
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('TECHX_SECURE_COOKIES', '1') == '1'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TECHX_DATABASE_URI', 'sqlite:///techx_db.db')
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
    user = db.session.get(User, user_id)
    version = session.get('account_session_version')
    if user and user.verified and version and secrets.compare_digest(version, session_version(user)):
        return user
    return None


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
def account_navigation():
    if not current_user.is_authenticated:
        return {}
    return {'sign_out_form': FlaskForm(prefix='logout'), 'can_manage_domains': is_domain_admin()}


def deliver_enquiry(form):
    if not form.validate_on_submit():
        flash('Enter a valid email address and describe your project.', 'error')
        return False

    message = EmailMessage()
    message['To'] = 'thabo@eswtn.com'
    message['Reply-To'] = form.email.data.strip()
    message['Subject'] = 'New TechX website enquiry'
    subject = (form.subject.data or '').strip() or 'General enquiry'
    name = (form.name.data or '').strip() or 'Not provided'
    message.set_content(f"Name: {name}\nEmail: {form.email.data.strip()}\nSubject: {subject}\n\n{form.message.data.strip()}")

    try:
        send_site_email(message)
    except (KeyError, ValueError, OSError, SMTPException) as error:
        app.logger.error('TechX enquiry delivery failed (%s)', type(error).__name__)
        flash('We could not send your enquiry. Please try again.', 'error')
        return False

    flash('Your enquiry was sent.', 'success')
    return True


@app.route("/", methods=['POST','GET'])
def home():
    logo_options = Logo_Options()
    poster_options = Poster_Options()
    flyer_options = Flyer_Options()
    brochure_options = Brochure_Options()
    db.create_all()
    contact_form = Contact_Form()
    title = "Tech Xolutions (TechX)"

    if request.method == "POST" and deliver_enquiry(contact_form):
        return redirect(url_for('home', _anchor='contact-us'))

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


def ensure_account_tables():
    User.__table__.create(bind=db.engine, checkfirst=True)
    AccountEmailCode.__table__.create(bind=db.engine, checkfirst=True)


def safe_login_destination(target):
    if not target or not target.startswith('/') or target.startswith('//'):
        return None
    if '\\' in target or any(ord(character) < 32 for character in target):
        return None
    parts = urlsplit(target)
    return target if not parts.scheme and not parts.netloc else None


def start_customer_session(user, version):
    session.clear()
    login_user(user)
    session['account_session_version'] = version


def begin_verification(user, destination):
    session.clear()
    session['verify_email'] = normalize_email(user.email)
    session['verify_session_version'] = session_version(user)
    session['verify_next'] = destination
    if issue_code(user, VERIFY_EMAIL):
        flash('We sent a verification code to your email.', 'success')
    return redirect(url_for('verify_email'))


@app.route("/client_signup", methods=["GET", "POST"])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('domain_portal'))

    register = CustomerSignupForm()
    destination = safe_login_destination(request.args.get('next'))
    if register.validate_on_submit():
        ensure_account_tables()
        email = normalize_email(register.email.data)
        existing = User.query.filter(func.lower(func.trim(User.email)) == email).first()
        if existing:
            register.email.errors.append('An account already uses this email. Sign in or reset your password.')
        else:
            password_hash = encry_pw.generate_password_hash(register.password.data).decode('utf-8')
            user = User(name=register.name.data, email=email, password=password_hash,
                        confirm_password=password_hash, image='default.jpg')
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                register.email.errors.append('Could not create the account. Try signing in or resetting your password.')
            else:
                return begin_verification(user, destination)

    return render_template('client_signup.html', register=register, destination=destination)


@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if not session.get('verify_email'):
        return redirect(url_for('login'))
    ensure_account_tables()
    user = find_account(session['verify_email'])
    if user is None or session.get('verify_session_version') != session_version(user):
        session.clear()
        return redirect(url_for('login'))

    form = AccountCodeForm()
    resend_form = FlaskForm()
    if request.method == 'POST':
        if request.form.get('action') == 'resend':
            if resend_form.validate_on_submit():
                if issue_code(user, VERIFY_EMAIL):
                    flash('We sent a new verification code.', 'success')
                else:
                    flash('A new code could not be sent. Wait one minute and try again.', 'error')
            return redirect(url_for('verify_email'))
        if form.validate_on_submit():
            if consume_code(user, VERIFY_EMAIL, form.code.data):
                db.session.refresh(user)
                version = session_version(user)
                if version != session.get('verify_session_version'):
                    db.session.rollback()
                    session.clear()
                    return redirect(url_for('login'))
                user.verified = True
                db.session.commit()
                destination = session.get('verify_next')
                start_customer_session(user, version)
                flash('Your email is verified.', 'success')
                return redirect(destination or url_for('domain_portal'))
            form.code.errors.append('This code is invalid or has expired. Request a new code if needed.')

    return render_template('account_email.html', title='Verify your email', form=form,
                           email=user.email, resend_form=resend_form)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        ensure_account_tables()
        email = normalize_email(form.email.data)
        user = find_account(email)
        if user:
            issue_code(user, RESET_PASSWORD)
        session['reset_email'] = email
        flash('If an account matches that email, a password reset code will be sent.', 'success')
        return redirect(url_for('reset_password'))

    return render_template('account_email.html', title='Forgot password', form=form)


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('forgot_password'))

    form = CustomerResetForm()
    if form.validate_on_submit():
        ensure_account_tables()
        user = find_account(email)
        version = session_version(user) if user else None
        if consume_code(user, RESET_PASSWORD, form.code.data):
            db.session.refresh(user)
            if version != session_version(user):
                db.session.rollback()
                return redirect(url_for('forgot_password'))
            password_hash = encry_pw.generate_password_hash(form.password.data).decode('utf-8')
            user.password = password_hash
            user.confirm_password = password_hash
            db.session.commit()
            logout_user()
            session.clear()
            flash('Your password has been reset. Sign in with your new password.', 'success')
            return redirect(url_for('login'))
        form.code.errors.append('This code is invalid or has expired. Request a new code if needed.')

    return render_template('account_email.html', title='Reset your password', form=form,
                           email=email, reset=True)


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


@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    destination = safe_login_destination(request.args.get('next'))
    if form.validate_on_submit():
        ensure_account_tables()
        user = find_account(form.email.data)
        if (user and len(form.password.data.encode('utf-8')) <= 72
                and encry_pw.check_password_hash(user.password, form.password.data)):
            if not user.verified:
                return begin_verification(user, destination)
            start_customer_session(user, session_version(user))
            return redirect(destination or url_for('domain_portal'))
        flash('Login unsuccessful. Check your email and password.', 'error')

    return render_template('login.html', login=form, destination=destination)


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

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    form = FlaskForm(prefix='logout')
    if form.validate_on_submit():
        logout_user()
        session.clear()
        return redirect(url_for('home'))
    return render_template('account_logout.html', title='Sign out of TechX', sign_out_form=form)


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
    if account.user_id != current_user.id and not is_domain_admin():
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

    if current_user.is_authenticated:
        form.email.data = current_user.email

    if form.validate_on_submit():
        label, available, message = eswtn_name_status(form.requested_label.data)
        if not available:
            flash(message, 'error')
        else:
            domain_request = DomainRequest(
                user_id=current_user.id if current_user.is_authenticated else None,
                requested_label=label,
                email=normalize_email(form.email.data),
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
    owner_email = normalize_email(current_user.email)
    # Preserve guest reservations and legacy approved domains after mailbox verification.
    for model, email_column in ((DomainRequest, DomainRequest.email),
                                (DomainAccount, DomainAccount.owner_email)):
        model.query.filter(model.user_id.is_(None), func.lower(func.trim(email_column)) == owner_email).update(
            {'user_id': current_user.id}, synchronize_session=False
        )
    db.session.commit()
    domain_requests = DomainRequest.query.filter_by(user_id=current_user.id).order_by(
        DomainRequest.created_at.desc()
    ).all()

    admin_view = is_domain_admin() and request.args.get('admin_view') == '1'
    requested_account_id = request.args.get('account', type=int)
    if admin_view and requested_account_id:
        selected_account = DomainAccount.query.get_or_404(requested_account_id)
        accounts = [selected_account]
    else:
        accounts = DomainAccount.query.filter_by(user_id=current_user.id).order_by(DomainAccount.created_at.desc()).all()
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


def ensure_business_email_tables():
    ensure_domain_tables()
    BusinessEmailRequest.__table__.create(bind=db.engine, checkfirst=True)


@app.route('/business-email')
def business_email():
    return render_template('business_email.html', title='Business Email | TechX')


@app.route('/business-email/setup/<mode>', methods=['GET', 'POST'])
@login_required
def business_email_setup(mode):
    if mode not in ('managed', 'external'):
        abort(404)
    ensure_business_email_tables()
    form = BusinessEmailForm()
    if form.validate_on_submit():
        try:
            return submit_business_email_request(form, mode)
        except ValueError as error:
            form.domain.errors.append(str(error))
        except IntegrityError:
            db.session.rollback()
            flash('You already requested this address. Check My Email for its status.', 'error')
    return render_template('business_email_setup.html', title='Request a mailbox', form=form, mode=mode)


def submit_business_email_request(form, mode):
    mailbox = form.mailbox.data.lower()
    raw_domain = form.domain.data.strip().lower()
    if mode == 'managed':
        label = raw_domain.rstrip('.')
        if label.endswith('.eswtn.com'):
            label = label[:-len('.eswtn.com')]
        domain = f'{label}.eswtn.com'
        existing = DomainAccount.query.filter_by(fqdn=domain, user_id=current_user.id, status='active').first()
        pending = DomainRequest.query.filter_by(requested_label=label, user_id=current_user.id, status='pending').first()
        if not existing and not pending:
            label, available, reason = eswtn_name_status(label)
            if not available:
                raise ValueError(reason)
            db.session.add(DomainRequest(
                user_id=current_user.id, requested_label=label, email=normalize_email(current_user.email),
                request_type='professional_email', intended_use='Business Email mailbox request',
                status='pending',
            ))
    else:
        domain = normalize_domain(raw_domain)
        if domain == 'eswtn.com' or domain.endswith('.eswtn.com'):
            raise ValueError('Choose the eswtn.com option for a TechX-managed address.')
    if len(f'{mailbox}@{domain}') > 254:
        raise ValueError('Choose a shorter mailbox name or domain.')

    item = BusinessEmailRequest(
        user_id=current_user.id, domain=domain, mailbox=mailbox, mode=mode,
        verification_code=f'techx-mail={secrets.token_urlsafe(24)}' if mode == 'external' else None,
    )
    db.session.add(item)
    db.session.commit()
    flash('Your mailbox request was submitted.', 'success')
    return redirect(url_for('my_email'))


@app.route('/my-email')
@login_required
def my_email():
    ensure_business_email_tables()
    items = BusinessEmailRequest.query.filter_by(user_id=current_user.id).order_by(
        BusinessEmailRequest.created_at.desc()
    ).all()
    return render_template('my_email.html', title='My Email', items=items,
                           action_form=DomainAdminActionForm(), mail_host=MAIL_HOST, mail_spf=MAIL_SPF)


@app.route('/my-email/<int:request_id>/verify', methods=['POST'])
@login_required
def business_email_verify(request_id):
    ensure_business_email_tables()
    if not DomainAdminActionForm().validate_on_submit():
        abort(400)
    item = BusinessEmailRequest.query.filter_by(id=request_id, user_id=current_user.id,
                                               mode='external').first_or_404()
    if item.status == 'dns_setup':
        hosts = mail_dns_hosts(item.domain)
        if hosts is None:
            flash('DNS is unavailable. Try again shortly.', 'error')
        elif set(hosts) == {MAIL_HOST}:
            flash('Mail is routed to TechX. We’ll complete the send and receive checks.', 'success')
        elif hosts:
            flash(f'Current mail servers: {", ".join(hosts)}. Your mail is not yet routed only to TechX.', 'error')
        else:
            flash('No MX record was found. Add the mail record shown below and check again.', 'error')
        return redirect(url_for('my_email'))
    if item.status != 'pending':
        abort(404)
    verified = has_verification_record(item)
    if verified:
        item.verified_at = datetime.utcnow()
        db.session.commit()
        flash(f'{item.domain} is verified. TechX can now review your request.', 'success')
    else:
        flash('DNS is unavailable. Try again shortly.' if verified is None else
              'The verification record was not found. Check the name and value, then try again.', 'error')
    return redirect(url_for('my_email'))


@app.route('/domain-admin/email/<int:request_id>/<action>', methods=['POST'])
@domain_admin_required
def business_email_review(request_id, action):
    ensure_business_email_tables()
    if not DomainAdminActionForm().validate_on_submit():
        abort(400)
    item = db.session.get(BusinessEmailRequest, request_id)
    if item is None:
        abort(404)
    destination = url_for('domain_admin', _anchor='email-requests')
    previous = item.status
    changes = {}
    if action == 'reject' and previous == 'pending':
        changes['status'] = 'rejected'
    elif action == 'approve' and previous == 'pending':
        if item.mode == 'external':
            eligible = item.verified_at is not None and has_verification_record(item)
            error = 'The customer needs a current DNS verification record before approval.'
        else:
            account = item.managed_domain_account
            eligible = account is not None and account.status == 'active'
            error = 'Approve the customer’s eswtn.com domain request first.'
        if not eligible:
            flash(error, 'error')
            return redirect(destination)
        changes = {'status': 'approved', 'reserved_address': item.address}
    elif action == 'provisioned' and previous == 'approved':
        changes['status'] = 'dns_setup'
    elif action == 'ready' and previous == 'dns_setup':
        if request.form.get('mail_tested') != 'yes' or mail_dns_status(item.domain) is not True:
            flash('Confirm the mailbox passed send and receive tests and that its MX points only to TechX.', 'error')
            return redirect(destination)
        changes['status'] = 'ready'
    else:
        flash('That action is unavailable for the current request status.', 'error')
        return redirect(destination)
    address = item.address
    try:
        updated = BusinessEmailRequest.query.filter_by(id=item.id, status=previous).update(changes)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('This mailbox address is already allocated.', 'error')
    else:
        if updated:
            flash(f'{address}: request updated.', 'success')
        else:
            flash('The request has already changed. Review its current status before trying again.', 'error')
    return redirect(destination)


@app.route('/domain-admin')
@domain_admin_required
def domain_admin():
    ensure_business_email_tables()
    pending_requests = DomainRequest.query.filter_by(status='pending').order_by(
        DomainRequest.created_at.asc()
    ).all()
    accounts = DomainAccount.query.order_by(DomainAccount.created_at.desc()).all()
    return render_template(
        'domain_admin.html',
        title='eswtn.com Administration | Tech Xolutions',
        pending_requests=pending_requests,
        email_requests=BusinessEmailRequest.query.order_by(BusinessEmailRequest.created_at.desc()).all(),
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

    linked_user = find_account(domain_request_item.email)
    account = DomainAccount(
        request_id=domain_request_item.id,
        user_id=domain_request_item.user_id or (linked_user.id if linked_user and linked_user.verified else None),
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



@app.route('/domain-admin/accounts/<int:account_id>/status', methods=['POST'])
@domain_admin_required
def domain_account_status(account_id):
    ensure_domain_tables()
    form = DomainAdminActionForm()
    if not form.validate_on_submit():
        abort(400)

    account = DomainAccount.query.get_or_404(account_id)
    if account.status == 'active':
        account.status = 'suspended'
        action = 'account_editing_paused'
        message = f'DNS editing paused for {account.fqdn}. Existing DNS records remain live.'
    else:
        account.status = 'active'
        action = 'account_editing_resumed'
        message = f'DNS editing resumed for {account.fqdn}.'

    add_dns_audit(account, action, account.fqdn, after={'status': account.status})
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('domain_admin'))


@app.route('/about')
def about():

    return render_template('about.html')

@app.route("/contact", methods=["POST", "GET"])
def contact_us():
    contact_form = Contact_Form()
    if request.method == "POST" and deliver_enquiry(contact_form):
        return redirect(url_for('contact_us'))

    return render_template("contact.html",contact_form=contact_form)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
