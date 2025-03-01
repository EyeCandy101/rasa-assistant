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
print(f" Metamodel generated in {RASA_DATA_DIR}")

# Step 2: Handle the Metamodel (if generated)
tar_files = [f for f in os.listdir(RASA_DATA_DIR) if f.endswith(".tar.gz")]

if tar_files:
    tar_file = os.path.join(RASA_DATA_DIR, tar_files[0])
    print(f"Found model file: {tar_file}")

    # Step 3: Extract the tar.gz file
    with tarfile.open(tar_file, "r:gz") as tar:
        # Get the main directory name from the first file path in the archive
        main_dir_name = tar.getnames()[0].split('/')[0]
        extracted_dir = os.path.join(RASA_DATA_DIR, main_dir_name)
        
        # Remove existing directory if it exists
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
        
        # Extract all files
        tar.extractall(RASA_DATA_DIR)
        print(f"Extracted files to {extracted_dir}")

    # Step 4: Move configuration files to the Rasa root directory
    for file in ["config.yml", "domain.yml"]:
        file_path = os.path.join(extracted_dir, file)
        if os.path.exists(file_path):
            shutil.move(file_path, os.path.join(RASA_DIR, file))
            print(f"Moved {file} to {RASA_DIR}")
    
    # Step 5: Move data files to the Rasa data directory
    for subdir in ["nlu", "stories", "rules"]:
        src_dir = os.path.join(extracted_dir, "data", subdir)
        if os.path.exists(src_dir):
            dst_dir = os.path.join(RASA_DATA_DIR, subdir)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"Moved {subdir} data to {dst_dir}")
    
    # Step 6: Move the model itself to the models directory
    model_files = [f for f in os.listdir(extracted_dir) if f.endswith(".tar.gz")]
    if model_files:
        model_file = os.path.join(extracted_dir, model_files[0])
        shutil.move(model_file, os.path.join(MODEL_DIR, "latest.tar.gz"))
        print(f"Moved model to {os.path.join(MODEL_DIR, 'latest.tar.gz')}")
    
    # Cleanup extracted directory
    shutil.rmtree(extracted_dir)
    print("Cleanup complete")

    print("Model is ready in Rasa!")
else:
    print("No .tar.gz model file found in the output directory")
