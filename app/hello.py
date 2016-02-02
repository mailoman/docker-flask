#!flask/bin/python
from flask import render_template, make_response
from flask import request
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/install/<vmname>')
def install(vmname):
    r = make_response(render_template('install.sh', vmname=vmname), 200)
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0')
