
from flask import Flask, render_template, redirect, url_for, request, session, flash
from jinja2 import Template
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)