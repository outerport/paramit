import os
import sys
import ast
import datetime
from typing import List, Any, Dict
from pydantic import BaseModel
import tomli
import tomli_w
import uuid
from haipera.venv import (
    find_venv_from_package_file,
    create_venv_and_install_packages,
    run_code_in_venv,
    find_package_file,
)


class HaiperaVariable(BaseModel):
    name: str
    value: Any
    type: str
    file_name: str
    line_number: int

    def __str__(self):
        return f"{self.name} = {self.value} ({self.type}) [{self.file_name}:{self.line_number}]"


class HaiperaMetadata(BaseModel):
    version: str
    created_on: str
    script_path: str
    package_path: str


class HaiperaParameter(BaseModel):
    name: str
    type: str
    values: List[Any]


def find_variables(tree: ast.AST, path: str) -> List[HaiperaVariable]:
    """Find all variables, their values, and types in the given AST tree."""
    variables = []

    class VariableVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_context = []

        def visit_Assign(self, node: ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(
                    node.value, ast.Constant
                ):
                    self.add_variable(target.id, node.value, node.lineno)
                elif (
                    isinstance(target, ast.Attribute)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                ):
                    self.add_variable(target.attr, node.value, node.lineno)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Name):
                self.current_context.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.current_context.append(node.func.attr)

            # Disable for now
            # print(self.current_context)
            """
            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Constant):
                    self.add_variable(keyword.arg, keyword.value, node.lineno)
            """

            self.generic_visit(node)

            if self.current_context:
                self.current_context.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            if node.name == "__init__":
                if node.args.defaults:
                    default_args = node.args.args[-len(node.args.defaults) :]
                    for arg, default in zip(default_args, node.args.defaults):
                        if isinstance(default, ast.Constant):
                            self.add_variable(arg.arg, default, node.lineno)
            self.generic_visit(node)

        def visit_ClassDef(self, node: ast.ClassDef):
            self.current_context.append(node.name)
            for base in node.bases:
                if isinstance(base, ast.Call):
                    self.visit_Call(base)
            self.generic_visit(node)
            self.current_context.pop()

        def add_variable(self, name: str, value: ast.Constant, lineno: int):
            full_name = ".".join(self.current_context + [name]) if name else None
            variables.append(
                HaiperaVariable(
                    name=full_name,
                    value=value.value,
                    type=type(value.value).__name__,
                    file_name=os.path.basename(path),
                    line_number=lineno,
                )
            )

    visitor = VariableVisitor()
    visitor.visit(tree)
    # TODO: Create another visitor that looks at function calls, and if it finds an
    # identical variable as the FunctionDef variable, change the value of the variable
    return variables


def expand_paths_in_global_variables(
    global_vars: List[HaiperaVariable], script_path: str
) -> List[HaiperaVariable]:
    """Expand the path in the given global variables using the script path."""
    expanded_vars = []
    for var in global_vars:
        if isinstance(var.value, str):
            expanded_path = os.path.abspath(
                os.path.join(os.path.dirname(script_path), var.value)
            )
            if os.path.exists(expanded_path):
                expanded_vars.append(
                    HaiperaVariable(
                        name=var.name,
                        value=expanded_path,
                        type=var.type,
                        file_name=var.file_name,
                        line_number=var.line_number,
                    )
                )
            else:
                expanded_vars.append(var)
        else:
            expanded_vars.append(var)
    return expanded_vars


def generate_config_file(
    global_vars: List[HaiperaVariable], script_path: str, config_path: str
) -> None:
    """Generate a TOML configuration file with the given global variables."""
    config = {"global": {}, "meta": {}}
    for var in global_vars:
        parts = var.name.split(".")
        if len(parts) == 1:
            config["global"][parts[0]] = var.value
        else:
            current_dict = config["global"]
            for part in parts[:-1]:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]
            current_dict[parts[-1]] = var.value

    package_file = find_package_file(os.path.dirname(script_path))

    if not package_file:
        print(
            "\033[93mWarning: No package file found, set the package_path manually in the config file\033[0m"
        )

    metadata = HaiperaMetadata(
        version="0.1.0",
        created_on=str(datetime.datetime.now()),
        script_path=os.path.abspath(script_path),
        package_path=package_file if package_file else "",
    )

    config["meta"] = metadata.model_dump()

    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    if not package_file:
        sys.exit(0)


def load_config_file(path: str) -> dict:
    """Load a TOML configuration file from the given path
    and return it as a dictionary."""

    with open(path, "rb") as f:
        return tomli.load(f)


