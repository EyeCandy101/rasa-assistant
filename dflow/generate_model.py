import os
import tarfile
import shutil
import subprocess

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Root directory (parent of dflow)
DFLOW_DIR = os.path.join(BASE_DIR, "dflow")  # dFlow directory
RASA_DATA_DIR = os.path.join(BASE_DIR, "rasa", "data")  # Target output path
RASA_DIR = os.path.join(BASE_DIR, "rasa")  # Rasa directory
MODEL_DIR = os.path.join(RASA_DIR, "models")  # Where models should go

# Ensure dFlow is installed
try:
    import dflow
except ImportError:
    print(" dFlow is not installed. Installing now...")
    subprocess.run(["pip", "install", "git+https://github.com/robotics-4-all/dFlow.git"], check=True)

# Step 1: Generate the model using dFlow (directly into rasa/data/)
print(" Generating Rasa model from dFlow DSL...")
os.makedirs(RASA_DATA_DIR, exist_ok=True)  # Ensure target directory exists

generate_command = [
    "textx", "generate",
    os.path.join(DFLOW_DIR, "metamodel.dflow"),
    "--target", "rasa",
    "-o", RASA_DATA_DIR  # Directly output to rasa/data
]

subprocess.run(generate_command, check=True)
print(f" Model training files generated in {RASA_DATA_DIR}")

# Step 2: Move config & domain files to `rasa/`
for file in ["config.yml", "domain.yml"]:
    file_path = os.path.join(RASA_DATA_DIR, file)
    if os.path.exists(file_path):
        shutil.move(file_path, os.path.join(RASA_DIR, file))
        print(f" Moved {file} to rasa/")

# Step 3: Handle the Rasa model (if generated)
tar_files = [f for f in os.listdir(RASA_DATA_DIR) if f.endswith(".tar.gz")]

if tar_files:
    tar_file = os.path.join(RASA_DATA_DIR, tar_files[0])
    print(f" Found model file: {tar_file}")

    with tarfile.open(tar_file, "r:gz") as tar:
        extracted_dir = os.path.join(RASA_DATA_DIR, tar.getnames()[0].split('/')[0])

        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)

        tar.extractall(RASA_DATA_DIR)

    # Move extracted model files
    os.makedirs(MODEL_DIR, exist_ok=True)

    for file in os.listdir(extracted_dir):
        shutil.move(os.path.join(extracted_dir, file), os.path.join(MODEL_DIR, file))

    # Cleanup
    os.remove(tar_file)
    shutil.rmtree(extracted_dir)
    print(" Cleanup complete.")

print(" Model is ready in Rasa! ")
