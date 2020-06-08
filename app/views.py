import os
from app import app
from flask import render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
import torch
import time
from summarizer import Summarizer
from .forms import PhotoForm

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/photo-upload', methods=['GET', 'POST'])
def photo_upload():
    photoform = PhotoForm()

    if request.method == 'POST' and photoform.validate_on_submit():

        photo = photoform.photo.data 

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))
        model = Summarizer('bert-base-uncased')
        file = open('app/static/uploads/'+filename)
        str = file.read()
        str.encode('utf-8').strip()
        file.close()
        start = time.time()
        resp = model(str)
        end = time.time()
        tot_time = end-start
        return render_template('display_photo.html', filename=filename, summ=resp, tt=tot_time)

    flash_errors(photoform)
    return render_template('photo_upload.html', form=photoform)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)