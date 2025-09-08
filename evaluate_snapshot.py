#!/bin/python3

import pytesseract
from PIL import Image
import cv2
import numpy as np
import re

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


def preprocess_image(image_path: str) -> np.ndarray:

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image file '{image_path}' not found or cannot be opened.")

    # Increase image resolution
    height, width = image.shape[:2]
    new_size = (width * 2, height * 2)
    image = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply binary thresholding to enhance text contrast
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return binary


def extract_text(image_path: str) -> str:

    processed_image = preprocess_image(image_path)
    pil_image = Image.fromarray(processed_image)

    custom_config = r'--oem 3 --psm 6 -l eng'
    text = pytesseract.image_to_string(pil_image, config=custom_config)

    return text


def clean_text(text: str) -> str:
    # Manual corrections for common OCR issues
    text = text.replace('24.64', '24.04')
    text = text.replace('Mam', 'LTS')

    # Replace common errors for Fall
    text = text.replace('Fal1', 'Fall')
    text = text.replace('Fa1l', 'Fall')
    text = text.replace('Fa11', 'Fall')
    text = text.replace('Falll', 'Fall')

    # Replace common errors for is
    text = text.replace('1s','is')

    # Remove unwanted characters and fix common OCR issues
    text = re.sub(r'[^\w\s:.]', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def check_syscall_output(syscall_img_path):

    syscall_text = extract_text(syscall_img_path)
    syscall_text = clean_text(syscall_text)

    print(f'[TC-1-log] Extracted text: {syscall_text}')

    pattern = r'This is the new system call .* implemented.'
    found = re.search(pattern, syscall_text, re.IGNORECASE)
    status = 'Fail'
    if not found:
        print('Syscall output incorrect')
        print(f'Extracted: {syscall_text}')
        #exit(1)
    else:
        print('Pass')
        status = 'Pass'

    return status,syscall_text

def check_lts_release(lsb_img_path):

    # lts_release_text = extract_text('lsb_release.png')
    lts_release_text = extract_text(lsb_img_path)
    lts_release_text = clean_text(lts_release_text)

    print(f'Extracted text: {lts_release_text}')

    pattern = r'Release:\s*24\.04(\.\d+)?'
    found = re.search(pattern, lts_release_text, re.IGNORECASE)
    status = 'Fail'

    if not found:
        print('LTS incorrect')
        print(f'Extracted: {lts_release_text}')
        # exit(1)
    else:
        print('Pass')
        status = 'Pass'

    return status, lts_release_text


def check_kernel_version(uname_img_path):
    # kernel_version_text = extract_text('uname.png')
    kernel_version_text = extract_text(uname_img_path)
    kernel_version_text = clean_text(kernel_version_text)

    print(f'Extracted text: {kernel_version_text}')

    pattern = r'6\.10\.0CSE330Fall2024'
    found = re.search(pattern, kernel_version_text)
    status = 'Fail'
    if not found:
        print('Kernel Version Incorrect')
        print(f'Extracted: {kernel_version_text}')
        # exit(1)
    else:
        print('Pass')
        status = 'Pass'

    return status, kernel_version_text


if __name__ == '__main__':
    check_syscall_output('syscall_output.png')
    check_lts_release('lsb_release.png')
    check_kernel_version('uname.png')

