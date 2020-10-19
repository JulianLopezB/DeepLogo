from src.paths import *
import configparser
import os
import glob
import zipfile
import pandas as pd
from sklearn import preprocessing
import pickle

def write_config(video_title, video_category):
    """Write user's configuration file."""

    try:
        config = configparser.ConfigParser()

        # Paths
        config['PATHS'] = {

                        # Inputs paths
                        'pathIn': f'data/video-files/{video_category}/{video_title}/input/',
                        'pathIn_Video': f'data/video-files/{video_category}/{video_title}/input/{video_title}.mp4',
                        'pathIn_Frames': f'data/video-files/{video_category}/{video_title}/input/' + 'frames/',
                        'pathIn_Frames_Resized' : f'data/video-files/{video_category}/{video_title}/input/frames_resized/',
                        'pathIn_Frames_zip': f'data/video-files/{video_category}/{video_title}/input/frames.zip',

                        # Output paths
                        'pathOut': f'data/video-files/{video_category}/{video_title}/output/',
                        'path_results': f'data/video-files/{video_category}/{video_title}/output/result.json',
                        'path_annotations': f'data/video-files/{video_category}/{video_title}/output/annotations.csv',
                        'path_logos_video': f'data/video-files/{video_category}/{video_title}/output/{video_title}_logos.mp4',
                        'path_model_data': f'data/video-files/{video_category}/{video_title}/output/data.csv'
                        }

        # Gcloud Storage Bucket
        config['BUCKET'] = { 'bucket_name': 'videos-detection',
                            'video_category' : video_category
                            }

        with open(pathConfig, 'w') as configfile:
            config.write(configfile)

    except:
        print('Error while creating the user config file.')
        return False

    return config 

def read_config(pathConfig):
    config = configparser.ConfigParser()
    config.read(pathConfig)

    return config


def zip_dir(path, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(path)
    for root, dirs, files in os.walk(str(path)):
        for f in files:
            absname = os.path.abspath(os.path.join(root, f))
            arcname = absname[len(abs_src) + 1:]
            print(f'zipping {os.path.join(root, f)} as {arcname}')
            zipf.write(absname, arcname)
            #zipf.write(os.path.join(root, f))
    zipf.close()



def create_paths(pathOut, pathIn_Frames, pathIn_Frames_Resized):

    if not os.path.exists(pathOut):
        os.makedirs(pathOut)

    if not os.path.exists(pathIn_Frames):
        os.makedirs(pathIn_Frames)
        
    if not os.path.exists(pathIn_Frames_Resized):
        os.makedirs(pathIn_Frames_Resized)

    print(f'Path "{pathOut}" created')
    print(f'Path "{pathIn_Frames}" created')
    print(f'Path "{pathIn_Frames_Resized}" created')

def concatenate_anno(path, video_category):

    le = preprocessing.LabelEncoder()
    list_data = []

    #df = pd.DataFrame()
    for root,dirs,_ in os.walk(path):
        for d in dirs:
            path_sub = os.path.join(root,d) # this is the current subfolder
            for filename in glob.glob(os.path.join(path_sub, '*.csv')):
                if os.path.split(filename)[1] == 'data.csv' and video_category in filename:
                    print(f'Concatenating {filename}')
                    #df = pd.concat([df, pd.read_csv(filename, index_col=[0])])
                    list_data.append(filename)
                    #df = pd.concat([df, pd.read_json(filename)])
                    #infile = open(filename,'rb')
                    #list_data.append(pickle.load(infile))
                    #df = pd.concat([df, pd.DataFrame(pickle.load(infile))])

    df = pd.concat([pd.read_csv(x) for x in list_data], axis=0)

    if len(df) >  0:
        if 'class' in df.columns:
            df['class'] = le.fit_transform(df['class'])
        else:
            raise ValueError("Column 'class' not found")
        df['category'] = video_category
        print(f'Data concatenated. {len(df)} annotations were appended')
    else:
        raise ValueError("No annotations found")
    
    return df

    
