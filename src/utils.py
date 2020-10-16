from src.paths import *
import configparser
import os
import zipfile

def write_config(video_title, video_category):
    """Write user's configuration file."""

    try:
        config = configparser.ConfigParser()
        config['PATHS'] = {
                        'pathIn': f'data/video-files/{video_category}/{video_title}/input/',
                        'pathIn_Video': f'data/video-files/{video_category}/{video_title}/input/' + str(video_title + '.mp4'),
                        'pathIn_Frames': f'data/video-files/{video_category}/{video_title}/input/' + 'frames/',
                        'pathIn_Frames_Resized' : f'data/video-files/{video_category}/{video_title}/input/' + 'frames_resized/',
                        'pathIn_Frames_zip': f'data/video-files/{video_category}/{video_title}/input/' + 'frames.zip',
                        'pathOut': f'data/video-files/{video_category}/{video_title}/output/',
                        'path_results': f'data/video-files/{video_category}/{video_title}/output/' + 'result.json',
                        'path_annotations': f'data/video-files/{video_category}/{video_title}/output/' + 'annotations.csv',
                        'path_logos_video': f'data/video-files/{video_category}/{video_title}/output/' + f'{video_title} - Logos.mp4',
                        'path_model_data': f'data/video-files/{video_category}/{video_title}/output/' + 'data.csv'
                        }

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
    #zipf = zipfile.ZipFile(str(zip_name), 'w', zipfile.ZIP_DEFLATED)
    zipf = zipfile.ZipFile(str(zip_name), 'w')
    for root, dirs, files in os.walk(str(str(path))):
        for f in files:
            zipf.write(os.path.join(root, f))
    zipf.close()

def create_paths(pathOut, pathIn_Frames, pathIn_Frames_Resized):

    if not os.path.exists(pathOut):
        os.makedirs(pathOut)

    if not os.path.exists(pathIn_Frames):
        os.makedirs(pathIn_Frames)
        
    if not os.path.exists(pathIn_Frames_Resized):
        os.makedirs(pathIn_Frames_Resized)
    
