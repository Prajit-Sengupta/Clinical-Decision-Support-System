# Clinical-Decision-Support-System
This Flask web application is designed for a medical platform, specifically targeting tuberculosis (TB) diagnosis and patient management. Key functionalities include user registration and login, OTP-based authentication, patient management, and tuberculosis test analysis.

1. User Authentication: Users can register and log in to the system. The registration process includes OTP verification sent via email, enhancing security. Passwords are securely hashed before storing in the MySQL database.
2. Patient Management: The application allows for adding new patient records, viewing existing patient data, and managing patient symptoms. This feature is crucial for keeping track of patient information and their medical history.
3. PDF Processing and Test Analysis: The application enables uploading and processing of PDF files, specifically for TB test results. It extracts text from these PDFs and uses pattern matching to determine if the TB status is positive or negative.
4. Integration with Google Sheets API: The app integrates with the Google Sheets API, allowing it to retrieve data from spreadsheets for further analysis or reporting.
5. Email Services: Utilizing Flask-Mail, the app can send emails for OTP verification and welcome messages to new users, enhancing the user experience.
6. Image Processing for Diagnosis: The app supports uploading medical images, which are then processed using a TensorFlow model to assist in TB diagnosis.
7. Remote Script Execution: There's a feature to execute Python scripts remotely on a Jetson device, indicating potential for IoT-based applications in the medical field.

This application serves as an end-to-end solution for healthcare professionals managing tuberculosis, offering a range of tools from patient data management to diagnostic support, all within a secure and user-friendly web environment.
