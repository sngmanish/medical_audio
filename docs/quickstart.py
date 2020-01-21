from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import webbrowser
from pprint import pprint

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive']

def validate():
    creds = None

    #checks if token.pickel exists already
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    docs = build('docs', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)

    return docs,drive

def format_for_merge(key,value):
    key = f"{{{{{key}}}}}" #dont ask why 10 braces
    formatted = {
    'replaceAllText': {
        'containsText': {
            'text': key,
            'matchCase':  'true'
        },
        'replaceText': value,
        }
    }
    return formatted

def form_report(patient_info,doctor_info):
    service_docs,service_drive = validate()
    TEMPLATE_ID = '{{PUT TEMPLATE ID HERE}}'

    #document = service_docs.documents().get(documentId=DOCUMENT_ID).execute()

    date = datetime.datetime.now().strftime("%y/%m/%d")

    requests = []

    #put all entities in merge format
    for key,value in patient_info.items():
        if(type(value)!=type([])):
            requests.append(format_for_merge(key,value))
        else:
            value = "\n".join(value)
            requests.append(format_for_merge(key,value))

    for key,value in doctor_info.items():
        if(type(value)!=type([])):
            requests.append(format_for_merge(key,value))
        else:
            value = "\n".join(value)
            requests.append(format_for_merge(key,value))

    requests.append(format_for_merge("date",str(date)))

    #copy template to new file
    report_template = service_drive.files().copy(fileId=TEMPLATE_ID,body={"name":f"Report {patient['name']}"}).execute()
    report = service_docs.documents().batchUpdate(documentId=report_template['id'], body={'requests': requests}).execute()
    report_url = f"https://docs.google.com/document/d/{report['documentId']}/edit"
    webbrowser.open(report_url)

if __name__ == '__main__':
    patient = {
        'name':'Harsheet',
        'age': '21',
        'gender': 'M',
        'tests':[
            'ABL Kinase Domain Mutation in CML',
            'F-Actin (Smooth Muscle) Antibody, IgG',
            'Factor H Complement Antigen',
        ],
        "diseases":[
            'Diabetes Mellitus, Noninsulin-Dependent',
            'Lateral sinus thrombosis',
        ],
        'id':'1',
        'meds':[
            'ABL',
            'F-Actin',
            'Factor H',
        ],
        'symptoms':[
        'fever',
        'headache',
        ],
    }
    doctor = {
    'doctor_name':'Akanksha',
    'doctor_spl':'MBBS',
    }
    form_report(patient,doctor)
