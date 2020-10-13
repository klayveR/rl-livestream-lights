from classes.image_reader import ImageReader
from classes.config import Config
import os
import glob
import cv2

def prepare(dir, area_keys):
    config = Config.read()
    path = os.path.join(dir, "*.jpg")
    files = glob.glob(path)
    print(files)

    print(path)

    for f in files:
        print(f)
        file_name = os.path.basename(os.path.splitext(f)[0])
        im = cv2.imread(f)

        for area_key in area_keys:
            prepared_im = ImageReader.prepare_image_area(im, config["areas"][area_key])
            file_path = os.path.join(dir, "prepared", f"{file_name}_{area_key}.jpg")
            cv2.imwrite(file_path, prepared_im)

if __name__ == "__main__":
    prepare("screenshots/replay", ["replay"])
    prepare("screenshots/top", ["score_orange", "time", "score_blue"])
    prepare("screenshots/winner", ["winner"])
    prepare("screenshots/kickoff", ["kickoff"])

