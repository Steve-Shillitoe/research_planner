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
   - 

7. Response Generation:
   - The view returns an HTTP response object, which contains the response data, status code, headers, and other relevant information.
   - The response can be a simple HTML page, JSON data, file download, or a redirect to another URL.

8. Middleware (post-processing):
   - After the view returns a response, any remaining middleware is invoked to perform post-processing tasks.
   - This can include modifying the response, adding additional headers, or logging.

9. Web Server:
   - Finally, the web server receives the response generated by Django and sends it back to the client that made the initial request.

It's important to note that Django provides a flexible framework, and the exact flow of request processing can be customized and extended using middleware, decorators, and other features based on the specific requirements of the application.

# Installation

**Git** is required to download this repository, unless you choose to download the `.zip` file. In order for Weasel to run successfully, it is required to have **Python (>=3.7)** installed.

Download URLs:

[Git](https://git-scm.com/downloads)

[Python](https://www.python.org/downloads/)

If the images you wish to work with are Enhanced/Multiframe DICOM, then it is required to have **Java JDK** installed so that `dcm4che` can work correctly. If you're using an old OS, it is recommended that you scroll down when navigating the link below and choose an older version of **Java JDK** to install.

[Java JDK](https://www.oracle.com/java/technologies/downloads/)

There are 2 options downloading and installing Weasel requirements:

#### Option 1
Download and install everything in one go by opening a Terminal (MacOS and Linux) or a CMD (Windows) and type in the following command:

`pip install -e git+https://github.com/QIB-Sheffield/Weasel#egg=Weasel --src <download_path>`

After the installation is finished, it's recommended that you go to the directory where Weasel was installed

`cd <download_path>/weasel`

and run the command

`python setup.py clean` 

to clean the installation files that are not needed anymore.

#### Option 2
First, download the repository via `git clone` or by downloading the `.zip` file and extracting its contents.
Then open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and run the command 

`pip install -e .` 

to install all Weasel dependencies. Finally, run the command

`python setup.py clean` 

to clean the installation files that are not needed anymore.

#### For users that are more familiar with Python (Developers)
Running `pip install -e .` will read the `setup.py` file and install the required Python packages to run Weasel successfully. If there are any other Python packages you wish to be installed with Weasel, you can edit the `setup.py` file and add packages to the variable `extra_requirements`.

The core Python modules used in Weasel are in requirements.txt so alternatively you may choose to run `pip install -r requirements.txt` and then any other Python packages of your choice can be installed separately in your machine or in your virtual environment.

# Start Weasel Graphical User Interface
Open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and start Weasel by running the command

`python Weasel.py`

If you're a developer, you may start Weasel by opening an IDE (Sublime Text, VS Code, Visual Studio, etc.) and run the Weasel.py script.

# Start Weasel Command-Line Mode
Open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and start Weasel by running the command

`python Weasel.py -c -d "path/to/xml/dicom.xml" -s "path/to/analyis/script.py`

This alternative of Weasel is recommended if you're processing a large number of DICOM files at the same time or if you're running a time-consuming script.

# Generate the Executable

There is a Github Action Workflow in place that automatically builds the Weasel executable for Windows, MacOS and Linux and uploads the output files to a Monthly Release every Friday at midday.

If you wish to create your own bundle, you can compile the Python project into an executable of the operative system you're using by using the `pyinstaller` package.

First, you have to navigate to your Weasel folder

`cd <Weasel_folder_path>`

and run the following python command:

`python create_weasel_executable.py`

You may use your IDE instead of the terminal during this process. The generated executable can be found in the `Weasel` folder.

**For MacOS:** If the command above doesn't work, you might need to run `python3` instead and/or use `sudo` before the command. Eg. `sudo python3 create_weasel_executable.py`.

Any extra files you wish to add to your bundle, you can do so by writing the files/folders path in the `--collect-datas` and `--add-data` flags in the `create_weasel_executable.py` file.

## Other Info

Weasel runs the command `emf2sf` of [dcm4che](https://www.dcm4che.org/) on Enhanced/Multiframe DICOM. Elastix for Python can be used via ITK-Elastix.
