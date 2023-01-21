# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Text, List, Any, Dict
import requests
from rasa_sdk import Action,Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import re
import psycopg2
import random
import twilio
from twilio.rest import Client

states_ut = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh','Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli', 'Daman and Diu', 'Lakshadweep', 'National Capital Territory of Delhi', 'Puducherry']

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_birth_death_form"

    def validate_full_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `full_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"full_name": None}
        return {"full_name": name}

    def validate_email_id(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is not None:
            if re.match(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", slot_value.strip()):
                return {"email_id" : slot_value}
        dispatcher.utter_message(text = "Please enter a valid email id ")    
        return {"email_id" : None} 


    # bd_list = ["birth","Birth", "death","Death", "BIRTH","DEATH"]
    # def validate_birth_death(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        # if slot_value is not None:
            #  if slot_value.strip() in bd_list:
                        # return {"birth_death" : slot_value}
        # dispatcher.utter_message(text = "Please enter a valid email id ")    
        # return {"birth_death" : None} 
    
    def validate_date_of_event(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
     if slot_value is not None:         
             return {"date_of_event" : slot_value}
     dispatcher.utter_message(text = "Please enter a valid date within 21 days of the event ")    
     return {"date_of_event" : None}  
    

    
    def validate_gender(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        gender_list =["Male","male","MALE","Female","female","FEMALE","Others","others","OTHERS"]
        if slot_value is not None:
         if slot_value.strip() in gender_list:
                            return {"birth_death" : slot_value}
        dispatcher.utter_message(text = "Please enter a valid email id ")    
        return {"birth_death" : None} 

    def validate_mobile_number(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is not None:
            if re.match(r"^(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[789]\d{9}$", slot_value.strip()):
                return {"mobile_number" : slot_value}
        dispatcher.utter_message(text = "Please enter a valid mobile number ")    
        return {"mobile_number" : None}  
    
    def validate_state(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is not None:
            if slot_value.strip() in states_ut:
                return {"state" : slot_value}      
        dispatcher.utter_message(text = "Please enter a valid state name ")
        return {"state" : None}

    def validate_district(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is not None:
            return {"district" : slot_value}
        dispatcher.utter_message(text = "Please enter a valid district name ")
        return {"district" : None}
    
    
class ValidateAadharForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_aadhar_val_form"    

        
    def validate_aadhar_number(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is not None:
            if re.match(r"^\d{12}$", slot_value.strip()):
                aadhar = slot_value

                conn = psycopg2.connect(
                    host="localhost",
                    database="postgres",
                    user="postgres",
                    password="Navyashree@123"
                )
                cur = conn.cursor()
                cur.execute(f"SELECT phone FROM aadhar WHERE aadharnumber='{aadhar}'")
                global phone_number
                phone_number = cur.fetchone()[0]
                print(phone_number)
                cur.close()
                conn.close()
                # return [SlotSet("phone_number", phone_number)]
                otp = random.randint(1000, 9999)
                account_sid = 'AC131f6a0383058a21a9a5374d1c2322d8'
                auth_token = '37a3dae8a5a94ac37f83151c6a715b6d'
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    body=f"Your OTP is {otp}",
                    from_='+19293771105',
                    to=phone_number
                )
                # return {"aadhar_number" : slot_value}
                return [SlotSet(("otp", otp))]
        dispatcher.utter_message(text = "Please enter a valid aadhar number ")    
        return {"aadhar_number" : None}
        

    def validate_otp_npr(self, slot_value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is not None:
            if re.match(r"^\d{4}$", slot_value.strip()):
                return {"otp_npr" : slot_value}
        dispatcher.utter_message(text = "Please enter a Valid OTP ")
        otp = tracker.get_slot("otp")
        user_given_otp = slot_value
        if user_given_otp == otp:
            dispatcher.utter_message(text="otp is verified")
        return {"otp_npr" : None}                
      


     



   
   

 
 
 
 
 
 
 
 
 
 
 











        

   
   
   
   
   
   

   
   
   
   
   
   
   
   
   