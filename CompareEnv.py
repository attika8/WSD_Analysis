import os
import sys
from datetime import date

import requests
import urllib3
from lxml import etree
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
utf8_parser = etree.XMLParser(encoding='utf-8')

#1234

path = os.getcwd()+"/"+date.today().strftime("%B %d, %Y")
try:
    os.makedirs(path)
except FileExistsError:
    pass

def print_path_of_elems(elem, elem_path=""):
    for child in elem:
        if not child.getchildren() and child.text:
            try:
                print(child.attrib['name'])
            except KeyError:
                pass

            if child.tag == 'number' or child.tag == 'text' or child.tag == 'date':
                print("%s/%s" % (elem_path, child.tag))
            else:
                print("%s/%s, %s" % (elem_path, child.tag, child.text))
        else:
            try:
                tagName = child.attrib['name']
                print("%s/%s" % (elem_path, tagName))
            except KeyError:
                tagName = child.tag

            print_path_of_elems(child, "%s/%s" % (elem_path, tagName))

def createUIXMLoutput(url,env):
    XML = requests.get(url, auth=('admin', 'citi@w$d'), verify=False)
    root = etree.fromstring(XML.content, parser=utf8_parser)
    with open(os.getcwd() + "/" + date.today().strftime("%B %d, %Y") + "/" + env + ".txt", "w") as f:
        sys.stdout = f
        print_path_of_elems(root, root.tag)
        f.close()

environments = ['UAT','PROD']
for env in tqdm(environments):
    if env == 'UAT':
        url = "https://citiuat.wallstreetdocs.local/api/rest/termSheet/50556.xml"
    else:
        url = "https://citi.wallstreetdocs.local/api/rest/termSheet/46186.xml"
    createUIXMLoutput(url,env)

os.chdir(path)

numberOfFiles = (os.listdir(path))

if len(numberOfFiles) >= 2:
    with open('UAT.txt', 'r') as file1:
        with open('PROD.txt', 'r') as file2:
            os.system("sort UAT.txt PROD.txt | uniq -u")