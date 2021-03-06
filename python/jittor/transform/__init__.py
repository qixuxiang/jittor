# ***************************************************************
# Copyright (c) 2020 Jittor.
# Authors:
#     Dun Liang <randonlang@gmail.com>. 
# All Rights Reserved.
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
# ***************************************************************
from PIL import Image
import random
import math
import numpy as np
import warnings
from collections.abc import Sequence, Mapping

def crop(img, top, left, height, width):
    '''
    Function for cropping image.

    Args::

        [in] img(Image.Image): Input image.
        [in] top(int): the top boundary of the cropping box.
        [in] left(int): the left boundary of the cropping box.
        [in] height(int): height of the cropping box.
        [in] width(int): width of the cropping box.

    Example::
        
        img = Image.open(...)
        img_ = transform.crop(img, 10, 10, 100, 100)
    '''
    return img.crop((left, top, left + width, top + height))

def resize(img, size, interpolation=Image.BILINEAR):
    '''
    Function for resizing image.

    Args::

        [in] img(Image.Image): Input image.
        [in] size: resize size.
        [in] interpolation(int): type of resize. default: PIL.Image.BILINEAR

    Example::
        
        img = Image.open(...)
        img_ = transform.resize(img, (100, 100))
    '''
    return img.resize(size[::-1], interpolation)

def crop_and_resize(img, top, left, height, width, size, interpolation=Image.BILINEAR):
    '''
    Function for cropping and resizing image.

    Args::

        [in] img(Image.Image): Input image.
        [in] top(int): the top boundary of the cropping box.
        [in] left(int): the left boundary of the cropping box.
        [in] height(int): height of the cropping box.
        [in] width(int): width of the cropping box.
        [in] size: resize size.
        [in] interpolation(int): type of resize. default: PIL.Image.BILINEAR

    Example::
        
        img = Image.open(...)
        img_ = transform.resize(img, 10，10，200，200，100)
    '''
    img = crop(img, top, left, height, width)
    img = resize(img, size, interpolation)
    return img

class Crop:
    """Crop and the PIL Image to given size.

    Args:

        * top(int): top pixel indexes
        * left(int): left pixel indexes
        * height(int): image height
        * width(int): image width
    """
    def __init__(self, top, left, height, width):
        self.top = top
        self.left = left
        self.height = height
        self.width = width
    def __call__(self, img):
        return crop(img, self.top, self.left, self.height, self.width)


class RandomCropAndResize:
    """Random crop and resize the given PIL Image to given size.

    Args::

        [in] size(int or tuple): width and height of the output image.
        [in] scale(tuple): range of scale ratio of the area.
        [in] ratio(tuple): range of aspect ratio.
        [in] interpolation: type of resize. default: PIL.Image.BILINEAR.

    Example::

        transform = transform.RandomCropAndResize(224)
        img_ = transform(img)
    """
    def __init__(self, size, scale:tuple=(0.08, 1.0), ratio:tuple=(3. / 4., 4. / 3.), interpolation=Image.BILINEAR):
        if isinstance(size, int):
            size = (size, size)
        assert isinstance(size, tuple)
        assert scale[0] <= scale[1] and ratio[0] <= ratio[1]

        self.size = size
        self.scale = scale
        self.ratio = ratio
        self.interpolation = interpolation

    def __call__(self, img:Image.Image):
        width, height = img.size
        scale = self.scale
        ratio = self.ratio
        area = height * width

        for _ in range(10):
            target_area = random.uniform(*scale) * area
            log_ratio = (math.log(ratio[0]), math.log(ratio[1]))
            aspect_ratio = math.exp(random.uniform(*log_ratio))

            w = int(round(math.sqrt(target_area * aspect_ratio)))
            h = int(round(math.sqrt(target_area / aspect_ratio)))

            if 0 < w <= width and 0 < h <= height:
                i = random.randint(0, height - h)
                j = random.randint(0, width - w)
                break
        else:
            # Fallback to central crop
            in_ratio = float(width) / float(height)
            if in_ratio < min(ratio):
                w = width
                h = int(round(w / min(ratio)))
            elif in_ratio > max(ratio):
                h = height
                w = int(round(h * max(ratio)))
            else:
                w = width
                h = height
            i = (height - h) // 2
            j = (width - w) // 2
        return crop_and_resize(img, i, j, h, w, self.size, self.interpolation)
    
