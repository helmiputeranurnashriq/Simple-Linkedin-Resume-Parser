
"""
Resume Parser Project (Python)
Developed by: Helmi Putera Nurnashriq Bin Aziz

Comment:
This project was created using basic python, slice-string-list method. 
Hopefully, there are someone who are willing to improve the system in the future.

Limitation:
Only linkedin resume format can be tested using this script
OOP is not included.

"""

#Import PDFMiner Library
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams #LTTextBox, LTTextLine, LTFigure, LTTextBoxHorizontal, LTTextBoxVertical
from pdfminer.pdfpage import PDFPage
from io import StringIO


#System Module
import re
import os
import pandas as pd
import csv
from time import process_time


language_data = []
skill_data = []
with open("language.csv", "rt") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        language_data.append(''.join(row))

#This is location of file
path = "Profile3.pdf"

#PDFMiner Engine
def convert_pdf_to_txt(path,value):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams(line_margin=value, char_margin=1)
    device = TextConverter(rsrcmgr, retstr,      codec=codec,laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text
pdf_miner_text = convert_pdf_to_txt(path,value = 0)
pdf_miner_text1 = convert_pdf_to_txt(path,value = 1)

 
#This Function is different compared to function of convert_pdf_to_text because it returns different format.
#The aim of this function is to extract applicant name
def pdf_margin_adjusted(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams(line_overlap = 0.5,
                        char_margin = 20,
                        line_margin = 50,
                        word_margin = 2,
                        boxes_flow = 1,
                        detect_vertical = False,
                        all_texts = False)

    device = TextConverter(rsrcmgr, retstr,      codec=codec,laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text.strip()

def extract_name():
    #changing format of text and then split up into list, we can assign a logic where the first index of a list will be applicant name
    pdf_text = pdf_margin_adjusted(path)
    pdf_text = pdf_text.split("\n")
    return pdf_text[0].upper()

#Data Mining using regex
def extract_email():
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    if r == []:
        return "Not found"
    return r.findall(pdf_miner_text)

def extract_phone_numbers():
    r = re.compile(r'\d\d\d\d\d\d\d\d+')
    phone_numbers = r.findall(pdf_miner_text)
    if phone_numbers == []:
        return "Not found"
    return [re.sub(r'\D', '', number) for number in phone_numbers]
    

#To get any possible link from resume.
def extract_hyperlink():
    #link_type1 = re.findall("https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)", pdf_miner_text.replace("\n\n", " "))
    link_extract = re.findall("[https?://]?(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-/a-zA-Z0-9()@:%_\\+.~#?&\\/=]*).\s[-a-zA-Z0-9()]+", pdf_miner_text1)
    link_extract = [x.replace("\n", "") for x in link_extract]
    link_extract = str(link_extract).replace(" ","")
    if link_extract == []:
        return "Not found"
    return ''.join(link_extract)


# Here we are transforming data because regex returns none 
# We were using basic python to manipulate text into usefull information/data
# variable_name[1:-1] is used to extract only list that has values. 
resume_text = ' -'.join(pdf_miner_text.split("\n\n"))
resume_text = resume_text.replace("\n"," ")


language_proficiency = []
skill_proficiency = []
achievementList = []

def extract_languages():
    language_list = re.findall("(?<=Languages )(.*)(?=Honors-Awards )", resume_text)
    language_list = str(language_list).split("-")
    language_list = language_list[1:-1]
    language_list = [x.rstrip() for x in language_list]

    if language_list == []:
        return "Not found"

    return language_list

# Require classfication method
def top_skills_extract():
    topSkill_list = re.findall("(?<=Top Skills )(.*)(?=Languages )", resume_text)
    topSkill_list = str(topSkill_list).split("-")
    topSkill_list = topSkill_list[1:-1]
    topSkill_list = [x.rstrip() for x in topSkill_list]
    if topSkill_list == []:
        return "Not found"
    return topSkill_list


honor_awards_data = []
def extract_honor_awards():

    honors_award_list = re.findall("(?<=Honors-Awards )(.*)(?=Summary )", resume_text1)
    # honors_award_list = str(honors_award_list).split("-")
    # honors_award_list = honors_award_list[1:-1]
    if honors_award_list == []:
        return "Not found"

    return honors_award_list

def extract_summary():
    if re.findall("(?<=Summary )(.*)(?=Experience )", pdf_miner_text.replace("\n", " ")) == []:
        return "Not found"
    return re.findall("(?<=Summary )(.*)(?=Experience )", pdf_miner_text.replace("\n", " "))


#Append for each item to list
companyName = []
positionName = []
Duration = []

def extract_experience():

    #regex cannot reads "\n" inside text and it returns no value. Therefore, replace "\n" with some space + symbol were used to split text into a list.
        experience_list = re.findall("(?<=Experience )(.*)(?=Education )", pdf_miner_text1.replace("\n"," -")) or re.findall("(?<=Pengalaman )(.*)(?=Pendidikan )", pdf_miner_text1.replace("\n"," -")) 
        experience_list = str(experience_list).split("- -")[1:-1]
        experience_list = [x.replace("\\xa0","") for x in experience_list]
        experience_list = [x.split("-") for x in experience_list]

        previous_work = experience_list[0]
        companyName.append(previous_work[0])
        positionName.append(previous_work[1])
        Duration.append(previous_work[3])



resume_text1 = ':'.join(pdf_miner_text1.split("\n\n"))
resume_text1 = resume_text1.replace("\n"," :")


education_name = []
education_level = []
education_major = []

def extract_education_place():
    #Data extraction for resume type 1
    string_to_remove = "\\xa0"
    education_list = re.findall("(?<=Education )(.*)(?= )", resume_text1) or re.findall("(?<=Pendidikan )(.*)(?= )", resume_text1)
    education_list = str(education_list).replace(string_to_remove,"").split(":")
    education_list = education_list[1:-1]
    education_list = [x.rstrip() for x in education_list]
    
    #Different format of linkedin resume requires conditional statement
    #Data extraction for resume type 2
    if education_list == []:
        resume_text3 = ' :'.join(pdf_miner_text1.split("\n\n"))
        resume_text3 = resume_text3.replace("\n"," :")

        education_list = re.findall("(?<=Education )(.*)(?= )", resume_text3) or re.findall("(?<=Pendidikan )(.*)(?= )", resume_text3)
        education_list = str(education_list).replace(string_to_remove,"").split(":")
        education_list = education_list[1:-1]
        education_list = [x.rstrip() for x in education_list]
        education_set =  education_list[1].split("·")
        education_set = education_set[0].split(",")
        

        education_name.append(education_list[0])
        education_level.append(education_set[0])
        education_major.append(education_set[1])
        
    #Data extraction for resume type 1
    else:
        education_set =  education_list[1].split("·")
        education_set = education_set[0].split(",")
        education_name.append(education_list[0])
        education_level.append(education_set[0])
        education_major.append(education_set[1])


#------OUTPUT-------

if __name__ == "__main__":
            #call the function to execute
            extract_experience()
            extract_languages()
            top_skills_extract()
            extract_education_place()

            #Store data into pandas
            dataset = {
                "Applicant Name" : extract_name(),
                "Phone Number" :  extract_phone_numbers(),
                "Email" : extract_email(),
                "HyperLink" : extract_hyperlink(),
                "Previous Company" : companyName,
                "Previous Position" :positionName,
                "Previous University" :education_name,
                "Course" :education_level,
                "Major" : education_major
            }
            #Create pandas from dictionary
            dataset_pandas = pd.DataFrame.from_dict(dataset)
            
            #Create new file if not exist
            file_path = "applicantData.csv"
            if not os.path.isfile(file_path):
                dataset_pandas.to_csv("applicantData.csv", header = "column_names", index = False)

            #Set header = None to avoid overwrite header
            else:
                dataset_pandas.to_csv(file_path, mode ="a", header = None, index = False)
            print(f"{path} has been exported to csv")
            print("Processing time: ", process_time(), "Seconds")
