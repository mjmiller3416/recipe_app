import os

ROOT_DIR = "app"  # Change this if needed

def create_init_files(root_dir):
    """Recursively creates __init__.py in all subdirectories."""
    for dirpath, _, _ in os.walk(root_dir):
        init_file = os.path.join(dirpath, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# This package is part of the Recipe App\n")
            print(f"Created: {init_file}")

# Run the script
if __name__ == "__main__":
    create_init_files(ROOT_DIR)
