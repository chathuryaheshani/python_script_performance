"""
Input the correct driver email , it will generate the activity graph and upload to firebase storage.
please consider driver must finish one trip (Their trip data important).
"""

import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import storage
import requests
import datetime
import collections
import matplotlib.pyplot as plt
import numpy as np
import os

class performance:
    def __init__(self,mail):
        global db,days,data,cred
        self.mail = mail
        self.currentmail = self.mail.split(".")
        
        self.savebarchart = (self.currentmail[0] + "_bar" + ".png")
        self.savepichart = (self.currentmail[0] + "_pi" + ".png")

        cred = credentials.Certificate('neon.json')
        firebase_admin.initialize_app(cred,{'storageBucket': 'neon-uom.appspot.com'})
        db = firestore.client()
        
        today = datetime.date.today()
            
        data = []
        days = []
        
        for i in range(0,7):
            pastdate = today - datetime.timedelta(days=i)

            temp = pastdate

            temp_pastdate = pastdate.strftime("%B %d, %Y") #change format date
        
            if temp_pastdate[-8]=='0':
                print("it is needed")
                temp_check = temp_pastdate.split(',')[0]
                temp_check = temp_check.replace('0','')
                print(temp_check)
                temp_pastdate = temp_check+','+temp_pastdate.split(',')[1]

            print(temp_pastdate)
            data.append(self.getData(temp_pastdate))
            days.append(pastdate.strftime("%B %d, %Y"))
            
            pastdate = temp
            
        print(days)
        self.drawBarChart()
        self.drawPieChart()
        self.saveInFirebase()
        

    def getData(self,date):
        print ("data getting")
        users_ref = db.collection(self.mail+date)
        docs = users_ref.get()
        tot = 0

        for doc in docs:
            if doc.id != 'Tripcount':
                a = doc.to_dict()
                od = collections.OrderedDict(sorted(a.items()))
                start,end = list(od.keys())[0],list(od.keys())[-1]

                s1 = start.split(" ")[0]
                s2 = end.split(" ")[0]

                FMT = '%H:%M:%S'
                
                tdelta = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
                h = (tdelta.total_seconds() / 60.0)
                tot = tot+h
       
        return tot
                

    def drawBarChart(self):
        global daynew
       
        
        daynew = []
        for i in days:
            temp = i.split(",")[0][0:3]+" "+i.split(",")[0][-2:]
            daynew.append(temp)
            
        y_pos = np.arange(len(days))
        
        
        plt.bar(y_pos, data, align='center', alpha=0.5)
        plt.xticks(y_pos, daynew)
        plt.ylabel('Minutes')
        plt.xlabel('Days')
        
        plt.savefig(self.savebarchart)
        


    def drawPieChart(self):
        tot = 0
        percentage = []

        for i in data:
            tot = tot+i

        per = 0
        for i in range(0,7):
            per = (100/tot)*data[i]
            percentage.append(per)

        fig1, ax1 = plt.subplots()
        ax1.pie(percentage,  labels=daynew, autopct='%1.1f%%',
        shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig(self.savepichart)


    def saveInFirebase(self):
        bucket = storage.bucket()

        dir = os.path.dirname(__file__)
        abs_path = os.path.join(dir,self.savebarchart)
      

        
        blob = bucket.blob("performance/barchart/"+self.savebarchart)
        blob.upload_from_filename(self.savebarchart)


        blob = bucket.blob("performance/piechart/"+self.savepichart)
        blob.upload_from_filename(self.savepichart)

        

perform = performance("chelvan34@gmail.com/Trip/")
