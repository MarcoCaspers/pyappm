# Pyappm Changelog

before:
- Added versioning functionality
- Added project type functionality

2024-08-17:
- Started using changelog
- Added create_changelog to config.
- Added changelog code to create CHANGELOG.md in pyappm_app_init.py, function: init_pyapp().
- Added pyappm_repository.py to handle repository functionality.
- PyAPPMRepository class representing a repository with a name and a url.
- PyAPPMRepositoryManager class with functionality to manage reposotories and repository functions.

## [1.0.7] - 2024-09-01

- Added loading/saving repository list functionality to PyAPPMRepositoryManager.
- Added documentation for the repository file format.
- Updated the installer to add ~/.local/bin to PATH if it isn't already there. Updates .bashrc.

## [1.0.8] - 2024-09-01

- Bugfix, removed repository from PyAPPMConfiguration because it's fully handled by PyAPPMRepositoryManager.
- Bugfix, fixed path for repository file to expand user.
- Bugfix, PyAPPMRepositoryManager, init now correctly loads repositories from file without complaining about repositories already existing.
- Removed repositories as a parameter in init of PyAPPMRepositoryManager.
- Added dependency check to app init, it now checks for pip3 and venv, if not it tells the user to install them and exits with error 404.
- Bugfix for creating CHANGELOG.md and .gitignore, they now are created in the correct directory.
- Added a check for the repository file in PyAPPMRepositoryManager, if it doesn't exist it creates it with the default repository list.
- Assume people have venv installed.

TODO:
Fix the bug in the installer where it doesn't properly detect if zip is installed.
Fix the bug in the app installer where it adds the repository?
Fix the bug in the app installer where it fails after unzipping the app file.

## [1.0.9] - 2024-09-03

- Bugfix installer.py, fixed bug where it did not check for zip to be installed.
- Added python3 and pip to the list of dependencies to check for.
- Added a check for venv in the installer.
- fixed bug in installer where it didn't install the app correctly after unzipping the app file. (cause: wrong path for pyapp.toml)
- fixed bug where "added repository" message was shown when loading the repository file.
- fixed bug where pyappm.toml was left dangling in /tmp/pyappm after installation.
- Updated makefile to add CHANGELOG.md to the list of files to be zipped in the distribution package.
  
## [1.1.0] - 2024-09-11

- Moved all the repository client functionality into pyappm_repository_client.py.
- PyAPPMRepositoryClient class to handle repository api connection functionality.