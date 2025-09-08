import os
import subprocess


# Define paths
ROOT_DIR = "dev_sandbox/qt"  # The root directory to search for .ui files
RESOURCE_FILE = "resources/icons.qrc"  # Path to .qrc file
OUTPUT_RESOURCE_FILE = "resources/icons_rc.py"  # Output .py file for icons

def find_ui_files(root_dir):
    """
    Recursively finds all .ui files in the given root directory.
    
    Args:
        root_dir (str): The directory to start the search.
    
    Returns:
        list: A list of paths to all .ui files found.
    """
    ui_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".ui"):
                ui_files.append(os.path.join(dirpath, file))
    return ui_files

def convert_ui_to_py(ui_file):
    """
    Converts a .ui file to a .py file using pyside6-uic.
    
    Args:
        ui_file (str): Path to the .ui file.
    """
    dir_name = os.path.dirname(ui_file)
    base_name = os.path.splitext(os.path.basename(ui_file))[0]
    output_file = os.path.join(dir_name, f"ui_{base_name}.py")

    print(f"Converting {ui_file} → {output_file}")

    try:
        result = subprocess.run(
            ["pyside6-uic", ui_file, "-o", output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # Ensures correct execution on Windows
        )

        if result.returncode == 0:
            print(f"SUCCESS: {ui_file} → {output_file}")
            fix_imports(output_file)
        else:
            print(f"ERROR: Failed to convert {ui_file}.\n{result.stderr}")

    except Exception as e:
        print(f"Unexpected error during UI conversion: {e}")

def fix_imports(file_path):
    """
    Replaces 'import icons_rc' with 'import resources.icons_rc' in the converted .py file.
    
    Args:
        file_path (str): Path to the converted .py file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace("import icons_rc", "import resources.icons_rc")

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"FIXED IMPORTS: {file_path}")

    except Exception as e:
        print(f"Error fixing imports in {file_path}: {e}")

def delete_existing_icons_rc():
    """Deletes the existing icons_rc.py file to prevent caching issues."""
    if os.path.exists(OUTPUT_RESOURCE_FILE):
        os.remove(OUTPUT_RESOURCE_FILE)
        print(f"Deleted existing: {OUTPUT_RESOURCE_FILE}")

def convert_qrc_to_py():
    """Converts the .qrc file to a Python resource file using pyside6-rcc."""
    if not os.path.exists(RESOURCE_FILE):
        print(f"Skipping QRC conversion: {RESOURCE_FILE} does not exist.")
        return

    delete_existing_icons_rc()

    try:
        subprocess.run(["pyside6-rcc", RESOURCE_FILE, "-o", OUTPUT_RESOURCE_FILE], check=True)
        print(f"Successfully converted {RESOURCE_FILE} to {OUTPUT_RESOURCE_FILE}")
    except subprocess.CalledProcessError as e:
        print(f"Error during QRC conversion: {e}")

if __name__ == "__main__":
    # Find and convert all .ui files
    ui_files = find_ui_files(ROOT_DIR)
    for ui_file in ui_files:
        convert_ui_to_py(ui_file)

    # Convert the resource file
    convert_qrc_to_py()
