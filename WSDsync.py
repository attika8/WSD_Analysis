import requests
import urllib3
from lxml import etree
import os
from datetime import date
from datetime import datetime
import urllib.parse
import pprint
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

pp = pprint.PrettyPrinter(indent=2)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
utf8_parser = etree.XMLParser(encoding='utf-8')
# Gets today's date
today = date.today()
now = datetime.now()
# get the current path
path = os.getcwd()

start = time.time()

# define the structure ID for the sync
#id for testing
#id = 323

#Master structure = 601
id = 601

dailyPath = path+"/"+today.strftime("%B %d, %Y")

try:
    os.makedirs(dailyPath)
except FileExistsError:
    pass

#with open(path+"/"+today.strftime("%B %d, %Y")+"/syncLog.txt", "w") as f:

#    sys.stdout = f



checkToProgress = input('Is the regression tool clean and are you ready to do a sync on the structure ' + str(id) + '? (Y/N)')
if checkToProgress.lower() == 'yes' or checkToProgress.lower() == 'y':
    print('Confirming the check to proceed')
    checkFileExist = input('Has the regression tool report been created in path: ' + dailyPath + '?')
    if checkFileExist.lower() == 'yes' or checkFileExist.lower() == 'y':
        print('Moving on')
    else:
        sys.exit('Please download the excel report file first and add it to path ' + dailyPath)
else:
    sys.exit('Not confirmed. Exiting the code.')


print('Starting tag lib work...')

url = "https://citi.wallstreetdocs.local/api/rest/taglib/list/structure/"+str(id)+".xml"
prodTagLibXML = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)
myPRODTree = etree.fromstring(prodTagLibXML.content, parser=utf8_parser)
numberOfAllPRODTagLibs = len(myPRODTree[0].getchildren())

listOfTagLibsPROD = {}
for elem in myPRODTree.iter():
    if elem.tag == 'taglib':
        try:
            listOfTagLibsPROD.update({elem.attrib['id']:elem.attrib['name']})
        except:
            listOfTagLibsPROD.update({elem.attrib['id']:'noName'})

print('PROD tag lib values:')
#pp.pprint(listOfTagLibsPROD)
print(listOfTagLibsPROD)
print('Number of tag libs in PROD: ' + str(numberOfAllPRODTagLibs))

# UAT taglibs
url = "https://citiuat.wallstreetdocs.local/api/rest/taglib/list/structure/"+str(id)+".xml"
XML = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)
myTree = etree.fromstring(XML.content, parser=utf8_parser)
numberOfAllUATTagLibs = len(myTree[0].getchildren())
print('All taglibs in UAT: ' + str(numberOfAllUATTagLibs))

tagLibPath = path + "/" + today.strftime("%B %d, %Y") + "/tagLib"
try:
    os.makedirs(tagLibPath)
    print('Created directory: ' + tagLibPath)
except FileExistsError:
    print('Directory: ' + tagLibPath + ' already exists')


count = 0
listOfTagsUAT = {}
updatedTagLibs = {}
createdTagLibs = {}
for elem in myTree.iter():
    if elem.tag == 'taglib':

        listOfTagsUAT.update({elem.attrib['id']:elem.attrib['name']})
        url = "https://citiuat.wallstreetdocs.local/api/rest/taglib/get/"+elem.attrib['id']
        response = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)

        tagName = elem.attrib['name']

        folder = tagLibPath
        filename = urllib.parse.quote(tagName).replace("/","%2F")
        ext = ".php"

        with open(os.path.join(folder,filename+ext),'wb') as f:

            f.write(response.content)

            if elem.attrib['name'] in listOfTagLibsPROD.values():
                prodID = (list(listOfTagLibsPROD.keys())[list(listOfTagLibsPROD.values()).index(elem.attrib['name'])])
                #print('UAT ID: ' + str(elem.attrib['id']) + ' and PROD ID: ' + str(prodID))
                postURL = "https://citi.wallstreetdocs.local/api/rest/taglib/put/"+prodID
                updatedTagLibs.update({prodID:elem.attrib['name']})
            else:
                #print('I have not found ' + elem.attrib['name'] + ' in PROD, creating a new codeLib with this name')
                postURL = "https://citi.wallstreetdocs.local/api/rest/taglib/create/"+str(id)+"?tagName="+elem.attrib['name']
                createdTagLibs.update({id:elem.attrib['name']})

            response = requests.post(postURL, data=response.content, auth=('admin', 'citi@w$d'), verify=False)

        count = count+1

