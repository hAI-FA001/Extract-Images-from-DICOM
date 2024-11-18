import os

from utils import process_dicoms

if __name__ == "__main__":
    base_dir = "../"

    dicom_files = files = [f"{base_dir}{f}" for f in os.listdir(base_dir) if 'dcm' in os.path.splitext(f)[-1].lower()]
    process_dicoms(dicom_files, save_images=True)

