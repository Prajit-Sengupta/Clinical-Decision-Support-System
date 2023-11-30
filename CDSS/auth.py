from flask import Flask, request, jsonify, render_template, redirect, session
from flask_mail import Mail, Message
import traceback
import mysql.connector
import pyotp,time
from werkzeug.security import generate_password_hash, check_password_hash
from zxcvbn import zxcvbn
import re
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import tensorflow as tf
import numpy as np
import PyPDF2
import re
import pandas as pd
import subprocess
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'       # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = ''   # Replace with your MySQL password
app.config['MYSQL_DB'] = 'loginorregister'   # Replace with your MySQL database name
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key for session management

# Configure Flask-Mail with your email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''

mail = Mail(app)

connection = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)

# Check if the connection with the database is established
if connection.is_connected():
    print("Connected to the database")
else:
    print("Failed to connect to the database")
    exit(0)

cursor = connection.cursor()

def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
    otp = totp.now()
    return otp, totp.secret

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            local_connection = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB']
            )
            local_cursor = local_connection.cursor()

            # Perform login logic
            query = "SELECT * FROM users WHERE username = %s"
            local_cursor.execute(query, (username,))
            user = local_cursor.fetchone()

            if user and check_password_hash(user[2], password):
                message = 'Login successful'
                return render_template('patients.html',username=username)
            else:
                message = 'Invalid credentials'

        except mysql.connector.Error as error:
            message = 'An error occurred during login.'

        finally:
            if local_connection.is_connected():
                local_cursor.close()
                local_connection.close()

    return render_template('example.html', message=message)

@app.route('/patientsSuccess')
def patientsSuccess():
    return render_template('patientSuccess.html')

@app.route('/patients')
def patients():
    return render_template('patients.html')

def extract_text_from_pdf(pdf_file_path):
    try:
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            if len(pdf_reader.pages) == 0:
                return "The PDF file is empty."

            extracted_text = ''
            for page in pdf_reader.pages:
                extracted_text += page.extract_text()

            return extracted_text
    except FileNotFoundError:
        return f"Error: The file '{pdf_file_path}' not found."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

# @app.route('/sentiment_analysis',methods=['GET', 'POST'])
# def sentimentAnalysis():
#     if request.method == 'POST':
#         pdf1 = "static/Test Result/"+request.files['pdf1'].filename
#         pdf2 = "static/Test Result/"+request.files['pdf2'].filename
#         pdf3 = "static/Test Result/"+request.files['pdf3'].filename

#         #result="First Test: {}\nSecond Test: {}\nThird Test: {}".format(extract_text_from_pdf(pdf1),extract_text_from_pdf(pdf2),extract_text_from_pdf(pdf3))

#         result1="First Test: {}".format(tb_report(pdf1))
#         result2="Second Test: {}".format(tb_report(pdf2))
#         result3="Third Test: {}".format(tb_report(pdf3))

#         return jsonify({'result1': result1, 'result2': result2, 'result3': result3})
        
#     return render_template('sentiment-analysis.html')

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

