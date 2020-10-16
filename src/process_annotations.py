from pathlib import Path
from tqdm import tqdm_notebook as tqdm
import pandas as pd
import numpy as np
import random
import cv2
import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import os
import os
from sklearn import preprocessing
from src.paths import *
from src.utils import *

config = read_config(pathConfig)
pathIn = config['PATHS']['pathIn']
pathIn_Video = config['PATHS']['pathIn_Video']
pathIn_Frames = config['PATHS']['pathIn_Frames']
pathIn_Frames_Resized = config['PATHS']['pathIn_Frames_Resized']
pathIn_Frames_zip = config['PATHS']['pathIn_Frames_zip']
pathOut = config['PATHS']['pathOut']
path_results = config['PATHS']['path_results']
path_annotations = config['PATHS']['path_annotations']
path_logos_video = config['PATHS']['path_logos_video']
path_model_data = config['PATHS']['path_model_data']


def create_path(frame): 
    return Path(pathIn_Frames) / str(f'frame{frame}.jpg')

def create_data(df, NUM_FRAMES):

    le = preprocessing.LabelEncoder()
    
    data = pd.DataFrame({'index': range(NUM_FRAMES)})
    data = data.join(df.set_index('frame'))

    data['logo'].fillna('None', inplace=True)
    data.fillna(0, inplace=True)
    data['filename'] = data['index'].apply(create_path)
    data['widht'] = data['x2'] - data['x1']
    data['height'] = data['y3'] - data['y1']
    data['class'] = le.fit_transform(data['logo'])
    data['xmin'] = data['x1']
    data['ymin'] = data['y1']
    data['xmax'] = data['x2']
    data['ymax'] = data['y3']
    
    data = data[['filename', 'widht', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']]

    return data

def create_mask(bb, x):
    """Creates a mask for the bounding box of same shape as image"""
    rows,cols,*_ = x.shape
    Y = np.zeros((rows, cols))
    bb = bb.astype(np.int)
    Y[bb[0]:bb[2], bb[1]:bb[3]] = 1.
    return Y

def mask_to_bb(Y):
    """Convert mask Y to a bounding box, assumes 0 as background nonzero object"""
    cols, rows = np.nonzero(Y)
    if len(cols)==0: 
        return np.zeros(4, dtype=np.float32)
    top_row = np.min(rows)
    left_col = np.min(cols)
    bottom_row = np.max(rows)
    right_col = np.max(cols)
    return np.array([left_col, top_row, right_col, bottom_row], dtype=np.float32)

def create_bb_array(x):
    """Generates bounding box array from a train_df row"""
    return np.array([x[5],x[4],x[7],x[6]])

def resize_image_bb(read_path,write_path,bb,sz):
    """Resize an image and its bounding box and write image to new path"""
    im = read_image(read_path)
    im_resized = cv2.resize(im, (int(1.49*sz), sz))
    Y_resized = cv2.resize(create_mask(bb, im), (int(1.49*sz), sz))
    new_path = str(write_path/read_path.parts[-1])
    cv2.imwrite(new_path, cv2.cvtColor(im_resized, cv2.COLOR_RGB2BGR))
    return new_path, mask_to_bb(Y_resized)

# modified from fast.ai
def crop(im, r, c, target_r, target_c): 
    return im[r:r+target_r, c:c+target_c]

# random crop to the original size
def random_crop(x, r_pix=8):
    """ Returns a random crop"""
    r, c,*_ = x.shape
    c_pix = round(r_pix*c/r)
    rand_r = random.uniform(0, 1)
    rand_c = random.uniform(0, 1)
    start_r = np.floor(2*rand_r*r_pix).astype(int)
    start_c = np.floor(2*rand_c*c_pix).astype(int)
    return crop(x, start_r, start_c, r-2*r_pix, c-2*c_pix)

def center_crop(x, r_pix=8):
    r, c,*_ = x.shape
    c_pix = round(r_pix*c/r)
    return crop(x, r_pix, c_pix, r-2*r_pix, c-2*c_pix)

def rotate_cv(im, deg, y=False, mode=cv2.BORDER_REFLECT, interpolation=cv2.INTER_AREA):
    """ Rotates an image by deg degrees"""
    r,c,*_ = im.shape
    M = cv2.getRotationMatrix2D((c/2,r/2),deg,1)
    if y:
        return cv2.warpAffine(im, M,(c,r), borderMode=cv2.BORDER_CONSTANT)
    return cv2.warpAffine(im,M,(c,r), borderMode=mode, flags=cv2.WARP_FILL_OUTLIERS+interpolation)

def random_cropXY(x, Y, r_pix=8):
    """ Returns a random crop"""
    r, c,*_ = x.shape
    c_pix = round(r_pix*c/r)
    rand_r = random.uniform(0, 1)
    rand_c = random.uniform(0, 1)
    start_r = np.floor(2*rand_r*r_pix).astype(int)
    start_c = np.floor(2*rand_c*c_pix).astype(int)
    xx = crop(x, start_r, start_c, r-2*r_pix, c-2*c_pix)
    YY = crop(Y, start_r, start_c, r-2*r_pix, c-2*c_pix)
    return xx, YY

def transformsXY(path, bb, transforms):
    x = cv2.imread(str(path)).astype(np.float32)
    x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)/255
    Y = create_mask(bb, x)
    if transforms:
        rdeg = (np.random.random()-.50)*20
        x = rotate_cv(x, rdeg)
        Y = rotate_cv(Y, rdeg, y=True)
        if np.random.random() > 0.5: 
            x = np.fliplr(x).copy()
            Y = np.fliplr(Y).copy()
        x, Y = random_cropXY(x, Y)
    else:
        x, Y = center_crop(x), center_crop(Y)
    return x, mask_to_bb(Y)

def create_corner_rect(bb, color='red'):
    bb = np.array(bb, dtype=np.float32)
    return plt.Rectangle((bb[1], bb[0]), bb[3]-bb[1], bb[2]-bb[0], color=color,
                         fill=False, lw=3)

def show_corner_bb(im, bb):
    plt.imshow(im)
    plt.gca().add_patch(create_corner_rect(bb))
    
def read_image(filename): 
    return mpimg.imread(filename)

def populate_data(df):
    df_new = df.copy()
    #Populating Training DF with new paths and bounding boxes
    new_paths = []
    new_bbs = []
    for index, row in tqdm(df_new.iterrows(), total=df_new.shape[0]):
        new_path,new_bb = resize_image_bb(row['filename'], Path(pathIn_Frames_Resized), create_bb_array(row.values),300)
        new_paths.append(new_path)
        new_bbs.append(new_bb)
    df_new['new_path'] = new_paths
    df_new['new_bb'] = new_bbs
    
    return df_new



