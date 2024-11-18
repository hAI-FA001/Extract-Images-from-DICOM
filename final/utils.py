import struct
import os
import numpy as np
import cv2


def read_items(f):
    def read_offsets_table():
        group, element = struct.unpack('<HH', f.read(4))
        tag = group << 16 | element
        
        table_len = struct.unpack('<I', f.read(4))[0]
        
        return list(struct.unpack(f'<{table_len // 4}L', f.read(table_len)))
    
    # skip the offsets table
    _ = read_offsets_table()

    frag = []
    while True:
        group, element = struct.unpack('<HH', f.read(4))
        tag = group << 16 | element

        if tag == 0xFFFEE000:
            item_len = struct.unpack('<I', f.read(4))[0]

            frag.append(f.read(item_len))
        elif tag == 0xFFFEE0DD:
            break

    return frag

def parse_img(fragments):
    from PIL import Image
    from io import BytesIO

    imgs = []
    for frag in fragments:
        # use decoder from PIL
        img = Image.open(BytesIO(frag), formats=('JPEG', "JPEG2000"))
        imgs.append(img)

    return imgs

def process_dicoms(files):
    def find_signature_bytes(f):
        # look for (7FE0, 0010) with VR code OB
        sign_bytes = [0xE0, 0x7f, 0x10, 0x0, 0x4f, 0x42]
        equal = True
        data = struct.unpack('<B', f.read(1))[0]
        # data_bytes = [data]
        
        for i in range(len(sign_bytes)):
            if sign_bytes[i] != data:
                equal = False
                break
            data = struct.unpack('<B', f.read(1))[0]
            # data_bytes.append(data)
        
        return equal

    for dicom in files:
        print(f"Processing {dicom}")
        fname, _ = os.path.splitext(dicom)
        fname = fname.split(os.sep)[-1]

        with open(dicom, "rb") as f:
            while True:
                try:
                    if not find_signature_bytes(f):
                        continue
                except:
                    break
                

                
                f.read(1)  # skip reserved bytes
                data_elem_len = struct.unpack('<I', f.read(4))[0]
                is_undef_len = data_elem_len == 0xFF_FF_FF_FF

                if not is_undef_len:
                    continue
                
                imgs = parse_img(read_items(f))
                imgs = np.array(imgs)
