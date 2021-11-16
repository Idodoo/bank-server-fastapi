from fastapi import FastAPI, Body, Request, HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, oauth2
import json
import os


app = FastAPI()

oauth_scheme = OAuth2PasswordBearer(tokenUrl = "token")


BASE_FOLDER = r''
BASE_NAME = 'userdb.json'
spend = 'spendhistory.json'
credit = 'credithistory.json'
balance = 'userbalance.json'
userdb = os.path.join(BASE_FOLDER, BASE_NAME)
spendhistroy =os.path.join(BASE_FOLDER, spend)
credithistory = os.path.join(BASE_FOLDER, credit)
user_balance = os.path.join(BASE_FOLDER, balance)



@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    with open(userdb, "r") as json_file:
      json_data = json.load(json_file)
      if json_data:
        #   Check if the username is present
        password = json_data.get(form_data.username)
        if password:
            print("Wrong Username or Password. Re-enter")
            raise HTTPException(status_code = 403, detail = "Incorrect Username or Password")     
    # To Check if the username is the DB, and the  password matches
    print({"access_token": "form_data.username", "token_type":"bearer"})
    return {"access_token": form_data.username, "token_type":"bearer"}
    


@app.get("/spend/history")
def spend_histroy(token: str = Depends(oauth_scheme)):
    # spend history logic
    with open (spendhistroy, "r") as spend_hist:
        spend_hist_data = json.load(spend_hist)
        if not spend_hist_data.get(token):
            print(token)
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Username not found in the spend history DB")
        return{"username": token, "spend_hist": spend_hist_data[token]}
    

@app.get("/creditcard/history")
def credit_history(token: str = Depends(oauth_scheme)):
     with open (credithistory, "r") as credit_hist:
        credit_hist_data = json.load(credit_hist)
        if not credit_hist_data.get(token):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Username not found in the credit history DB")
        return{"username": token, "credit_hist": credit_hist_data[token]}

@app.post("/transfer/money")
def transfer_money(token: str = Depends(oauth_scheme), destination_user: str = Body(...), amount_to_transfer: float = Body(...)):  
    print(token)
    print(destination_user)
    print(amount_to_transfer)
    with open(user_balance , "r") as userbalance_file:
        userbalance_data = json.load(userbalance_file)
        # Current user balance
        curr_user_bal = userbalance_data.get(token)['curr_balance']
        print(f"Current user balance is{curr_user_bal}")
        # Destination user balance 
        dest_user_bal =  userbalance_data.get(destination_user)
        print(dest_user_bal)
        if not dest_user_bal:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invaild Destination User, Cannot transfer amount")
        print(f"Destination User Balance = {dest_user_bal}") 
        if curr_user_bal - amount_to_transfer < 0:
            raise HTTPException(status_code = 400, detail = "Amount to transfer is greater than account balance. Cannot transfer")
        userbalance_data[token]['curr_balance'] -=   amount_to_transfer
        userbalance_data[destination_user]['curr_balance'] +=   amount_to_transfer
        with open(user_balance, "w") as userbal_write:
             json.dump(userbalance_data, userbal_write)
             return{
                 "username":token,
                 "message" : f"Money {amount_to_transfer} successfully Transferred to {destination_user}"
             }

@app.get("/userbalance")
def get_userbalance(token: str = Depends(oauth_scheme)):
    with open (user_balance, "r") as userfile:
        userbalance = json.load(userfile)
    if  not userbalance.get(token):
         raise HTTPException(status_code = 403, detail = "Invaild User")  
    return {"username": token, "current_balance": userbalance.get(token)['curr_balance']}  


    



        