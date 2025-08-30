#!/usr/bin/env python3
import os
import shutil


def delete_pycache(start_path='.'):
    """
    Recursively deletes all __pycache__ folders and .pyc files starting from `start_path`.
    """
    removed_dirs = 0
    removed_files = 0

    for dirpath, dirnames, filenames in os.walk(start_path):
        # Remove __pycache__ directories
        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"🗑️  Removed directory: {pycache_path}")
                removed_dirs += 1
            except Exception as e:
                print(f"❌ Failed to remove {pycache_path}: {e}")

        # Remove .pyc files
        for filename in filenames:
            if filename.endswith('.pyc'):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    print(f"🧽 Removed file: {file_path}")
                    removed_files += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")

    print(f"\n✅ Cleanup complete: {removed_dirs} dirs, {removed_files} files removed.")


if __name__ == '__main__':
    delete_pycache()
