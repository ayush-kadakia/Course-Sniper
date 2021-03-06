from flask import Flask, flash, redirect, render_template, request, session, abort, request, url_for
from twilio.rest import Client
from multiprocessing import Process
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'test'
account_sid = os.getenv('ACCT-SID')
auth_token = os.getenv('AUTH-TKN')
print(account_sid)
client = Client(account_sid, auth_token)

class Node:
    def __init__(self, index, phone):
        self.index = index
        self.phone = phone
        self.status = True
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, i, p): 
        new_node = Node(i, p) 

        if self.head is None: 
            self.head = new_node 
            return
  
        last = self.head 
        while (last.next): 
            last = last.next
  
        last.next =  new_node

    def searchIndex(self, x): 
  
        current = self.head 
  
        while current != None: 
            if current.index == x: 
                return current
              
            current = current.next
          
        return None 

    def searchPhone(self, x): 
  
        current = self.head 
  
        while current != None: 
            if current.phone == x: 
                return True 
              
            current = current.next
          
        return False 

    def deleteNode(self, i, p):  
          
        temp = self.head  
  
        if (temp is not None):  
            if (temp.index == i and temp.phone == p):  
                self.head = temp.next
                temp = None
                return
    
        while(temp is not None):  
            if temp.index == i and temp.phone == p:  
                break
            prev = temp  
            temp = temp.next
  
        if(temp == None):  
            return
  
        prev.next = temp.next
  
        temp = None

courses = LinkedList()

def script(index, phone):
    print(index + ' begin loop')
    status = True
    while(status):
        response = requests.get("http://sis.rutgers.edu/soc/api/courses.gzip?campus=NB&year=2020&term=9&level=U")
        print("checking " + index)
        data = response.json()
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
                                    print (index + 'end loop')
                                    courses.deleteNode(index, phone)
                                    return currStatus

def chkIndex(index):
    if len(index) == 5:
        try: 
            int(index)
            return True
        except ValueError:
            return False

def chkPhone(phone):
    try: 
        int(phone)
        return True
    except ValueError:
        return False

def chkDupe(index, phone):
    something = courses.searchIndex(index)
    if something is not None and something.phone == phone:
        return True
    return False

        
@app.route("/", methods=['POST'])
def addToLL():
    index = request.form['index']
    phone = request.form['phone']

    if chkIndex(index) and chkPhone(phone):
        if chkDupe(index, phone) == False:
            courses.append(index, phone)
            p = Process(target=script, args=(index, phone,))
            p.start()
            flash('Added index:' + index + ' to watch list!')
            return redirect(url_for('hello'))
        else:
            flash('Already being tracked')
            return redirect(url_for('hello'))          
    else:
        flash('Invalid Index or Phone')
        return redirect(url_for('hello'))  

@app.route("/")
def hello():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()

