# Research Planner Web Application.
The Research Planner web application allows researchers to allocate data processing tasks to themselves and upload the resulting reports to a server.  Research administrators can then view the reports and approve them or not.  

A research study may have one or more datasets that require processing.  Typically a dataset will have several data processing tasks applied to it.  Each task must be preformed once or repeated several times.  When a task is repeated several times, each repetition of that task must be done by a different researcher. Consequently, a researcher is prevented from selecting the same dataset-task combination more than once. 

The combination of a task applied to a dataset is called a **job**.

The Research Planner web application uses a Postgres database to store user and **job** data.  This database is populated by uploading an Excel spreadsheet with a specific format to the web application. This Excel spreadsheet defines the dataset names and tasks.  An example of this spreadsheet called **Test_Data_Do_Not_Delete.xlsx** is contained in the root folder of the web application.  **Do not edit, remove, delete or rename this file** as it is used by the automated tests developed to test this application.  It is recommended that you make a copy of this file, give it a meaningful name and edit its contents to fit the requirements of your research project. 

This web application was written in Python 3.9 and uses the Django framework. 
When a request is made to a Django web application, several steps are involved in processing the request and generating a response. Here is an overview of the typical request/response cycle in the context of this web application:

1. Web Server:
   - The request is initially received by a web server, such as Nginx, which is responsible for handling incoming HTTP requests.

2. URL Routing:
   - The web server forwards the request to the research planner web application, which matches the requested URL to a specific view function in the file **views.py** using the URL-view function mappings in the file **urls.py**.

3. View Function:
   - Once the URL is matched, Django calls the associated view function.
   - The view function processes the request and generates a response.
   - In this application, view functions typically save data to or fetch it from a database and render a template.

4. Middleware:
   - Django's middleware components are invoked before and after the view is called.
   - Middleware can intercept the request or response, perform additional processing, modify headers, or authenticate users.

5. Database Interaction:
   - If the view requires data from a database, it can use Django's ORM (Object-Relational Mapping) to interact with the database.
   - The ORM provides a high-level API for querying and manipulating data, abstracting away the specific database engine being used.

6. Template Rendering:
   - If the view needs to render a template, it utilizes Django's template engine.
   - The template engine combines the view's data with the specified template, generating the final HTML content to be sent in the response.
   - Templates are HTML files in which executable commands are enclosed in **{% %}** and context variables are enclosed in **{}**.  When a template is rendered into a web page, the context variables are replaced by a value or a string. 

7. Response Generation:
   - The view returns an HTTP response object, which contains the response data, status code, headers, and other relevant information.
   - The response can be a simple HTML page, JSON data, file download, or a redirect to another URL.

8. Middleware (post-processing):
   - After the view returns a response, any remaining middleware is invoked to perform post-processing tasks.
   - This can include modifying the response, adding additional headers, or logging.

9. Web Server:
   - Finally, the web server receives the response generated by Django and sends it back to the client that made the initial request.


# Setting up a development environment
As this web application uses a Postgres database, the first task is the installation of the Postgres database management system and the creation of the database and a database user.

## Installing the Postgres database
1. Visit the official PostgreSQL downloads page at **https://www.postgresql.org/download/** and select the appropriate version for your operating system.

2. Download the installer for your operating system and run the installer.

3. Follow the installation wizard instructions, accepting the default settings unless you have specific requirements.

4. During the installation process, you will be prompted to set a password for the default database superuser (usually called "postgres"). Choose a strong password and remember it for future use.

5. Complete the installation process by following the remaining steps in the wizard.

Verify the installation by opening a terminal or command prompt and running the following command to access the PostgreSQL command-line interface:

      `psql -U postgres`

This command connects to the default PostgreSQL database as the "postgres" superuser.

If the command is successful, you will see the PostgreSQL command prompt (postgres=#), indicating that you have successfully installed PostgreSQL.

At this point, you could enter the following commands to create the database and a user.  Use the given database name, username and password in order to match the database definition in the settings.py file in the web application source code,
1.  Create the database :
      `postgres=# CREATE DATABASE plannerdb;`
    
**Note: Every Postgres statement must end with a semi-colon, so make sure that your command ends with one if you are experiencing issues.**

3.  Create a database user for our project:
      `postgres=# CREATE USER planneruser WITH PASSWORD 'planner1234';`

Alternatively, you could use the GUI tool **pgAdmin4** to create the database and database user.

To install pgAdmin4, you can follow these general steps:

1. Visit the official pgAdmin4 website at https://www.pgadmin.org/ and navigate to the "Download" section.

2. In the download section, select the appropriate version of pgAdmin4 for your operating system.

3. Click on the download link for your chosen version to start the download.

4. Once the download is complete, run the installer for pgAdmin4.

5. Follow the installation wizard instructions, accepting the default settings unless you have specific requirements.

6. During the installation process, you may be prompted to choose the installation directory and specify additional configuration options. Make any necessary selections based on your preferences and requirements.

7. Complete the installation process by following the remaining steps in the wizard.

8. Launch pgAdmin4 by locating its executable or by searching for it in the Start menu.

When you open pgAdmin4 for the first time, you will be prompted to set up the initial configuration. Provide the necessary information, such as the server hostname, port, and login credentials, to connect to your PostgreSQL database.

To create a database called "plannerdb" and user in pgAdmin4 for a PostgreSQL server, follow these steps:
1. Launch pgAdmin4 and connect to your PostgreSQL server.

2. Expand the server group in the Object browser on the left-hand side.

3. Right-click on the "Databases" option and select "Create" from the context menu. This will open the "Create - Database" dialog.

4. In the "General" tab, provide the name "**plannerdb**" in the "Database" field.

5. Click the "Save" button to create the database.

To create a user, follow these steps:
1. Expand the server group in the Object browser on the left-hand side.
2. Expand the server to which you want to create the user. This will be the server hosting the above database.
3. Right-click on the "Login/Group Roles" option and select "Create" from the context menu. This will open the "Create - Login/Group Role" dialog.
4. In the "General" tab, provide a name for the user in the "Name" field; i.e., **planneruser**.
5. Switch to the "Definition" tab.
   Enter the password, **planner1234**,  for the user in the "Password" field and confirm it in the "Password (again)" field. 
6. In the "Privileges" tab, assign log on and superuser privileges to the user.
7. Once you have filled in the required information, click the "Save" button to create the user.

## Installing the source code
1. Download the source code from github to your computer.
2. Open a command prompt in the root of the Django web application where the file **manage.py** is located and
3. to build the tables in the plannerdb database, type the following command,
   
       `python manage.py migrate`

4. and to create a superuser, type the following command,
   
      `python manage.py createsuperuser`

5. You will be prompted to enter a username for the superuser. Type the desired username and press Enter.

6. Next, you will be prompted to enter an email address for the superuser. Provide the email address and press Enter.

7. Finally, you will be prompted to enter a password for the superuser. Type a secure password and press Enter. Note that the password will not be displayed as you type for security reasons.

If the username, email, and password are valid, the superuser will be created, and you will see a success message.

Once the superuser is created, you can use the above credentials to log in to the Django admin interface and access the administrative features of the web application.
         