tagLibsToBeDeleted = {}
for tag in listOfTagLibsPROD.values():
    if tag not in listOfTagsUAT.values():
        for id, nameOfTag in listOfTagLibsPROD.items():
            if tag == nameOfTag:
                tagLibsToBeDeleted.update({id: nameOfTag})

deletedTagLibs = {}
for id, name in tagLibsToBeDeleted.items():
    postURL = "https://citi.wallstreetdocs.local/api/rest/taglib/delete/" + str(id)
    response = requests.post(postURL, auth=('admin', 'citi@w$d'), verify=False)
    pp.pprint(response.content)
    deletedTagLibs.update({id: name})

print("All taglibs downloaded to " + tagLibPath)
print('--------')
print('Updated tag libs:')
print(updatedTagLibs)
print('Number of updated tag libs: ' + str(len(updatedTagLibs)))
print('--------')
print('Created tag libs:')
if len(createdTagLibs) > 0:
    pp.pprint(createdTagLibs)
else:
    print('No created tag libs')

print('--------')
print('Deleted tag libs:')
if len(deletedTagLibs) > 0:
    print(deletedTagLibs)
else:
    print('No deleted tag libs')



print('\n')
print('\n Starting code lib work...')

url = "https://citi.wallstreetdocs.local/api/rest/codeLibrary/list/structure/"+str(id)+".xml"
prodCodeLibXML = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)
myPRODTree = etree.fromstring(prodCodeLibXML.content, parser=utf8_parser)
numberOfAllPRODCodeLibs = len(myPRODTree[0].getchildren())



listOfCodeLibsPROD = {}
for elem in myPRODTree.iter():
    if elem.tag == 'codelib':
        try:
            listOfCodeLibsPROD.update({elem.attrib['id']: elem.attrib['name']})
        except:
            listOfCodeLibsPROD.update({elem.attrib['id']:'noName'})

#pp.pprint(listOfCodeLibsPROD)

print('PROD code lib values:')
print(listOfCodeLibsPROD)
print('Number of codelibs in PROD: ' + str(numberOfAllPRODCodeLibs))

# UAT file download
url = "https://citiuat.wallstreetdocs.local/api/rest/codeLibrary/list/structure/"+str(id)+".xml"
uatCodeLibXML = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)
myTree = etree.fromstring(uatCodeLibXML.content, parser=utf8_parser)
numberOfAllUATCodeLibs = len(myTree[0].getchildren())
print('Number of codelibs in UAT: ' + str(numberOfAllUATCodeLibs))

listOfCodeLibsUAT = {}
for elem in myTree.iter():
    if elem.tag == 'codelib':
        try:
            listOfCodeLibsUAT.update({elem.attrib['id']:elem.attrib['name']})
        except:
            pass



codeLibsToBeDeleted = {}
for tag in listOfCodeLibsPROD.values():
    if tag not in listOfCodeLibsUAT.values():
        for id, nameOfTag in listOfCodeLibsPROD.items():
            if tag == nameOfTag:
                codeLibsToBeDeleted.update({id: nameOfTag})


codeLibPath = path + "/" + today.strftime("%B %d, %Y") + "/codeLib"
try:
    os.makedirs(codeLibPath)
    print('Created directory: ' + codeLibPath)
except FileExistsError:
    print('Directory: ' + codeLibPath + ' already exists')

count = 0
createdCodeLibs = {}
updatedCodeLibs = {}
for elem in myTree.iter():
    if elem.tag == 'codelib':

        url = "https://citiuat.wallstreetdocs.local/api/rest/codeLibrary/get/"+elem.attrib['id']
        response = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)

        tagName = elem.attrib['name']

        folder = codeLibPath
        filename = urllib.parse.quote(tagName).replace("/","%2F")
        ext = ".php"

        with open(os.path.join(folder,filename+ext),'wb') as f:

            f.write(response.content)

            if elem.attrib['name'] in listOfCodeLibsPROD.values():
                prodID = (list(listOfCodeLibsPROD.keys())[list(listOfCodeLibsPROD.values()).index(elem.attrib['name'])])
                #print('UAT ID: ' + str(elem.attrib['id']) + ' and PROD ID: ' + str(prodID))
                postURL = "https://citi.wallstreetdocs.local/api/rest/codeLibrary/put/"+str(prodID)
                updatedCodeLibs.update({prodID:elem.attrib['name']})
            else:
                #print('I have not found ' + elem.attrib['name'] + ' in PROD, creating a new codeLib with this name')
                postURL = "https://citi.wallstreetdocs.local/api/rest/codeLibrary/create/"+str(id)+"?codeLibName="+elem.attrib['name']
                createdCodeLibs.update({id:elem.attrib['name']})

            response = requests.post(postURL, data=response.content, auth=('admin', 'citi@w$d'), verify=False)




        count = count+1


