import subprocess

def check_python3_venv() -> bool:
    """Check if the Python3 venv module is installed."""
    output = subprocess.check_output(
        "dpkg -l | grep python3-venv", shell=True, executable="/bin/bash"
    ).decode("utf-8")
    print(output)
    return False

check_python3_venv();
