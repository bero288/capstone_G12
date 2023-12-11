import numpy as np
from flask import Flask, request, render_template, jsonify, session, abort, redirect
from google_auth_oauthlib.flow import Flow
import pickle
import requests
import os
import pathlib
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
#Create an app object using the Flask class. 
app = Flask(__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"]= "1"
#environment variables I must clean them and put in .env
app.secret_key = "ebraam"
GOOGLE_CLIENT_ID = "91192143570-1i15b3heae4urduum6bnopppms81th4t.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client-secret.json")
flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets_file, scopes=["https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email", "openid"], redirect_uri="http://127.0.0.1:5000/callback")
#Load the trained model. (Pickle file)
model = pickle.load(open('models/rf_(1).pkl', 'rb'))

#check authorized users
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else: return function()
    return wrapper
#Define the route to be home. 
#The decorator below links the relative route of the URL to the function it is decorating.
#Here, home function is with '/', our root directory. 
#Running the app sends us to index.html.
#Note that render_template means it looks for the file in the templates folder. 

#use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def home():
        return render_template('login.html')

@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["token"] = credentials.token
    return redirect("/google-fit-data")
    
@app.route('/logout')
def logout():
    session.clear()
    return "logout"

@app.route('/protected_area')
@login_is_required
def protected_area():
    return render_template('protected.html')

#You can use the methods argument of the route() decorator to handle different HTTP methods.
#GET: A GET message is send, and the server returns data
#POST: Used to send HTML form data to the server.
#Add Post method to the decorator to allow for form submission. 
#Redirect to /predict page with the output
@app.route('/predict',methods=['POST'])
def predict():
    data = request.json 
    response_data = { 'message': 'Response from Flask server' }
    ##int_features = [float(x) for x in request.args()] #Convert string inputs to float.
    ##features = [np.array(int_features)]  #Convert to the form [[a, b]] for input to the model
    ##prediction = model.predict(features)  # features Must be in the form [[a, b]]

    ##output = round(prediction[0], 2)

    return jsonify(response_data)


#When the Python interpreter reads a source file, it first defines a few special variables. 
#For now, we care about the __name__ variable.
#If we execute our code in the main program, like in our case here, it assigns
# __main__ as the name (__name__). 
#So if we want to run our code right here, we can check if __name__ == __main__
#if so, execute it here. 
#If we import this file (module) to another file then __name__ == app (which is the name of this python file).

@app.route('/google-fit-data', methods=['GET'])
def send_google_fit_request():
    access_token = session.get('token')  # Retrieve access token from the session

    if access_token:
        url = 'https://www.googleapis.com/fitness/v1/users/me/dataSources'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.ok:
            data = response.json()
            # Process the response data as needed
            return data
        else:
            # Handle the error response
            return f'Request failed with status code {response.status_code}'
    else:
        # Access token not found in the session
        return 'Access token not available'

if __name__ == "__main__":
    app.run()