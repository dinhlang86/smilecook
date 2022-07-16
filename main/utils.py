from pickletools import optimize
from passlib.hash import pbkdf2_sha256
import uuid
from flask_uploads import extension
import os
from PIL import Image

from main.extensions import image_set, cache

def hash_password(password):
    return pbkdf2_sha256.hash(password)

def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

def save_image(image, folder):
    filename = '{}.{}'.format(uuid.uuid4(), extension(image.filename))
    image_set.save(image, folder=folder, name=filename)
    filename = compress_image(filename=filename, folder=folder)
    return filename

def compress_image(filename, folder):
    file_path = image_set.path(filename=filename, folder=folder)
    image = Image.open(file_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    if max(image.width, image.height) > 1600:
        maxsize = (1600, 1600)
        image.thumbnail(maxsize, Image.ANTIALIAS)
    compress_filename = '{}.jpg'.format(uuid.uuid4)
    compress_file_path = image_set.path(filename=compress_filename, folder=folder)
    image.save(compress_file_path, optimize=True, quality=85)
    
    original_size = os.stat(file_path).st_size
    compress_size = os.stat(compress_file_path).st_size
    percentage = round((original_size - compress_size)/original_size * 100)
    print(f'The file size is reduced by {percentage}%, from {original_size} to {compress_size}')
    
    os.remove(file_path)
    return compress_filename

# Clear cache with the keys have the prefix
# *keys: unpacking the list of keys into positional arguments
def clear_cache(key_prefix):
    keys = [key for key in cache.cache._cache.keys() if key.startswith(key_prefix)]
    cache.delete_many(*keys)