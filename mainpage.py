#-*- coding: utf-8 -*-
import json
from app import *

@app.route('/', methods=['GET', 'POST'])
def mainpage():
    return render_template('wsd.html')
