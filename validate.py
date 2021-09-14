from datetime import datetime, timedelta
from datetime import date
import re


def clean_phone_str(phone):
   phone = (
     phone.replace("-", "")
            .replace("{", "")
            .replace("}", "")
            .replace("[", "")
            .replace("]", "")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
            .replace(" ", "")
             )
   return phone

def validate_contact_data(request, form_dict):
    for key in form_dict.keys():
        if  re.search("^Hint", request.form.get(key)):
            form_dict[key]['value'] = ""
        else:
            form_dict[key]['value'] = request.form.get(key)
        res_tuple = form_dict[key]['checker'](form_dict[key]['value'])
        form_dict[key]['valid']  = res_tuple[0]
        form_dict[key]['error_message'] =res_tuple[1]
        form_dict[key]['value']= res_tuple[2]
    return form_dict

def Name_checker(name):
    error_message  = ""
    valid = True
    if len(name)>50:
        error_message  = "Max len of Name is 50 char"
        valid = False
    return valid, error_message, name    
        
def Birthday_checker(birthday):
    error_message  = ""
    valid = True
    if birthday!="":
       if re.search('\d{2}\.\d{2}\.\d{4}', birthday) == None:
          error_message  = "Use dd.mm.yyyy format"
          valid = False
       else:
           birthday = datetime.strptime(birthday, '%d.%m.%Y')
    else:
       birthday = None
    return valid, error_message, birthday

def Phone_checker(phones):
    error_message  = ""
    valid = True
    phones = clean_phone_str(phones);
    for phone in phones.split(","):
       if re.search('\+{0,1}\d{9,13}', phone.strip()) == None:
            error_message  = """Phone should have format: '[+] XXXXXXXXXXXX' (9-12 digits), phones separated by ','"""
            valid = False
    return valid, error_message, phones

def ZIP_checker(zip):
    error_message  = ""
    valid = True
    if len(zip)>10:
        error_message  = "Max len of ZIP is 10 char"
        valid = False
    return valid, error_message, zip

def Country_checker(Country):
    error_message  = ""
    valid = True
    if len(Country)>50:
        error_message  = "Max len of Country is 50 char"
        valid = False
    return valid, error_message, Country

def Region_checker(Region):
    error_message  = ""
    valid = True
    if len(Region)>50:
        error_message  = "Max len of Region is 50 char"
        valid = False
    return valid, error_message, Region

def City_checker(City):
    error_message  = ""
    valid = True
    if len(City)>40:
        error_message  = "Max len of City is 40 char"
        valid = False
    return valid, error_message, City

def Street_checker(Street):
    error_message  = ""
    valid = True
    if len(Street)>50:
        error_message  = "Max len of Street is 50 char"
        valid = False
    return valid, error_message, Street

def House_checker(House):
    error_message  = ""
    valid = True
    if len(House)>5:
        error_message  = "Max len of House is 5 char"
        valid = False
    return valid, error_message, House

def Apartment_checker(Apartment):
    error_message  = ""
    valid = True
    if len(Apartment)>5:
        error_message  = "Max len of House is 5 char"
        valid = False
    return valid, error_message, Apartment

def Email_checker(email):
    error_message  = ""
    valid = True
    if re.search('[a-zA-Z0-9\.\-\_]+@[a-zA-Z0-9\-\_\.]+\.[a-z]{2,4}', email) == None:
        error_message  = "Email should have format: 'name@domain.[domains.]high_level_domain'"
        valid = False
    return valid, error_message, email

form_dict_temp = {"Name":{
                           "value": "Hint: Input first and second name in one row",
                           "valid": True,
                           "checker": Name_checker,
                           "error_message":""
                         },
                  "Birthday":
                        {
                           "value":"Hint: Use dd.mm.yyyy format",
                           "valid": True,
                           "checker": Birthday_checker,
                           "error_message":""
                        },
                 "Email":
                        {
                           "value":"Hint: Use user@domain format",
                           "valid": True,
                           "checker": Email_checker,
                           "error_message":""
                        },
                 "Phone":
                        {
                           "value":"Hint: Use + or digits only, phones separate by ','",
                           "valid": True,
                           "checker": Phone_checker,
                           "error_message":""
                        },    
                 "ZIP":
                        {
                           "value":"Hint: Up to 10 char",
                           "valid": True,
                           "checker": ZIP_checker,
                           "error_message":""
                        },
                 "Country":
                        {
                           "value":"Hint: Up to 50 char",
                           "valid": True,
                           "checker": Country_checker,
                           "error_message":""
                        },
                 "Region":
                        {
                           "value":"Hint: Up to 50 char",
                           "valid": True,
                           "checker": Region_checker,
                           "error_message":""
                        },
                 "City":
                        {
                           "value":"Hint: Up to 40 char",
                           "valid": True,
                           "checker": City_checker,
                           "error_message":""
                        },
                 "Street":
                        {
                           "value":"Hint: Up to 50 char",
                           "valid": True,
                           "checker": Street_checker,
                           "error_message":""
                        },
                 "House":
                        {
                           "value":"",
                           "valid": True,
                           "checker": House_checker,
                           "error_message":""
                        },
                 "Apartment":
                        {
                           "value":"",
                           "valid": True,
                           "checker": Apartment_checker,
                           "error_message":""
                        },
                }

