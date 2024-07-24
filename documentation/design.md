# Pyapp

Pyapp is the Python application management system.

With Pyapp you can build, install, remove, update, and create Python applications.
It will use a toml file that is similar in nature to pyproject.toml.

pyapp is the cli tool that will implement all the features.

pyapp accepts several arguments to indicate which functions need to be executed.


pyapp <command> [optional]

commands:
    init [appname]       initializes a pyapp project optionally give it a folder to initialize, otherwise the current directory is assumed.
                        init will:
                          create the directory <appname> if the <appname> is provided.
                          create pyapp.toml (with defaults)
                          create LICENSE.txt (empty)
                          create README.md (empty)
                          create .gitignore (empty)
                          create dist directory
                          create build directory
                          create tests directory
                          create docs directory
                          create a virtual environment                             
                          create the src/appname directory                          
                          create __init__.py
                          create __about__.py with boilerplate, need to edit
                          create <appname>.py with boilerplate, need to edit


                          in case the appname was not provided, it will assume that the current directory is the appname.


    add <library>       add a dependency in pyapp.toml under [project] dependencies. It will also install the library in the virtual environment.
    remove <library>    remove a dependency in pyapp.toml and uninstall it from the virtual environment.
    
    install <application>   installs the application from the application repository configurred in pyapp.conf, this includes installing a virtual environment and creating a shell script that will execute the application with that virtual enviroment activated.
    uninstall <application> uninstalls the application from the system also removes its virtual environment and all files that were installed.

    config [config variable] sets the config variable in pyapp.conf

    
# Configuration


Configuration for the pyapp application management system is held in the pyapp.conf file which is in the file:

~/.config/pyapp/pyapp.conf

It contains the following settings:

key                   description

env-create-tool       This is the command to create a virtual environment, this is copied to pyapp.toml 
                      when a new project is initialized (pyapp init). (default: python3 -m venv)

env-name              This will be the name of the environment, this is copied to pyapp.toml. (default: env)

env-lib-installer     This is the command to install, update or remove libraries to a (virtual) environment.
                      It is copied to pyapp.toml. (default: python3 -m pip)

dependencies          This is the default list of dependencies, comma separated.
                      By default it is empty.
                      It is copied to pyapp.toml.
                      This does not include the hardcoded dependencies: tomli and tomli_w to read&write toml files.
                      These two libraries will always be installed and should never be put into the dependencies
                      list. 
                      The add/remove functions of pyapp rely on these two libraries to exist in the applications' 
                      virtual environment.

requires-python       The minimal version of python that should be on the system for installing the app. (default: >=3.9)
create-venv           True/False flag indicating that a virtual environment should be created on init. (default: true)
create-gitignore      True/False flag indicating that a .gitignore file should be created by init. (default: true)
create-readme         True/False flag indicating that a README.md file should be created by init. (default: true)
create-license        True/False flag indicating that a LICENSE.txt file should be created by init. (default: true)
create-init           True/False flag indicating that a __init__.py file should be created by init. (default: true)
create-about          True/False flag indicating that a __about__.py file should be created by init. (default: true)
create-typed          True/False flag indicating that a py.typed file should be created by init. (default: true)

repository            This is the URL that pyapp should access for finding the pyapp application server.


# Application configuration file (pyapp.toml)

The pyapp.toml file is the configuration for the application project.
It is a toml file like the known pyproject.toml file, while it does have some similarities, 
it's not completely the same.

The pyapp.toml file has the following content:

[tools]                            tools section name
env-create-tool                    command to create a virtual environment, copied over from pyapp.conf
env-name                           the name of the virtual environment, copied over from pyapp.conf
env-lib-installer                  command to install/uninstall libraries in the virtual environment, copied over from pyapp.conf

[project]                          project section name
name                               name of the application
version                            version of the applicaiton
readme                             filename of the readme file
license                            filename of the license file
description                        an optional description of the application
authors                            the list of authors, list of dict (name=, email=) (identical to pyproject.toml)
requires-python                    the required python version (identical to pyproject.toml)
dependencies                       List of dependancies, it will list any library that was installed with pyapp add.
                                   But in addittion it will also list the dependencies that were installed alongside 
                                   with the library.

                                   NOTE:
                                   The implemented dependancy check is not perfect.

                                   Consider the scenario:
                                   lib a      dependancies: lib x, lib y, lib z
                                   lib b      dependancies: lib u, lib y, lib z
                                   lib c      dependancies: lib a, lib b

                                   The dependancy list in pyapp.toml will look like this:

                                   [
                                      {name="lib a", new_packages=["lib x", "lib y", "lib z"]},
                                      {name="lib b", new_packages=["lib u"]},
                                      {name="lib c", new_packages=[]},
                                   ]

                                   What pyapp does is run a diff on the installed packages each time a new library
                                   is added, the downside is, as you see that it won't record the actual dependencies.
                                   When lib a gets uninstalled lib b and lib c won't work anymore.


[executable]                      executalbe section name
<appname> = "<appname>:run"       will install an executable to run the application appname calling the function run.

[includes]                        includes section name

directories = ["<directory>"]     a list of directories that should be included in the distribution
                                  the entire contents of these directories will be included in the distribution
files = ["<file>"]                a list of files that should be included in the distribution
                                  the files here will be added to the distribution inside the "includes" directory.



# Application repository

The application repository is a web server combined with a REST API server.

The repository will hold the applications that are available for installation.
The repository will have a configuration file that will hold the applications that are available for installation.

The API is used for authentication and to get the list of applications that are available for installation by the pyapp tool.
The authentication is only required for the uploading of new (versions of) applications to the repository.