@app.route('/sentiment_analysis', methods=['GET', 'POST'])
def sentimentAnalysis():
    if request.method == 'POST':
        # Create a directory if it doesn't exist
        directory = "static/Test Result/"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the uploaded files
        for pdf_key in ['pdf1']:
            file = request.files[pdf_key]
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(directory, filename))

        # Assume tb_report is your function to analyze the PDF
        # Update these paths as needed
        pdf1 = os.path.join(directory, request.files['pdf1'].filename)

        result1 = "First Test: {}".format(tb_report(pdf1))

        return jsonify({'result1': result1})

    return render_template('sentiment-analysis.html')


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
            
    # Load your custom model
    model = tf.keras.models.load_model('model_T2.h5')
    file_path="Test Images/"+file.filename
    # Load the image
    img = image.load_img(file_path, target_size=(224, 224))

    # Convert the image to a numpy array
    img_array = image.img_to_array(img)

    # Expand dimensions to match the input shape of the model
    img_array_expanded = np.expand_dims(img_array, axis=0)

    # Preprocess the image
    preprocessed_img = preprocess_input(img_array_expanded)

    # Make predictions
    predictions = model.predict(preprocessed_img)

    # Get the predicted class
    result = 'Tuberculosis' if predictions > 0.5 else 'Normal'
    
    return jsonify({'filename': result})

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        try:
            local_connection = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB']
            )
            local_cursor = local_connection.cursor()

            # Check if the username already exists
            query = "SELECT * FROM users WHERE username = %s"
            local_cursor.execute(query, (username,))
            existing_user = local_cursor.fetchone()

            if existing_user:
                message = 'Username already exists'
            else:
                # Generate OTP
                otp, otp_secret = generate_otp()

                # Store the OTP secret and username in session for validation
                session['otp_secret'] = otp_secret
                session['username'] = username
                session['password'] = password
                session['email'] = email

                # Send OTP to the user's email
                send_otp_email(email, otp)

                return redirect('/verify_otp')

        except mysql.connector.Error as error:
            message = 'An error occurred during registration.'

        finally:
            if local_connection.is_connected():
                local_cursor.close()
                local_connection.close()

    return render_template('register.html', message=message)

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp_value = request.form['otp']
        otp_secret = session.get('otp_secret')
        username = session.get('username')
        password = session.get('password')
        email = session.get('email')

        # Validate OTP
        totp = pyotp.TOTP(otp_secret, interval=300)
        if totp.verify(otp_value):
            try:
                local_connection = mysql.connector.connect(
                    host=app.config['MYSQL_HOST'],
                    user=app.config['MYSQL_USER'],
                    password=app.config['MYSQL_PASSWORD'],
                    database=app.config['MYSQL_DB']
                )
                local_cursor = local_connection.cursor()

                # Hash password before storing
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

                # Use parameterized query to avoid SQL Injection
                query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
                local_cursor.execute(query, (username, hashed_password, email))
                local_connection.commit()

                print("User successfully created")  # Debugging print statement
                email = session.get('email')
                send_welcome_email(email)
                return redirect('/register_success')

            except mysql.connector.Error as error:
                # Provide generic error message
                print(f"An error occurred during registration: {error}")  # Debugging print statement
                return jsonify({'message': 'An error occurred during registration.'})

            finally:
                if local_connection.is_connected():
                    local_cursor.close()
                    local_connection.close()

        else:
            message = 'Invalid OTP'
            return render_template('verification.html', message=message)

    return render_template('verification.html')

