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