**Car Prediction Website**
*Overview*
This project demonstrates the creation of a machine learning web application that predicts car prices. It incorporates DevOps practices such as Infrastructure as Code, Continuous Integration, and Continuous Delivery. The application is built using Flask and deployed through GitLab.

*Features*
Machine Learning Model: Utilizes a sophisticated machine learning model for predicting car prices based on a dataset from Kaggle.

Flask Web Application: A user-friendly web interface for interacting with the prediction model.

SQLite Database: Stores prediction history, enabling users to view past results.

User Authentication: Implements basic login functionality for enhanced security.

REST APIs: Offers RESTful services for performing predictions and accessing prediction history.
DevOps Practices

GitLab SCM: Project managed using GitLab for source control and continuous integration.
SCRUM Board: Agile development process with SCRUM methodology for task management.

Continuous Integration/Continuous Delivery (CI/CD): Automated pipelines for efficient and reliable code integration and deployment.

*Installation*
Prerequisites
- Python 3.x
- Git
- Flask
- SQLite
  
*Setup*
Clone the repository: git clone [repository-url]
Install dependencies: pip install -r requirements.txt
Initialize the database: python init_db.py (Assuming you have a script for DB initialization)
Run the Flask application: python app.py
Usage
After starting the server, navigate to http://localhost:5000 in your web browser to access the application. Log in using the provided credentials, and start making car price predictions.

Testing
Comprehensive unit testing is provided, covering various aspects such as validity, range, consistency, unexpected failure, and expected failure scenarios.

Deployment (Optional)
Deployed to Render [https://vroom-co.onrender.com/]

License
Specify the license under which the project is made available.