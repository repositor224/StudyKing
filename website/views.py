from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import google.generativeai as genai
# from fpdf import FPDF

API_KEY = 'YOUR_API_KEY'
MODEL = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=API_KEY)

views = Blueprint('views', __name__)

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@views.route('/', methods=['GET', 'POST'])
@login_required

def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            #Input the Gemini Program Here
            def summarize():
                prompt = MODEL.generate_content(f"Summarize the following texts in bullet point notes: {note}")
                summary = prompt.text
                return render_template('summary.html', summary=summary)
            
            db.session.commit()
            flash('Generated Text Are Below:', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@app.route('/success', methods = ['POST'])   
def success():  
    flash('Files have been uploaded successfully!', category='success') 
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(f.filename)   

@views.route('/Test', methods = ['GET', 'POST'])
def Testing():
     return render_template("Test.html", user=current_user)
