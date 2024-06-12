from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, TextAreaField,BooleanField, SelectField,DateField, URLField
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError
from flask_login import current_user
from flask_wtf.file import FileField , FileAllowed
# from wtforms.fields.html5 import DateField,DateTimeField



class Register(FlaskForm):

    name = StringField('name', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('confirm', validators=[DataRequired(),EqualTo('password'), Length(min=8, max=64)])

    submit = SubmitField('Create Account!')


    def validate_email(self,email):
        from main import db, User,app

        # with db.init_app(app):
        user_email = User.query.filter_by(email = self.email.data).first()
        if user_email:
            return ValidationError(f"Email already registered in this platform")



class Login(FlaskForm):


    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    submit = SubmitField('Login')


class Contact_Form(FlaskForm):

    name = StringField('name')
    email = StringField('email', validators=[DataRequired(),Email()])
    subject = StringField("subject")
    message = TextAreaField("Message",validators=[Length(min=8, max=2000)])
    submit = SubmitField("Send")


class Project_Form(FlaskForm):

    target_audience = SelectField('Customers Age Range', choices=[("18 - 25 years","18 - 25 years"),("18 - 36 years","18 - 36 years"),("25 - 45 years","25 - 45 years"),("+18 years","+18 years"),("+36 years","+36 years")])
    targetm_area = SelectField('Customers Locations',
                                  choices=[("Urban Set-up", "Urban Set-up"), ("Rural", "Rural"),
                                           ("No Specific Area", "No Specific Area")])
    targetm_segment = SelectField('Customers Categorised',
                               choices=[("Working Class", "Working Class"), ("Students", "Students"),("Tourists", "Tourists"),
                                        ("Non Working Class", "Non Working Class"),("No Specific Category", "No Specific Category")])
    artwork_name = StringField('Verbiage')
    company_category = SelectField('Category', choices=[("Technology","Technology"), ("Healthcare","Healthcare"),("Finance","Finance"),("Retail","Retail"),
                                                        ("Manufacturing","Manufacturing"),("Energy","Energy"), ("Transportation and Logistics","Transportation and Logistics"),
                                                        ("Entertainment and Media","Entertainment and Media"),("Real Estate","Real Estate"),("Professional Services","Professional Services")])
    other_services = StringField('Services')
    vision = StringField('Vision')
    mission = StringField('Mission')
    slogan = StringField('Slogan / Tagline')
    proj_deadline = DateField('When are you expecting your Project?')
    comments = TextAreaField('What can you add?')
    upload_profile = FileField("Upload Profile Content")
    company_document = FileField("Upload any Company Document")
    upload_logo = FileField("Upload Company Logo")
    comp_colors1 = StringField('Choose Color')
    comp_colors2 = StringField('Choose Color')

    submit = SubmitField('Submit')


class Web_Design_Brief(Project_Form):

    current_website = BooleanField("Do you currently have a website?")
    # Project Goals
    # Ask for your client’s definition of success.Do they want to increase the amount of visitors, up the average order size, or boost the users on their web forum? Perhaps
    # they want to encourage greater engagement via their blog, increase their brand visibility, or encourage people to sign up for their email newsletter/free trial/white paper, etc.
    web_traffic = BooleanField("We aim to increase traffic and establish an online presence")
    web_forum = BooleanField("We aim to boost the number users on our web forum")
    build_brand = BooleanField("We want to building our brand")
    web_ui_interactivity = BooleanField("We want improve the User Interactivity")
    web_new_look= BooleanField("We want a whole new on our Website")
    curr_web_comments = StringField("Comments about the current website")

    company_profile = BooleanField("Do you have any document you can upload i.e. business profile?")

    payment_options = SelectField('Choose Best Payment Option', choices=[("On-time Payment","On-time Payment"),("Pay Deposit + Balance Later","Pay Deposit + Balance Later"),
                                                                         ("Pay Deposit + with 2-3 Months Installments"),("Pay Deposit + with 2-3 Months Installments")])
    hosting = SelectField('Do you a Domain Name for site', choices=[("Yes, I have a domain","Yes, I have a domain"),("Yes, but I need a new one","Yes, but I need a new one"),
                                                                         ("No, I will need advice from You","No, I will need advice from You")])
    dns = SelectField('Do you a Hosting Server', choices=[("Yes, I have a hosting site", "Yes, I have a hosting site"),("Yes, but I need a new one","Yes, but I need a new one"),
                                                                ("No, I will need your advice","No, I will need your advice")])
    pages = SelectField('How many page does your site need?', choices=[("1 Page Website", "1 Page Website"),("1 Page divided by Sections","1 Page divided by Sections"),
                                                                ("3-4 Pages","3-4 Pages"),("4+ Pages","4+ Pages")])
    type = SelectField('Type of Website', choices=[("Business website", "Business website"), ("Business with eCommerce website", "Business with eCommerce website"),
                                                  ("Blog website", "Blog website"),("Portfolio website", "Portfolio website"),("Nonprofit website", "Nonprofit website"),
                                                   ("Other", "Other")])

    model = SelectField('Your business with your clients', choices=[("B2B - Business-to-Business", "B2B - Business-to-Business"), ("B2C - Business-to-Customer", "B2C - Business-to-Customer"),
                                                   ("Both", "Both")])

    feel1= BooleanField("Executive")
    feel2 = BooleanField("Modern Look")
    feel3 = BooleanField("Youthful")
    feel4 = BooleanField("Motion Effects")
    feel5 = BooleanField("More Graphics than content")
    feel6 = BooleanField("Content & Pictures")

    inspiration = URLField("Can you link us to an any website that inspires you")
    inspiration2 = URLField("Can you link us to an any website that inspires you")




class Update_account_form(FlaskForm):


    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    image_pfl = FileField('Profile Image', validators=[FileAllowed(['jpg','png'])])
    contacts = StringField('Contact(s)', validators=[Length(min=8, max=64)])
    school = StringField('High School', validators=[Length(min=8, max=64)])
    tertiary = StringField('Tertiary (Optional)')
    experience = TextAreaField('Work Experience (Optional)')
    skills = TextAreaField('Skills', validators=[Length(min=8, max=150)])
    hobbies = StringField('Hobbies (Optional)')
    address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    reference_1 = TextAreaField('Reference 1 [Fullname & Contact]',
                                validators=[DataRequired(), Length(min=8, max=64)])
    reference_2 = TextAreaField('Reference 2  [Fullname & Contact]',
                                validators=[DataRequired(), Length(min=8, max=64)])

    def validate_email(self,email):
        from application import db, user
        if current_user.email != self.email.data:
            #Check if email exeists in database
            user_email = user.query.filter_by(email = self.email.data).first()
            if user_email:
                raise ValidationError(f"email, {email.value}, already taken by someone")


    update = SubmitField('Update')


class Reset(FlaskForm):

    old_password = PasswordField('old password', validators=[DataRequired(), Length(min=8, max=64)])
    new_password = PasswordField('new password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new_password'), Length(min=8, max=64)])

    reset = SubmitField('Reset')


class Reset_Request(FlaskForm):

    email = StringField('email', validators=[DataRequired(), Email()])

    reset = SubmitField('Submit')

    # def validate_email(self,email):
    #     user = user.query.filter_by