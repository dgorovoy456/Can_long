import cv2
import time
from skimage.metrics import structural_similarity


def compare_images(image_path_1: str,
                   image_path_2: str,
                   diff_image_path_save: str = ''
                   ) -> float:
    """
    Calculate similarity of two images, returns an float point value of similarity in range from 0 to 1 and
    numpy array represents difference image
    """
    image_1 = cv2.imread(image_path_1)
    image_2 = cv2.imread(image_path_2)

    shape_1 = image_1.shape[1], image_1.shape[0]
    shape_2 = image_2.shape[1], image_2.shape[0]

    if shape_1 != shape_2:
        image_2 = cv2.resize(src=image_2,
                             dsize=shape_1,
                             interpolation=cv2.INTER_AREA)

    # Convert images to grayscale
    before_gray = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY)

    score, diff = structural_similarity(before_gray, after_gray, full=True)

    if diff_image_path_save:
        cv2.imwrite(diff_image_path_save, diff)

    return score


def crop_image(x: int,
               y: int,
               w: int,
               h: int,
               image_path: str) -> str:
    """
    Crops the image by coordinates
    """
    cropped_image_path_save = f"cropped_image_{int(time.time())}.png"
    image1 = cv2.imread(image_path)

    x_w = x + w
    y_h = y + h

    crop_picture = image1[y:y_h, x:x_w]

    cv2.imwrite(cropped_image_path_save, crop_picture)

    return cropped_image_path_save
