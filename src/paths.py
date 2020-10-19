from pathlib import Path

path_data = Path('./data')
path_json = path_data / 'credentials/credentials_POSTA.json'
pathConfig = path_data / 'config.ini'

# # #PATHS
# pathIn = None
# pathIn_Video = None
# pathIn_Frames =  None
# pathIn_Frames_Resized = None
# pathIn_Frames_zip =None

# pathOut = None
# path_results= None
# path_annotations = None
# path_logos_video = None
# path_model_data = None

# # video_title = ''

# def define_paths(video_title):

#     global pathIn
#     pathIn = path_data / str(video_title + '/input/')

#     global pathIn_Video
#     pathIn_Video = pathIn / str(video_title + '.mp4')

#     global pathIn_Frames
#     pathIn_Frames =  pathIn / 'frames'

#     global pathIn_Frames_Resized
#     pathIn_Frames_Resized = pathIn / 'frames_resized'

#     global pathIn_Frames_zip
#     pathIn_Frames_zip = pathIn / 'frames.zip'

#     global pathOut
#     pathOut = path_data / str(video_title + '/output/')

#     global path_results
#     path_results= pathOut / 'result.json'

#     global path_annotations
#     path_annotations = pathOut / 'annotations.csv'

#     global path_logos_video
#     path_logos_video = pathOut / f'{video_title} - Logos.mp4'

#     global path_model_data
#     path_model_data = pathOut / 'data.csv'

# define_paths(video_title)
