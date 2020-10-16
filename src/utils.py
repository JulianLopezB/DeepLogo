from src.paths import *
import configparser

def write_config(video_title):
    """Write user's configuration file."""

    try:
        config = configparser.ConfigParser()
        config['PATHS'] = {
                        'pathIn': 'data/' + str(video_title + '/input/'),
                        'pathIn_Video': 'data/' + 'video_title/input/' + str(video_title + '.mp4'),
                        'pathIn_Frames': 'data/' + str(video_title + '/input/') + 'frames/',
                        'pathIn_Frames_Resized' : 'data/' + str(video_title + '/input/') + 'frames_resized/',
                        'pathIn_Frames_zip': 'data/' + str(video_title + '/input/') + 'frames.zip',
                        'pathOut': 'data/' + str(video_title + '/output/'),
                        'path_results': 'data/' + str(video_title + '/output/') + 'result.json',
                        'path_annotations': 'data/' + str(video_title + '/output/') + 'annotations.csv',
                        'path_logos_video': 'data/' + str(video_title + '/output/') + f'{video_title} - Logos.mp4',
                        'path_model_data': 'data/' + str(video_title + '/output/') + 'data.csv'
                        }

        config['BUCKET'] = { 'bucket_name': 'videos-detection',
                            'video_category' : 'F1'
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
    
