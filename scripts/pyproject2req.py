import toml

def convert_pyproject_to_requirements(pyproject_file, requirements_file):
    try:
        with open(pyproject_file, "r") as file:
            pyproject_data = toml.load(file)

        dependencies = pyproject_data.get("project", {}).get("dependencies", [])
        optional_dependencies = pyproject_data.get("project", {}).get("optional-dependencies", {})

        with open(requirements_file, "w") as file:
            for dependency in dependencies:
                file.write(f"{dependency}\n")

            for option, option_dependencies in optional_dependencies.items():
                file.write(f"\n# Optional Dependencies - {option}\n")
                for dependency in option_dependencies:
                    file.write(f"{dependency}\n")

        print(f"Successfully converted {pyproject_file} to {requirements_file}.")

    except FileNotFoundError:
        print(f"File {pyproject_file} not found.")
    except toml.TomlDecodeError:
        print(f"Error decoding {pyproject_file}. Please ensure it is a valid TOML file.")

# Usage example
pyproject_file = "pyproject.toml"
requirements_file = "requirements.txt"
convert_pyproject_to_requirements(pyproject_file, requirements_file)
