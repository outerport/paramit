import sys
import os
import subprocess
import subprocess_tee
import uuid
import tempfile
import hashlib

from typing import Optional

import platformdirs
import tomli
import tomli_w

try:
    import git

    GIT_ENABLED = True
except ImportError:
    # This is needed for when git is not properly installed
    GIT_ENABLED = False

from haipera.constants import YELLOW, RED, RESET

__all__ = [
    "find_package_to_venv_config_file",
    "find_venv_from_package_file",
    "create_venv_and_install_packages",
    "run_code_in_venv",
    "find_package_file",
]


def get_python_path(venv_path) -> str:
    if sys.platform.startswith("win"):
        python_path = os.path.join(venv_path, "Scripts", "python")
    else:
        python_path = os.path.join(venv_path, "bin", "python")
    return python_path


def get_pip_path(venv_path) -> str:
    if sys.platform.startswith("win"):
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
    return pip_path


def hash_package_file(package_file: str) -> str:
    with open(package_file, 'r') as file:
        # Read and split the file into lines
        lines = file.readlines()
    
    # Remove whitespace and empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Sort the lines
    sorted_lines = sorted(lines)
    
    # Join the sorted lines
    content = '\n'.join(sorted_lines)

    # Create a hash of the content
    return hashlib.sha256(content.encode()).hexdigest()


def find_package_to_venv_config_file() -> str:
    """Find the path to the package_to_venv.toml configuration file."""
    user_data_dir = platformdirs.user_data_dir("haipera")
    os.makedirs(user_data_dir, exist_ok=True)
    config_file_path = os.path.join(user_data_dir, "package_to_venv.toml")

    if not os.path.exists(config_file_path):
        with open(config_file_path, "wb") as f:
            tomli_w.dump({}, f)

    return config_file_path


def find_venv_from_package_file(package_file: str) -> Optional[str]:
    config_file_path = find_package_to_venv_config_file()

    if not os.path.exists(config_file_path):
        return None

    with open(config_file_path, "rb") as f:
        config = tomli.load(f)

    hash_key = hash_package_file(package_file)
    print(hash_key)
    if hash_key in config:
        # Check that the venv path is valid
        venv_path = config[hash_key]
        if os.path.exists(venv_path):
            return venv_path
        else:
            del config[hash_key]
            with open(config_file_path, "wb") as f:
                tomli_w.dump(config, f)


def create_venv_and_install_packages(package_file: str) -> str:
    user_cache_dir = platformdirs.user_cache_dir("haipera")
    venv_path = os.path.join(user_cache_dir, str(uuid.uuid4()), ".venv")
    os.makedirs(venv_path, exist_ok=True)
    print(f"Creating virtual environment at {venv_path}")
    venv_result = subprocess.run(["python", "-m", "venv", venv_path], check=True)

    if venv_result.returncode != 0:
        print(
            f"{RED}Error: Failed to create virtual environment at {venv_path}{RESET}"
        )
        sys.exit(1)

    python_path = get_python_path(venv_path)

    pip_result = subprocess.run([python_path, "-m", "ensurepip"], check=True)

    if pip_result.returncode != 0:
        print(
            f"{RED}Error: Failed to install pip in the virtual environment at {venv_path}{RESET}"
        )
        sys.exit(1)

    pip_path = get_pip_path(venv_path)

    if (
        os.path.exists(package_file)
        and os.path.basename(package_file) == "requirements.txt"
    ):
        result = subprocess.run([pip_path, "install", "-r", package_file])
    elif (
        os.path.exists(package_file)
        and os.path.basename(package_file) == "pyproject.toml"
    ):
        result = subprocess.run([pip_path, "install", "-e", package_file], check=True)
    else:
        print(f"{YELLOW}Warning: Invalid package file {package_file}{RESET}")

    if result.returncode != 0:
        print(f"{RED}Error: Failed to install packages from {package_file}{RESET}")
        sys.exit(1)

    print(f"Installed packages from {package_file} in the virtual environment")
    config_file_path = find_package_to_venv_config_file()
    with open(config_file_path, "rb") as f:
        config = tomli.load(f)

    hash_key = hash_package_file(package_file)
    config[hash_key] = venv_path
    with open(config_file_path, "wb") as f:
        tomli_w.dump(config, f)

    return venv_path


def run_code_in_venv(source_code: str, venv_path: str, cwd: str) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
        temp_file.write(source_code)
        temp_file_path = temp_file.name

    python_path = get_python_path(venv_path)

    log_file_path = os.path.join(cwd, "console.log")
    try:
        output = subprocess_tee.run(
            f"{python_path} -u {temp_file_path}",
            cwd=cwd, 
            shell=True,
        )
        
        # Save 
        with open(log_file_path, "w") as f:
            f.write(output.stdout)

    except subprocess.CalledProcessError as e:
        return e.stderr
    finally:
        os.unlink(temp_file_path)


def find_package_file(directory: str) -> Optional[str]:
    """Searches for a requiements.txt file or a pyproject.toml file in the given directory."""
    directory = os.path.abspath(directory)
    for file in os.listdir(directory):
        if file == "requirements.txt":
            return os.path.join(directory, file)
        elif file == "pyproject.toml":
            return os.path.join(directory, file)

    # If no package file is found in the directory, search in the git repository
    if GIT_ENABLED:
        try:
            repo = git.Repo(directory)
            # Root
            repo_root = repo.git.rev_parse("--show-toplevel")
            # Search between the directory and the root of the repository, starting from the directory
            while directory != repo_root:
                for file in os.listdir(directory):
                    if file == "requirements.txt":
                        return os.path.join(directory, file)
                    elif file == "pyproject.toml":
                        return os.path.join(directory, file)
                directory = os.path.dirname(directory)

        except git.InvalidGitRepositoryError:
            pass

    return None
