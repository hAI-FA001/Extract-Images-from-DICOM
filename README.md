# Extract Images from DICOM

Extracts and saves images from dicom files in the specified base directory.

## How to Run

- Install `numpy`, `cv2` and `PIL`
- Set the `base_dir` variable in `main.py` appropriately
- Run using `python main.py`

## To-Do

Currently, it works on some assumptions:

- Images are stored in JPG inside the dicom
- Data element length must be undefined, i.e. `0xFFFFFFFF`
- Item element length must be defined
- Data element's signature is `E0 7F 10 00 4F 42`, i.e. `(7FE0, 0010)` with VR code `OB`, followed by reserved bytes `00 00`

These assumptions hold for the files it was tested on, and may be handled in the future.
