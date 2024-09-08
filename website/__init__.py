from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
# from fpdf import FPDF
import google.generativeai as genai

views = Blueprint('views', __name__)

db = SQLAlchemy()
DB_NAME = "database.db"

API_KEY = 'YOUR_API_KEY'
MODEL = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=API_KEY)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @views.route('/')
    def home():
        return render_template('home.html')

    @views.route('summarize', methods=['POST'])
    def summarize():
        text = request.form.get('note')
        prompt = MODEL.generate_content(f"Summarize the following texts in bullet point notes: {text}")
        summary = prompt.text
        return render_template('summary.html', summary=summary)

#         convert the sumary in a PDF file
#         pdf = FPDF()
#         pdf.set_auto_page_break(auto=True, margin=15)
#         pdf.add_page()
#         pdf.set_font('Arial', size=14) #customize the font style and size here
#         pdf.multi_cell(0, 10, summary)
#         pdf.output(output_pdf) #saves the pdf

# convert_to_pdf(summary, "summary.pdf")
# files.download("summary.pdf")

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
