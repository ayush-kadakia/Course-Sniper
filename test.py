from flask import Flask, flash, redirect, render_template, request, session, abort, request
from twilio.rest import Client
import requests
import json

app = Flask(__name__)
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

@app.route("/", methods=['POST'])
def getStatus():

    status = True
    while(status):
        response = requests.get("http://sis.rutgers.edu/soc/api/courses.gzip?campus=NB&year=2020&term=9&level=U")
        data = response.json()
        index = request.form['index']
        phone = request.form['phone']
        print(phone)
        for thing in data:
            for key, value in thing.items():
                if key == "title":
                    subjectName = value
                if key == "sections":
                    for sections in value:
                        for hi, lol in sections.items():
                            if hi == "openStatusText":
                                currStatus = lol
                            if hi == "index":
                                if lol == index and currStatus == "OPEN":
                                    status = False
                                    textMsg = subjectName + " is OPEN"
                                    client.messages \
                                    .create(
                                    body= textMsg,
                                    from_='+17328009198',
                                    to= phone
                                    )
                                    return currStatus
        

@app.route("/")
def hello():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()