@app.route('/register_success')
def register_success():
    print("email::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    return render_template('registration_success.html')

@app.route('/symptoms')
def symptoms():
    return render_template('Symptoms.html')


from datetime import datetime

@app.route('/submit_answers/<int:patient_id>', methods=['POST','GET'])
def submit_answers(patient_id):
    print(request.form)
    if request.method == 'POST':
    # Here, you will extract the form data and store it in the database
        q1_answer = request.form.get('q1')
        q2_answer = request.form.get('q2')
        q3_answer = request.form.get('q3')
        q4_answer = request.form.get('q4')
        q5_answer = request.form.get('q5')
        # ... Add more if you have more questions
        #session['patient_id']=patient_id
        # You'll need to determine the patient's id. 
        # This is just a placeholder, adjust this to fit your system.
        #patient_id = session['patient_id']
        print(patient_id, q1_answer, q2_answer, q3_answer, q4_answer, q5_answer)
        try:
            # Store in the database
            local_connection = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB']
            )
            local_cursor = local_connection.cursor()

            # Insert answers into the database
            query = """
            INSERT INTO patient_symptoms (patient_id,q1_answer, q2_answer, q3_answer, q4_answer, q5_answer)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            local_cursor.execute(query, (patient_id, q1_answer, q2_answer, q3_answer, q4_answer, q5_answer))
            local_connection.commit()

            # Close cursor and connection
            local_cursor.close()
            local_connection.close()

            # Redirect to a success page or wherever you'd like
            return render_template('Symptoms.html')

        except mysql.connector.Error as error:
            # Log and handle the error appropriately
            return "An error occurred. Please try again."

@app.route('/add_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        age = request.form['patient_age']
        gender = request.form['patient_gender']
        previous_diseases = request.form['previous_diseases']

        try:
            # Create a new local connection
            local_connection = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB']
            )
            local_cursor = local_connection.cursor()

            query = """
            INSERT INTO patients ( patient_name, age, gender, previous_diseases, added_date) 
            VALUES (%s, %s, %s, %s, NOW())
            """
            # Use a static doctor_id for now, replace this with the logged-in doctor's ID
            doctor_id = 1  
            local_cursor.execute(query, (patient_name, age, gender, previous_diseases))
            local_connection.commit()
            return redirect('/patientsSuccess')  # Redirect to a success page

        except mysql.connector.Error as error:
            print(f"Error: {error}")
            return jsonify({"error": "Failed to add patient"})

        finally:
            if local_connection.is_connected():
                local_cursor.close()
                local_connection.close()

    return render_template('newPatient.html')

@app.route('/existing_patients', methods=['GET', 'POST'])
def existing_patients():
    try:
        local_connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        local_cursor = local_connection.cursor(dictionary=True)  # Use dictionary=True to get results as dict

        query = "SELECT * FROM patients"  # Adjust the table name if it's different
        local_cursor.execute(query)
        patients = local_cursor.fetchall()
       
        return render_template('existingPatient.html', patients=patients)

    except mysql.connector.Error as error:
        print(f"An error occurred while fetching patients: {error}")
        return "An error occurred while fetching patient data."

    finally:
        if local_connection.is_connected():
            local_cursor.close()
            local_connection.close()

def send_welcome_email(recipient_email):
    msg = Message('Welcome to Our App', sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
    
    # Plain text version
    msg.body = f"""\
    Welcome to Our App!
    
    We're excited to have you on board. Thank you for registering with us.
    
    If you have any questions or need assistance, feel free to contact our support team.
    
    Thanks,
    Your Company Team
    """

    # HTML version
    msg.html = f"""\
    <html>
        <body>
            <h2>Welcome to Our App!</h2>
            <p>We're excited to have you on board. Thank you for registering with us.</p>
            <p>If you have any questions or need assistance, feel free to contact our support team.</p>
            <br>
            <p>Thanks,</p>
            <p>Your Company Team</p>
        </body>
    </html>
    """
    mail.send(msg)

def send_otp_email(recipient_email, otp):
    msg = Message('Registration OTP', sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
    
    # Plain text version
    msg.body = f"""\
    Welcome to Our Service!
    
    We're excited to have you on board. To complete your registration, please verify your email address by entering the following One Time Password:
    
    OTP: {otp}
    
    This OTP is valid for 5 minutes.
    
    If you did not make this request, please ignore this email or contact support if you have questions.
    
    Thanks,
    Your Company Team
    """

    # HTML version
    msg.html = f"""\
    <html>
        <body>
            <h2>Welcome to Our Service!</h2>
            <p>We're excited to have you on board. To complete your registration, please verify your email address by entering the following One Time Password:</p>
            <h3 style="color: #3498db;">{otp}</h3>
            <p>This OTP is valid for 5 minutes.</p>
            <br>
            <p>If you did not make this request, please ignore this email or contact support if you have questions.</p>
            <br>
            <p>Thanks,</p>
            <p>Your Company Team</p>
        </body>
    </html>
    """
    mail.send(msg)

def tb_report(pdf_file_path):
    pdfFileObj = open(pdf_file_path, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    extracted_text = []
    for page_num in range(len(pdfReader.pages)):
        page = pdfReader.pages[page_num]
        text = page.extract_text()
        extracted_text.append(text)
    df = pd.DataFrame({'Page_Number': range(1, len(extracted_text) + 1), 'Text': extracted_text})
    pdfFileObj.close()
    str=""
    for i in df['Text']:
        str=str+i
    text = str
    text_without_newlines = ' '.join(text.split('\n'))
    text1 =text_without_newlines
    lines = text1.split('●')
    data = {}
    for line in lines:
        parts = line.split(':')
        if len(parts) > 1:
            key = parts[0].strip()
            value = ':'.join(parts[1:]).strip()
            data[key] = [value]
    df = pd.DataFrame(data)
    df.drop(['Tuberculosis Report Patiala TB hospital Patient Information'],axis=1,inplace=True)
    t=df['Sputum Culture'][0]
    cleaned_text = t.replace('Diagnosis:', '').strip()
    df['Sputum Culture'] = cleaned_text
    df.drop(df.columns[-1], axis=1, inplace=True)
    dft=df.T
    dft_string = dft.to_string()
    print(dft_string)
    return dft_string

def find_data():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'creds.json'
    SAMPLE_SPREADSHEET_ID = '1FEOpxxmAPWEPO76JvMr5aMVtwYj-FmRMVK18RNdtLyc'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1").execute()
    values = result.get('values', [])
    df = pd.DataFrame(values)
    headers = df.iloc[0]
    df = df[1:]
    df.columns = headers
    if not df.empty:
        non_empty_rows = df.dropna(how='all')
        last_value = non_empty_rows.iloc[-1].dropna().values[-1]
    else:
        last_value = None 
    print(last_value) 
    return last_value
    



# def extract_text_from_pdf(pdf_file_path):
#     try:
#         with open(pdf_file_path, 'rb') as file:
#             pdf_reader = PyPDF2.PdfReader(file)

#             if len(pdf_reader.pages) == 0:
#                 return "The PDF file is empty."

#             extracted_text = ''
#             for page in pdf_reader.pages:
#                 extracted_text += page.extract_text()

#             return find_tb_status(extracted_text)
#     except FileNotFoundError:
#         return f"Error: The file '{pdf_file_path}' not found."
#     except Exception as e:
#         return f"Error: {str(e)}"

# def find_tb_status(text_data):
#     # Define regular expressions to search for specific patterns
#     tb_positive_patterns = [
#         r'\b(tb\s*positive)\b',
#         r'\b(\s*positive\s*Tuberculosis)\b',
#         r'\b(tb[\w\s]*pos(itive)?)\b',
#         r'\b(positive for tb)\b',
#         r'\b(active tb)\b',
#         r'\b(tb infection detected)\b',
#         r'\b(tb present)\b',
#         r'\b(tb\s*diagnosed)\b',
#         r'\b(tb\s*infection)\b',
#     ]
    
#     tb_negative_patterns = [
#         r'\b(tb\s*negative)\b',
#         r'\b(tb[\w\s]*neg(ative)?)\b',
#         r'\b(negative for tb)\b',
#         r'\b(no active tb)\b',
#         r'\b(no tb infection detected)\b',
#         r'\b(no evidence of tb)\b',
#         r'\b(tb\s*not\s*detected)\b',
#     ]

#     # Check for positive patterns
#     for pattern in tb_positive_patterns:
#         if re.search(pattern, text_data, re.IGNORECASE):
#             return 'TB Positive'

#     # Check for negative patterns
#     for pattern in tb_negative_patterns:
#         if re.search(pattern, text_data, re.IGNORECASE):
#             return 'TB Negative'

#     return 'TB status not mentioned or unclear'

# @app.route('/start_script', methods=['POST'])
# def run_script():
#     # Logic to run your Python file on the Jetson device
#     # For example:
#     import subprocess
#     subprocess.run(['python', 'Desktop/final_send_data.py'])
#     return 'Script executed'
# @app.route('/existing_patients', methods=['GET', 'POST'])
# def existing_patients():
#     try:
#         local_connection = mysql.connector.connect(
#             host=app.config['MYSQL_HOST'],
#             user=app.config['MYSQL_USER'],
#             password=app.config['MYSQL_PASSWORD'],
#             database=app.config['MYSQL_DB']
#         )
#         local_cursor = local_connection.cursor(dictionary=True)  # Use dictionary=True to get results as dict

#         query = "SELECT * FROM patients"  # Adjust the table name if it's different
#         local_cursor.execute(query)
#         patients = local_cursor.fetchall()
       
#         return render_template('existingPatient.html', patients=patients)

#     except mysql.connector.Error as error:
#         print(f"An error occurred while fetching patients: {error}")
#         return "An error occurred while fetching patient data."

#     finally:
#         if local_connection.is_connected():
#             local_cursor.close()
#             local_connection.close()



@app.route('/Scipt', methods=['GET', 'POST'])
def Scipt():
    try:
        return render_template('Scipt.html')
    except Exception as e:
        return "Failed to execute script"


@app.route('/start_jetson', methods=['GET', 'POST'])
def start_jetson():
    command = "ssh smart_breath_analyzer@172.16.70.214 /home/smart_breath_analyzer/.pyenv/shims/python3 Desktop/final_send_data.py"
    try:
        subprocess.run(command, shell=True, check=True)
        if request.method == 'POST':
            print("YESS")
            result2 = "First Test: {}".format(find_data())
            return jsonify({'result2': result2})
        print("Success Script")
        return render_template('Scipt.html')
    except Exception as e:
        return "Failed to execute script"

if __name__ == '__main__':
    app.run()