def set_global_variables_from_config(tree: ast.AST, config: dict) -> None:
    """Set global variables in the given AST tree using the values from the config dictionary."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if name in config["global"]:
                        value = config["global"][name]
                        node.value = ast.Constant(value=value)


def parse_args(args: List[str]) -> Dict[str, Any]:
    """Parse the given list of arguments into a dictionary."""
    args_dict = {}
    for arg_index, arg in enumerate(args):
        if arg.startswith("--"):
            if "=" in arg:
                key, value = arg.split("=")
            else:
                key = arg
                if arg_index + 1 >= len(args):
                    print(f"\033[91mError: Argument {arg} is missing a value\033[0m")
                    sys.exit(1)

                value = ""
                while arg_index + 1 < len(args) and not args[arg_index + 1].startswith(
                    "--"
                ):
                    if value:
                        value += ","
                    value += args[arg_index + 1]
                    arg_index += 1

            key = key[2:].replace("-", "_")
            args_dict[key] = value
    return args_dict


def expand_args_dict(args_dict: Dict[str, str]) -> Dict[str, HaiperaParameter]:
    """Parse the value in the args according to the special haipera syntax.

    The syntax is as follows:
        "123,126,128" -> [123, 126, 128]
        "blue, red" -> ["blue", "red"]
        "blue red" -> ["blue", "red"]
    """

    hyperparameters = {}
    for arg, value in args_dict.items():
        if "," in value:
            values = value.split(",")
        else:
            values = [value]

        if not values:
            print(f"\033[91mError: Argument {arg} must have at least one value\033[0m")
            sys.exit(1)

        value_type = None
        if all(v.isdigit() for v in values):
            value_type = int
            values = [value_type(v) for v in values]
        elif all(v.replace(".", "").replace("e", "").isdigit() for v in values):
            value_type = float
            values = [value_type(v) for v in values]
        elif all(v.lower() in ["true", "false"] for v in values):
            value_type = bool

            def str_to_bool(value):
                if value.lower() == "true":
                    return True
                elif value.lower() == "false":
                    return False
                else:
                    print(f"\033[91mError: Bool argument must be True or False\033[0m")
                    sys.exit(1)

            values = [str_to_bool(v) for v in values]

        else:
            value_type = str
            values = [value_type(v) for v in values]

        hyperparameters[arg] = HaiperaParameter(
            name=arg, type=type(values[0]).__name__, values=values
        )

    return hyperparameters


def generate_configs_from_hyperparameters(
    base_config: Dict[str, Any], hyperparameters: Dict[str, HaiperaParameter]
) -> List[Dict[str, Any]]:
    """Generate a list of configurations from the base config and hyperparameters."""

    hyperparameters_range: List[HaiperaParameter] = []
    hyperparameters_single: List[HaiperaParameter] = []
    for hyperparameter in hyperparameters:
        if len(hyperparameters[hyperparameter].values) > 1:
            hyperparameters_range.append(hyperparameters[hyperparameter])
        else:
            hyperparameters_single.append(hyperparameters[hyperparameter])

    for hyperparameter in hyperparameters_single:
        if hyperparameter.name in base_config["global"]:
            try:
                base_config["global"][hyperparameter.name] = type(
                    base_config["global"][hyperparameter.name]
                )(hyperparameter.values[0])
            except ValueError:
                print(
                    f"\033[91mError: Argument {hyperparameter.name} must be of type {type(base_config['global'][hyperparameter.name])}\033[0m"
                )
                sys.exit(1)
        else:
            print(
                f"\033[91mError: Argument {hyperparameter.name} not found in the code or config\033[0m"
            )
            sys.exit(1)

    if not hyperparameters_range:
        return [base_config]

    # Generate all possible combinations of hyperparameters
    hyperparameters_combinations = []
    for i in range(len(hyperparameters_range)):
        hyperparameter = hyperparameters_range[i]
        if not hyperparameters_combinations:
            for value in hyperparameter.values:
                hyperparameters_combinations.append({hyperparameter.name: value})
        else:
            new_combinations = []
            for combination in hyperparameters_combinations:
                for value in hyperparameter.values:
                    new_combination = combination.copy()
                    new_combination[hyperparameter.name] = value
                    new_combinations.append(new_combination)
            hyperparameters_combinations = new_combinations

    configs: List[Dict[str, Any]] = []

    for combination in hyperparameters_combinations:
        config = base_config.copy()
        for key, value in combination.items():
            if key in config["global"]:
                try:
                    config["global"][key] = type(config["global"][key])(value)
                except ValueError:
                    print(
                        f"\033[91mError: Argument {key} must be of type {type(config['global'][key])}\033[0m"
                    )
                    sys.exit(1)
            else:
                print(
                    f"\033[91mError: Argument {key} not found in the code or config\033[0m"
                )
                sys.exit(1)

        configs.append(config)

    return configs


def main():
    if len(sys.argv) < 3 or (sys.argv[1] != "run" and sys.argv[1] != "cloud"):
        print(
            "\033[93mUsage: haipera [run | cloud] <path_to_python_or_toml_file>\033[0m"
        )
        sys.exit(1)

    if sys.argv[1] == "cloud":
        print(
            "\033[93mCloud runs are not available yet. Please sign up on the waitlist for updates at https://www.haipera.com\033[0m"
        )
        sys.exit(1)

    path = sys.argv[2]
    if not os.path.exists(path):
        print(f"\033[91mError: File {path} does not exist\033[0m")
        sys.exit(1)

    cli_args = parse_args(sys.argv[3:])
    hyperparameters = expand_args_dict(cli_args)

    if not path.endswith(".py") and not path.endswith(".toml"):
        print(f"\033[91mError: File {path} is not a Python or TOML file\033[0m")
        sys.exit(1)

    if path.endswith(".toml"):
        config = load_config_file(path)

        try:
            HaiperaMetadata(**config["meta"])
        except Exception:
            print(
                "\033[91mError: The config file is not a valid haipera config file\033[0m"
            )

        if not os.path.exists(config["meta"]["script_path"]):
            print(
                f"\033[91mError: Python file {config['meta']['script_path']} does not exist\033[0m"
            )
            sys.exit(1)

        with open(config["meta"]["script_path"], "r") as f:
            code = f.read()

    elif path.endswith(".py"):
        with open(path, "r") as f:
            code = f.read()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        e.filename = path
        print(f"\033[91mSyntaxError: {e}\033[0m")
        sys.exit(1)

    if not os.path.exists(path.replace(".py", ".toml")):
        global_vars = find_variables(tree, path)
        global_vars = expand_paths_in_global_variables(global_vars, path)
        config_path = path.replace(".py", ".toml")
        script_path = path.replace(".toml", ".py")
        generate_config_file(global_vars, script_path, config_path)
        print(f"Configuration file generated at {config_path}")
    elif not path.endswith(".toml"):
        print(
            f"\033[93mWarning: Configuration file {path.replace('.py', '.toml')} already exists\033[0m"
        )
        overwrite = input("Do you want to overwrite it? (y/n): ")
        if overwrite.lower() == "y":
            global_vars = find_variables(tree, path)
            global_vars = expand_paths_in_global_variables(global_vars, path)
            config_path = path.replace(".py", ".toml")
            script_path = path.replace(".toml", ".py")
            generate_config_file(global_vars, script_path, config_path)
            print(f"Configuration file generated at {config_path}")

    config = load_config_file(path.replace(".py", ".toml"))

    package_file = config["meta"]["package_path"]
    venv_path = find_venv_from_package_file(package_file)
    if not venv_path:
        venv_path = create_venv_and_install_packages(package_file)

    experiment_configs = generate_configs_from_hyperparameters(config, hyperparameters)

    if len(experiment_configs) > 100:
        print(f"\033[93mWarning: Running {len(experiment_configs)} experiments\033[0m")
        confirm = input("Do you want to continue? (y/n): ")
        if confirm.lower() != "y":
            sys.exit(0)
    elif len(experiment_configs) == 0:
        print("\033[93mWarning: No experiments to run\033[0m")
        sys.exit(0)
    elif len(experiment_configs) == 1:
        pass
    else:
        print(f"\033[93mRunning {len(experiment_configs)} experiments\033[0m")

    for experiment_config in experiment_configs:
        experiment_id = (
            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            + "-"
            + str(uuid.uuid4())[0:8]
        )
        experiment_dir = os.path.join("reports", experiment_id)
        os.makedirs(experiment_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(path))[0]

        # Save the config file in the experiment directory
        with open(os.path.join(experiment_dir, base_name + ".toml"), "wb") as f:
            tomli_w.dump(experiment_config, f)

        set_global_variables_from_config(tree, experiment_config)

        # Also save the script file
        source_code = ast.unparse(tree)
        with open(os.path.join(experiment_dir, base_name + ".py"), "w") as f:
            f.write(source_code)

        # Also save the package file
        with open(
            os.path.join(experiment_dir, os.path.basename(package_file)), "wb"
        ) as f:
            with open(package_file, "rb") as p:
                f.write(p.read())

        run_code_in_venv(source_code, venv_path, experiment_dir)
