from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from moviepy.editor import *
import numpy as np
from configparser import ConfigParser

def get_image_path(folder_path):
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(('.jpg', '.jpeg', '.png'))]


def createVideo(framesWithText, ch):
    framesForVideo = []
    for i, v in enumerate(framesWithText):
        duration = config['duration']['another_frame']
        img_array = np.array(v)
        if i == 0:
            duration = config['duration']['first_frame']
        framesForVideo.append(ImageClip(img_array).set_duration(duration))
    clip = concatenate_videoclips(framesForVideo, method='compose')
    clip.write_videofile(f'test-{ch}.mp4', fps=24, codec='libx264', threads=4, audio=False)


def add_text(image_files):
    framesWithText = []
    font = ImageFont.truetype('font/Garet_Free_Fonts/Garet Fonts/TTF/Garet-Heavy.ttf', 18)
    first_slide_text = config['text']['first_text'] + '\n' + config['text']['second_text']

    for i, photo in enumerate(image_files[:5]):
        background_image = Image.new('RGB', (600, 900), color='black')

        blurred_background = Image.open(photo)
        blurred_background = blurred_background.resize((600, 900))
        blurred_background = blurred_background.filter(ImageFilter.GaussianBlur(radius=5))

        background_image.paste(blurred_background, (0, 0))

        image = Image.open(photo)
        image.thumbnail((600, 700)) 
        image_width, image_height = image.size
        offset = ((600 - image_width) // 2, (900 - image_height) // 2)
        background_image.paste(image, offset)

        drawer = ImageDraw.Draw(background_image)
        another_text = config['text']['another_text'].split(',')

        if i == 0:
            text_width = font.getbbox(first_slide_text)[2]
            text_height = font.getbbox(first_slide_text)[3]
            x = (600 / 2) - 50
            y = (900 / 2) - 50
            outline_thickness = 1
            for dx in range(-outline_thickness, outline_thickness + 1):
                for dy in range(-outline_thickness, outline_thickness + 1):
                    drawer.text((x + dx, y + dy), first_slide_text, font=font, fill='black')
            drawer.text((x, y), first_slide_text, font=font, fill='white')
        else:
            top_text = config['text']['top_text']
            top_text_size = 70
            rect_width = 600
            rect_height = top_text_size + 20
            rect_x = 0
            rect_y = 100
            drawer.rectangle([rect_x, rect_y, rect_x + rect_width, rect_y + rect_height], fill='black')
            text_x = (rect_width - top_text_size) / 2
            text_y = (rect_height - top_text_size) / 2
            drawer.text((text_x, 130), top_text, font=font, fill='white')
            drawer.text((text_x, y+250), another_text[i-1], font=font, fill='white')

        framesWithText.append(background_image.copy())

    return framesWithText


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    
    images_files = get_image_path(config['path']['images_path'])
    
    for i in range(int(config['amount_video']['amount_video'])):
        frames = add_text(images_files)
        createVideo(frames, i)
        del images_files[0:5]
