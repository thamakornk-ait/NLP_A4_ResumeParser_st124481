from flask import Flask, render_template, request, redirect, url_for
import os
from PyPDF2 import PdfReader
import pandas as pd
import numpy as np
from spacy.lang.en.stop_words import STOP_WORDS
import spacy

app = Flask(__name__)

df_resume = pd.read_csv("data/resume.csv")
nlp = spacy.load('en_core_web_md')
skill_path = 'data/skills.jsonl'
ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(skill_path)
# Configure a folder to store uploaded PDFs
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocessing(sentence):
    stopwords    = list(STOP_WORDS)
    doc          = nlp(sentence)
    clean_tokens = []
    
    for token in doc:
        if token.text not in stopwords and token.pos_ != 'PUNCT' and token.pos_ != 'SYM' and \
            token.pos_ != 'SPACE':
                clean_tokens.append(token.lemma_.lower().strip())
                
    return " ".join(clean_tokens)

def get_skills(text):
    
    doc = nlp(text)
    
    skills = []
    
    for ent in doc.ents:
        if ent.label_ == 'SKILL':
            skills.append(ent.text)
            
    return skills

def unique_skills(x):
    return list(set(x))

def lookfor_skill(skill):
    qualified_id = []
    for i in range(len(df_resume)):
        if skill in (df_resume.Skills.iloc[i]):
            qualified_id.append(df_resume.ID.iloc[i])
        else:
            # return f"{df_resume.ID.iloc[i]} is not qualified"
            continue
    return qualified_id

# Create the uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])

def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select a file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            # Save the uploaded PDF file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            reader = PdfReader(file_path)
            page = reader.pages[0]
            text = page.extract_text()
            text = preprocessing(text)
            doc = nlp(text)
            output = get_skills(doc)
            
            # Return the uploaded filename and number of pages
            return render_template('result.html', filename=file.filename, skill=output)
    
    # Render the file upload form if GET request
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
