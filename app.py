from flask import Flask, request, redirect, jsonify, render_template
import os
import pandas as pd
import markdown
from werkzeug.utils import secure_filename
from app_functions import *

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


material = {}
def process_excel():
    global material  # Declare the global variable inside the function
    df = pd.read_excel('uploads/stored_excel_file.xlsx')
    # Extract the 'Text' column and convert it to a dictionary
    text_column = df['Text']
    material = text_column.to_dict()  # Assign to the global variable
    return material


@app.route('/')
def home():
    return render_template('home.html')

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return "No file part"
#     file = request.files['file']
#     if file.filename == '':
#         message = "No selected file"
#     if file:
#         filename = secure_filename(file.filename)
#         new_filename = 'stored_excel_file.xlsx'  # Custom name for future use
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
#         message = "File uploaded successfully"
#         process_excel()
#     return render_template('upload.html', message=message)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', message="No file part")
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message="No selected file")
        if file:
            filename = secure_filename(file.filename)
            new_filename = 'stored_excel_file.xlsx'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            process_excel()
            return render_template('upload.html', message="File uploaded successfully")
    else:
        # When user clicks "Back to Options" button
        return render_template('upload.html', message="")


@app.route('/dashboard')
def dashboard():
    df1 = csv_text_to_dataframe(summarize(material))
    df2 = csv_text_to_dataframe(tag_it(material))
    merged_df = df1.merge(df2, on="Index", how="left")
    actual_rating_flag = True
    avg_rating = actual_rating()
    # avg_rating = 3.8
    positive, negative, neutral = count_sentiments(merged_df)
    satisfaction_score = clean_and_mean(merged_df)
    return render_template('dashboard.html',
                           table=merged_df.to_html(classes='table table-bordered', index=False, table_id="myTable"),
                           flg=actual_rating_flag, actr=avg_rating, pos=positive, neg=negative, neu=neutral,
                           air=satisfaction_score)

@app.route('/analysis')
def analysis():
    result = analysis_report(material)
    # Convert markdown to HTML
    result = markdown.markdown(result)
    return render_template('analysis.html', message=result)

@app.route('/suggest')
def suggest():
    result = suggested_improvements(material)
    # Convert markdown to HTML with ordered list numbering disabled
    html_content = markdown.markdown(result, extensions=['nl2br'], output_format='html5')
    return render_template('suggest.html', message=html_content)

@app.route('/safa')
def safa():
    return render_template('safa.html')

#####################################################
#trials of errors
@app.route('/404_copy')
def copy_404():
    return render_template('404.html')

@app.route('/500_copy')
def copy_500():
    return render_template('500.html')

@app.route('/502_copy')
def copy_502():
    return render_template('502.html')

@app.route('/503_copy')
def copy_503():
    return render_template('503.html')

##################################################
# ERROR HANDLERS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(502)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(503)
def unauthorized(e):
    return render_template('503.html'), 401

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

