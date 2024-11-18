import os

from utils import process_dicoms

if __name__ == "__main__":
    SLASH = os.sep
    base_dir = ".."

    dicom_files = files = [f"{base_dir}{SLASH}{f}" for f in os.listdir(base_dir) if 'dcm' in os.path.splitext(f)[-1].lower()]
    if len(dicom_files) > 0:
        process_dicoms(dicom_files, save_images=True)
    else:
        print("Found no dicom files. Make sure they end in .dcm")

