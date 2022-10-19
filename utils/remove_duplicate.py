import hashlib
import os
from pathlib import Path
import time
import shutil
import cv2
from PIL import Image
from loguru import logger as LOGGER
from tqdm import tqdm




def get_md5(img_path):
    m = hashlib.md5(open(img_path,'rb').read())
    return m.hexdigest()




def main():

    input_dir = "set_3"
    image_list = [x for x in Path(input_dir).iterdir() if x.suffix in ('.png', '.jpg', '.jpeg')]
    LOGGER.info(f"Has {len(image_list)} images.")

    img_md5_dict = {} # {md5: abs_img_path}

    MV_DIR = "moved_data"
    if not Path(MV_DIR).exists():
        Path(MV_DIR).mkdir(exist_ok=True, parents=True)

    # t1 = time.time()
    for img in tqdm(image_list):

        if cv2.imread(str(img.resolve())) is not None:
            md5 = get_md5(str(img.resolve()))

            if md5 in img_md5_dict.keys():
                similar_img_path = img_md5_dict[md5]
                shutil.move(str(img.resolve()), str(Path(MV_DIR).resolve()))
                LOGGER.success(f"Move [{img} to {Path(MV_DIR)}] | similar image is [{similar_img_path}]")
            else:
                img_md5_dict[md5] = str(Path(img))

        else:
            shutil.move(str(img.resolve()), str(Path(MV_DIR).resolve()))
            LOGGER.success(f"Wrong image! Move [{img} to {Path(MV_DIR)}]")




if __name__=='__main__':
    main()
