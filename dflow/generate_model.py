import os
import tarfile
import shutil
import subprocess

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Root directory
DFLOW_DIR = os.path.join(BASE_DIR, "dflow")  # dFlow directory
DFLOW_MODELS_DIR = os.path.join(DFLOW_DIR, "models")  # Where dFlow generated models go
RASA_DIR = os.path.join(BASE_DIR, "rasa")  # Rasa directory

# Ensure directories exist
os.makedirs(DFLOW_MODELS_DIR, exist_ok=True)
os.makedirs(RASA_DIR, exist_ok=True)

# Ensure dFlow is installed
try:
    import dflow
except ImportError:
    print("dFlow is not installed. Installing now...")
    subprocess.run(["pip", "install", "git+https://github.com/robotics-4-all/dFlow.git"], check=True)

# Step 1: Generate the model using dFlow (into dflow/models/)
print("Generating Rasa model from dFlow DSL...")

generate_command = [
    "textx", "generate",
    os.path.join(DFLOW_DIR, "metamodel.dflow"),
    "--target", "rasa",
    "-o", DFLOW_MODELS_DIR  # Output to dflow/models
]

subprocess.run(generate_command, check=True)
print(f"Metamodel generated in {DFLOW_MODELS_DIR}")

# Step 2: Find the generated tarball
tar_files = [f for f in os.listdir(DFLOW_MODELS_DIR) if f.endswith(".tar.gz")]

if tar_files:
    tar_file = os.path.join(DFLOW_MODELS_DIR, tar_files[0])
    print(f"Found model file: {tar_file}")

    # Step 3: Clean Rasa directory to ensure fresh start
    for item in os.listdir(RASA_DIR):
        item_path = os.path.join(RASA_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
    print("Cleaned Rasa directory for fresh extraction")

    # Step 4: Create a temporary directory for extraction
    temp_dir = os.path.join(BASE_DIR, "temp_extract")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Step 5: Extract the tar.gz file to the temporary directory
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(temp_dir)
        print(f"Extracted model files to temporary directory: {temp_dir}")
    
    # Step 6: Get the extracted directory name (usually the first directory in the archive)
    extracted_items = os.listdir(temp_dir)
    if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
        # Single directory was extracted - move its contents to rasa/
        extracted_dir = os.path.join(temp_dir, extracted_items[0])
        for item in os.listdir(extracted_dir):
            src_path = os.path.join(extracted_dir, item)
            dst_path = os.path.join(RASA_DIR, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        print(f"Moved contents from {extracted_dir} to {RASA_DIR}")
    else:
        # Multiple items were extracted - move everything to rasa/
        for item in extracted_items:
            src_path = os.path.join(temp_dir, item)
            dst_path = os.path.join(RASA_DIR, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        print(f"Moved all extracted items to {RASA_DIR}")
    
    # Step 7: Clean up temporary directory
    shutil.rmtree(temp_dir)
    print("Cleaned up temporary extraction directory")
    
    # Step 8: Create models directory in Rasa if it doesn't exist
    models_dir = os.path.join(RASA_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print("Model structure is ready for training!")
else:
    print("No .tar.gz model file found in the output directory")