class RandomHorizontalFlip:
    """
    Random flip the image horizontally.

    Args::

        [in] p(float): The probability of image flip, default: 0.5.

    Example::

        transform = transform.RandomHorizontalFlip(0.6)
        img_ = transform(img)
    """
    def __init__(self, p=0.5):
        self.p = p
        
    def __call__(self, img:Image.Image):
        if random.random() < self.p:
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        return img

class CenterCrop:
    '''
    Class for cropping image centrally.

    Args::

    [in] size(int or tuple): Size want to crop.

    Example::

        transform = transform.CenterCrop(224)
        img_ = transform(img)
    '''
    def __init__(self, size):
        if isinstance(size, int):
            size = (size, size)
        assert isinstance(size, tuple)
        self.size = size
    
    def __call__(self, img:Image.Image):
        width, height = img.size
        return crop(img, (height - self.size[0]) / 2, (width - self.size[1]) / 2, self.size[0], self.size[1])

def to_tensor(img):
    """
    Function for turning Image.Image to jt.array.

    Args::

        [in] img(Image.Image): Input image.
    
    Example::
        
        img = Image.open(...)
        img_ = transform.to_tensor(img)
    """
    if isinstance(img, Image.Image):
        return np.array(img).transpose((2,0,1)) / np.float32(255)
    return img

class ImageNormalize:
    '''
    Class for normalizing the input image.

    Args::

    [in] mean(list): the mean value of Normalization.
    [in] std(list): the std value of Normalization.

    Example::

        transform = transform.ImageNormalize(mean=[0.5], std=[0.5])
        img_ = transform(img)
    '''

    def __init__(self, mean, std):
        self.mean = np.float32(mean).reshape(-1,1,1)
        self.std = np.float32(std).reshape(-1,1,1)
        
    def __call__(self, img):
        if isinstance(img, Image.Image):
            img = (np.array(img).transpose((2,0,1)) \
                - self.mean*np.float32(255.)) \
                / (self.std*np.float32(255.))
        else:
            img = (img - self.mean) / self.std
        return img
    
class Compose:
    '''
    Base class for combining various transformations.

    Args::

    [in] transforms(list): a list of transform.

    Example::

        transform = transform.Compose([
            transform.Resize(opt.img_size),
            transform.Gray(),
            transform.ImageNormalize(mean=[0.5], std=[0.5]),
        ])
        img_ = transform(img)
    '''
    def __init__(self, transforms):
        self.transforms = transforms
    def __call__(self, data):
        for t in self.transforms:
            data = t(data)
        return data

class Resize:
    '''
    Class for resizing image.

    Args::

    [in] size(int or tuple): Size want to resize.
    [in] mode(int): type of resize.

    Example::

        transform = transform.Resize(224)
        img_ = transform(img)
    '''
    def __init__(self, size, mode=Image.BILINEAR):
        if isinstance(size, int):
            size = (size, size)
        assert isinstance(size, tuple)
        self.size = size
        self.mode = mode
    def __call__(self, img:Image.Image):
        return img.resize(self.size, self.mode)

class Gray:
    '''
    Convert image to grayscale.

    Example::

        transform = transform.Gray()
        img_ = transform(img)
    '''
    def __call__(self, img:Image.Image):
        img = np.array(img.convert('L'))
        img = img[np.newaxis, :]
        return np.array((img / 255.0), dtype = np.float32)

class RandomCrop:
    '''
    Class for randomly cropping the input image.

    Args::

    [in] size(tuple or int): the size want to crop.

    Example::

        transform = transform.RandomCrop(128)
        img_ = transform(img)
    '''
    def __init__(self, size):
        if isinstance(size, int):
            size = (size, size)
        assert isinstance(size, tuple)
        self.size = size
    def __call__(self, img:Image.Image):
        width, height = img.size
        assert self.size[0] <= height and self.size[1] <= width, f"crop size exceeds the input image in RandomCrop"
        top = np.random.randint(0,height-self.size[0]+1)
        left = np.random.randint(0,width-self.size[1]+1)
        return crop(img, top, left, self.size[0], self.size[1])
        