deletedCodeLibs = {}
for id, name in codeLibsToBeDeleted.items():
    postURL = "https://citi.wallstreetdocs.local/api/rest/codeLibrary/delete/" + str(id)
    response = requests.post(postURL, data=response.content, auth=('admin', 'citi@w$d'), verify=False)
    #print(response)
    deletedCodeLibs.update({id:name})


print('--------')
print("All codeLibs downloaded to " + codeLibPath)

print('--------')
print('Updated code libs:')
print(updatedCodeLibs)
print('Number of updated code libs: ' + str(len(updatedCodeLibs)))
print('--------')
print('Created code libs:')
if len(createdCodeLibs) > 0:
    print(createdCodeLibs)
else:
    print('No created code libs')

print('--------')
print('Deleted code libs:')
if len(deletedCodeLibs) > 0:
    print(deletedCodeLibs)
else:
    print('No deleted code libs')



pp.pprint('Sync is done. Time elapsed: ' + format(time.time() - start) + ' seconds')
#pp.pprint('done')

#print("test sys.stdout")

#pp.pprint(listOfCodeLibsUAT)
#pp.pprint(now.strftime("%A, %B %d, %Y %H:%M:%s"))

import smtplib, ssl
import getpass

port = 587  # For starttls
smtp_server = "smtp.gmail.com"
#sender_email = "attila.labai@gmail.com"
sender_email = "alabai@wallstreetdocs.com"
#receiver_email = 'attika8@gmail.com, attila.labai@citi.com, martina.labai@gmail.com'
receiver_email = 'attila.labai@citi.com, toyohiro.kajiyama@citi.com, avaiz.choudhury@citi.com'
password = 'kingwach'

#msg = MIMEMultipart()
msg = MIMEMultipart(_charset="UTF-8")
msg['From'] = sender_email
msg['To'] = receiver_email
#msg['Cc'] = Cc
msg['Subject'] = 'WSD sync has been concluded'

message = """This is an automated email with logs for the sync that occurred on """ + now.strftime("%B %d, %Y") + """ 
""" + "\n\n ========== Tag libs ========= " \
    + "\n Number of tag libs currently in UAT: " + str(len(listOfTagsUAT)) \
    + "\n Number of tag libs currently in PROD: " + str(len(listOfTagLibsPROD)) \
    + "\n Number of updated tag libs: " + str(len(updatedTagLibs)) \
    + "\n Number of created tag libs: " + str(len(createdTagLibs)) \
    + "\n Number of deleted tag libs: " + str(len(deletedTagLibs)) \
    + "\n\n ========= Code libs ========= " \
    + "\n Number of code libs currently in UAT: " + str(len(listOfCodeLibsUAT)) \
    + "\n Number of code libs currently in PROD: " + str(len(listOfCodeLibsPROD)) \
    + "\n Number of updated code libs: " + str(len(updatedCodeLibs)) \
    + "\n Number of created code libs: " + str(len(createdCodeLibs)) \
    + "\n Number of deleted code libs: " + str(len(deletedCodeLibs)) \
    + "\n\nSync has taken " + format(round(time.time() - start,2)) + ' seconds' \
    + "\n\nFor details of the regression tool prior to sync, see excel report and blackline summary files attached." \
    + "\n\n"


textPart = MIMEText(message)
msg.attach(textPart)

part = MIMEBase('application', "octet-stream")
part.set_payload(open(r""+dailyPath+"/report.csv", "rb").read())
#part.set_payload(open(r'report.csv', 'rb').read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="report.csv"')
#part.add_header('Content-Disposition', 'attachment; filename="report.csv"')
msg.attach(part)

part2 = MIMEBase('application', "octet-stream")
part2.set_payload(open(r""+dailyPath+"/blackline.docx", "rb").read())
#part.set_payload(open(r'report.csv', 'rb').read())
encoders.encode_base64(part2)
part2.add_header('Content-Disposition', 'attachment; filename="blackline.docx"')
#part.add_header('Content-Disposition', 'attachment; filename="report.csv"')
msg.attach(part2)


context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email.split(','), msg.as_string())
    server.quit()

print('Notification email has been sent out.')