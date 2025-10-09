# Meal-Plan-App: Raw Ingredient Detector Setup Guide

This document summarizes the complete process for setting up your environment, preparing the Google Open Images Dataset (OID), and initiating the training of your custom YOLOv8 model for raw food ingredient detection.

---

## 1. Initial Setup and Environment Configuration

These steps ensure your local machine is ready for Python and machine learning development.

### A. Install Prerequisites (Git and System Dependencies)

You must have **Git** installed on your system. If `git --version` fails, install Git for Windows (select the default option that adds Git to your PATH).

If you encounter PyTorch DLL errors later, you must install the Visual C++ Redistributable.

#### ⚠️ **Action: Install Visual C++ Redistributable (Prevent DLL Errors)**

Download and install the necessary Microsoft runtime library to prevent PyTorch from failing:

* **Download:** [Microsoft Visual C++ Redistributable for Visual Studio 2015-2022 (x64)](https://aka.ms/vs/16/release/vc_redist.x64.exe)
* Run the executable and restart your terminal.

### B. Clone Project and Create Environment

Navigate to your desired local folder and clone the repository.

```bash
# 1. Clone the repository (replace URL with your specific GitHub link if needed)
git clone [https://github.com/BillyASC20/Meal-Plan-App.git](https://github.com/BillyASC20/Meal-Plan-App.git)
cd Meal-Plan-App

# 2. Create the isolated Python environment named 'env'
python -m venv env 

# 3. ACTIVATE the environment (Crucial step for installing packages)
.\env\Scripts\Activate.ps1   # <- Use this for PowerShell
# OR
.\env\Scripts\activate       # <- Use this for Command Prompt (CMD)
```

### C. Install Dependencies

Install all required packages (ultralytics, fiftyone, PyTorch dependencies, etc.) using the generated requirements.txt file.

```bash
pip install -r requirements.txt
```

### 2. Dataset Preparation (Download and Convert OID)
This step executes your prepare_dataset.py script to download a filtered subset of raw food ingredients from the massive Google Open Images Dataset (OID) and converts the annotations into the required YOLO format.

Action: Run the preparation script

# Adjust: Start with 500-1000 for a quick test; increase for better results
The default is 10 just for testing.

```bash
python prepare_dataset.py
```
This will create two essential assets in your project root:

OID_YOLO_DATA/: The large folder containing the downloaded images and labels (ignored by Git).

oid_ingredients.yaml: The training configuration file.


### Training the custom YOLOv8 Model
You will now start the fine-tuning process. Since you are using an AMD GPU or running on a standard machine, we use device=cpu to ensure compatibility and stability (but expect training to be slow).

A. The Training Command
Run the following command in your active terminal to begin the training process.

```bash
yolo detect train data=oid_ingredients.yaml model=yolov8n.pt epochs=50 imgsz=640 batch=8 name=raw_food_ingredients_detector_CPU device=cpu
```
Parameter	Value	                Purpose
data=	    oid_ingredients.yaml	Links to your filtered food dataset configuration.

model=	    yolov8n.pt	            Uses pre-trained weights for fast transfer learning.

epochs=	    50	                    Number of cycles over the dataset (recommended start for fine-tuning).

batch=	    8	                    Processes 8 images per step (safe value for CPU/standard RAM).

device=	    cpu	                    Forces CPU utilization to avoid AMD/CUDA errors.

or you can use the script to train the model.
```bash
python train_model.py
```
# Choose the how many epochs you want.


## B. Monitoring and Output
The training will take several hours on a CPU.

The final trained model weights (best.pt) will be saved in: runs/detect/raw_food_ingredients_detector_CPU/weights/

### 4. Running Prediction (Inference)
Once training is complete (or after you run a quick test epoch), you can run your detector.py script. Ensure you update the model path in detector.py to point to your new best.pt file.

Action: Test the trained model

```bash
python detector.py
```

The script will load your custom model and output a clean list of detected food names, validating your entire pipeline.