import struct
import os
import numpy as np
import cv2


def read_items(f):
    def read_offsets_table():
        group, element = struct.unpack('<HH', f.read(4))
        tag = group << 16 | element
        if tag != 0xFFFEE000:
            print(f"{tag:0x}")
            raise ValueError('Incorrect tag for Offset Table')
        
        table_len = struct.unpack('<I', f.read(4))[0]
        if table_len % 4 != 0:
            raise ValueError('Offset Table length must be a multiple of 4')
        
        return list(struct.unpack(f'<{table_len // 4}L', f.read(table_len)))
    
    # skip the offsets table
    _ = read_offsets_table()

    frag = []
    while True:
        group, element = struct.unpack('<HH', f.read(4))
        tag = group << 16 | element

        if tag == 0xFFFEE000:
            item_len = struct.unpack('<I', f.read(4))[0]

            if item_len == 0xFFFFFFFF:
                raise ValueError('Undefined Item Length')
            
            frag.append(f.read(item_len))
        elif tag == 0xFFFEE0DD:
            break
        else:
            raise ValueError(f"Incorrect tag found while reading items: {tag:0x}\nExpected Item Tag 0xFFFEE000 or Sequence Delimiter Tag 0xFFFEE0DD")

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

def process_dicoms(files, save_images=False):
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
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(0, os.SEEK_SET)

            while True:
                try:
                    if not find_signature_bytes(f):
                        continue
                except:
                    if f.tell() != file_size:
                        print(f'Unknown Error at offset: {f.tell()}')
                    else:
                        print(f"Finished reading {dicom}")
                    break
                

                
                f.read(1)  # skip reserved bytes
                data_elem_len = struct.unpack('<I', f.read(4))[0]
                is_undef_len = data_elem_len == 0xFF_FF_FF_FF

                if not is_undef_len:
                    print(f"Expected undefined length but got {data_elem_len:0x}. Skipping...")
                    continue
                
                print("Extracting raw images...")
                imgs = parse_img(read_items(f))
                imgs = np.array(imgs)
                
                print(f'Read {len(imgs)} images')
        print()

