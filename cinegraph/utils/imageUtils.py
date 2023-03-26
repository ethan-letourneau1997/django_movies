import time
import numpy as np
from PIL import Image
import colorgram
import requests
from io import BytesIO
import httpx


def get_contrast_ratio(r, g, b):
    rgb = np.array([r, g, b]) / 255
    gamma = np.where(rgb <= 0.03928, rgb / 12.92,
                     ((rgb + 0.055) / 1.055) ** 2.4)
    luminance = np.dot(gamma, [0.2126, 0.7152, 0.0722])
    contrast_ratio = (1 + 0.05) / (luminance + 0.05)
    return contrast_ratio


def get_image_overlay(image_url):

    image_url = image_url

    num_iterations = 10

    # # > Retrieve the image from the URL using requests
    # t0 = time.time()
    # img_response = requests.get(image_url)
    # t1 = time.time()
    # print(f"Retrieving image took {t1-t0} seconds.")

    # > Retrieve the image from the URL using httpx
    t0 = time.time()
    img_response = httpx.get(image_url)
    t1 = time.time()
    print(f"Retrieving image took {t1-t0} seconds.")

    # > Convert the image data to a PIL Image object
    t0 = time.time()
    img = Image.open(BytesIO(img_response.content))
    t1 = time.time()
    print(f"Converting to PIL Image took {t1-t0} seconds.")

    # > Extract 6 colors from the image using colorgram
    t0 = time.time()
    colors = colorgram.extract(img, 2)
    t1 = time.time()
    print(f"Extracting colors took {t1-t0} seconds.")

    # > Get the two most dominant colors.
    t0 = time.time()
    color1, color2 = sorted(
        colors, key=lambda c: c.proportion, reverse=True)[:2]
    t1 = time.time()
    print(f"Getting dominant colors took {t1-t0} seconds.")

    # > Average color palette values.
    t0 = time.time()
    red = (color1.rgb.r + color2.rgb.r) // 2
    green = (color1.rgb.g + color2.rgb.g) // 2
    blue = (color1.rgb.b + color2.rgb.b) // 2

    t1 = time.time()
    print(f"Calculating average color took {t1-t0} seconds.")

    # # > Ensure image is not too light
    contrast = get_contrast_ratio(red, green, blue)
    while contrast < 4.5:
        red = red*.95
        blue = blue*.95
        green = green*.95
        contrast = get_contrast_ratio(red, green, blue)

    # # > Ensure image is not too dark
    while contrast > 12:
        red = red/.95
        blue = blue/.95
        green = green/.95
        contrast = get_contrast_ratio(red, green, blue)

    # Define background-image string
    backdrop_filter = f"background-image: linear-gradient(to right, rgba({red}, {green}, {blue}, 1) calc((50vw - 170px) - 340px), rgba({red}, {green}, {blue}, 0.84) 50%, rgba({red}, {green}, {blue}, 0.84) 100%);"

    return backdrop_filter
