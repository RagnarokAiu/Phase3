import zipfile
import os

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Create relative path
                relative_path = os.path.relpath(file_path, os.path.dirname(folder_path))
                # Enforce forward slashes for Linux compatibility
                formatted_path = relative_path.replace(os.path.sep, '/')
                zipf.write(file_path, formatted_path)
    print(f"Created {output_path}")

if __name__ == "__main__":
    zip_folder("phase2-services", "services.zip")
