import pandas as pd
from pathlib import Path
import glob
import pafy
import youtube_dl
import io
from PIL import Image
from tqdm import tqdm_notebook, tqdm
import cv2
import json
from tqdm import tqdm_notebook as tqdm
from pathlib import Path
import os
import math
import datetime
import urllib.request as req
import urllib.parse as urlparse
from google.protobuf.json_format import MessageToJson
import ast
from apiclient.http import MediaFileUpload

#from google.cloud import videointelligence_v1p3beta1 as videointelligence
from google.cloud import videointelligence
from google.oauth2 import service_account


path_data = Path('./data')
path_json = path_data / 'logo-detection.json'

credentials = service_account.Credentials.from_service_account_file(path_json)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(path_json)


def create_paths(pathOut, pathIn_Frames, pathIn_Frames_Resized):

    if not os.path.exists(pathOut):
        os.makedirs(pathOut)

    if not os.path.exists(pathIn_Frames):
        os.makedirs(pathIn_Frames)
        
    if not os.path.exists(pathIn_Frames_Resized):
        os.makedirs(pathIn_Frames_Resized)
    
def load_videos(video_file):
    
    capture = cv2.VideoCapture(video_file)

    fps = capture.get(cv2.CAP_PROP_FPS)
    
    read_flag, frame = capture.read()
    
    vid_frames = []

    while (read_flag):
        
        vid_frames.append(frame)
        
        read_flag, frame = capture.read()
        
    vid_frames = np.asarray(vid_frames, dtype='uint8')
    
    capture.release()
    
    return vid_frames, fps


def get_video_anno(input_video, local=False):
    """
    Performs asynchronous video annotation for logo recognition on a local file.

    """
    client = videointelligence.VideoIntelligenceServiceClient(credentials=credentials)

    if local:
        with io.open(input_video, 'rb') as f:
            input_video = f.read()
            input_video = str(input_video).encode('utf-8')
        
    features = [videointelligence.enums.Feature.LOGO_RECOGNITION]
    operation = client.annotate_video(input_video, features=features, location_id='us-west1')
    print('\nProcessing video for logo annotations:')
    
    print(u'Waiting for operation to complete...')
    response = operation.result(timeout=1000)
    print('\nFinished processing.')
  
    return response

def video_to_frames(vid_input, pathOut):

    #start the video
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,  480))

    cap = cv2.VideoCapture(str(vid_input))

    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    count = 0

    while(cap.isOpened()):

        #Capture frame-by-frame
        ret, frame = cap.read()

        if ret==True:

            write_frame(count, frame, pathOut)

            ret, frame = cap.read()
            count += 1
            wait = cv2.waitKey(10)

            if wait==27 & 0xFF == ord('q'):
                break   

        else:
            break

    cap.release()
    cv2.destroyAllWindows()


def write_frame(count, frame, pathOut):

    cv2.imwrite(str(pathOut / f'frame{count}.jpg'), frame)

    if not cv2.imwrite(str(pathOut / f'frame{count}.jpg'), frame):
        raise Exception("Could not write image")
        
def download_video(video_url, pathIn_Video):
    """
    Download a video using youtube url and video title
    """
    if not os.path.isfile(str(pathIn_Video)):
        ydl_opts = {'outtmpl': str(pathIn_Video), format:'-f 133+14'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    else:
        print('Video file already exists')
        
def download_video_bis(video_url, pathIn_Video):
    """
    Download a video using youtube url and video title
    """
    from pytube import YouTube
    yt = YouTube(video_url)
    yt = yt.get('mp4', '720p')
    yt.download(str(pathIn_Video))

        
def anno_to_pandas(pathIn_Video, result):

    vcap = cv2.VideoCapture(str(pathIn_Video))

    fps = vcap.get(cv2.CAP_PROP_FPS)
    width, height = (int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    annotation_result = result['annotationResults'][0]
    
    DfLogos = pd.DataFrame()

    if 'logoRecognitionAnnotations' in annotation_result:
        for label in tqdm(annotation_result['logoRecognitionAnnotations']):
            for track in label['tracks']:
                confidence = track['confidence']
                for idx, anno in enumerate(track['timestampedObjects']):
                    
                    micro, seconds = math.modf(float(anno['timeOffset'].replace('s', '')))
                    bounding_box = dict()
                    anno_bounding_box = anno['normalizedBoundingBox']
                    for key in ['top', 'bottom', 'left', 'right']:
                        bounding_box[key] = anno_bounding_box.get(key, 0)

                    df_tmp = pd.DataFrame({'seconds': seconds,
                                           'micro': micro,
                                           'frame': int((seconds + micro)*fps/2)+1,
                                           'logo': label['entity']['description'],
                                           'x1': int(bounding_box['left']*width), 
                                           'y1': int(bounding_box['top']*height),
                                           'x2': int(bounding_box['right']*width),
                                           'y2': int(bounding_box['top']*height),
                                           'x3': int(bounding_box['right']*width),
                                           'y3': int(bounding_box['bottom']*height),
                                           'x4': int(bounding_box['left']*width),
                                           'y4': int(bounding_box['bottom']*height),
                                           'conficence': confidence}, index=[idx])
                    DfLogos = DfLogos.append(df_tmp, sort=False, ignore_index=True)

    else:
        raise ValueError('Annotation file (json) truncated')

    return DfLogos

def video_url_to_frames(video_url, pathOut):

    ydl_opts = {}

    # create youtube-dl object
    ydl = youtube_dl.YoutubeDL(ydl_opts)

    # set video url, extract video information
    info_dict = ydl.extract_info(video_url, download=False)

    # get video formats available
    formats = info_dict.get('formats',None)

    for f in formats:

        # I want the lowest resolution, so I set resolution as 144p
        if f.get('format_note',None) == '144p':

            #get the video url
            url = f.get('url',None)
            
            cap = cv2.VideoCapture(url)

            if (cap.isOpened()== False): 
                print("Error opening video stream or file")

            count = 0

            while(cap.isOpened()):

                #Capture frame-by-frame
                ret, frame = cap.read()

                if ret==True:

                    write_frame(count, frame, pathOut)

                    ret, frame = cap.read()
                    count += 1
                    wait = cv2.waitKey(10)

                    if wait==27 & 0xFF == ord('q'):
                        break   

                else:
                    break
            

#             # open url with opencv
#             cap = cv2.VideoCapture(url)

#             # check if url was opened
#             if not cap.isOpened():
#                 print('video not opened')
#                 exit(-1)

#             ret, frame = cap.read()
#             count = 0
#             while True:
                
#                 write_frame(count, frame, pathOut)
                    
#                 # read frame
#                 ret, frame = cap.read()
                
#                 count += 1
                
#                 # check if frame is empty
#                 if not ret:
#                     break

#                 # display frame
#                 cv2.imshow('frame', frame)

#                 if cv2.waitKey(30)&0xFF == ord('q'):
#                     breakz

            # release VideoCapture
            cap.release()

    cv2.destroyAllWindows()
    
def persist_result(result, path_results):
    serialized = MessageToJson(result)
    serialized = ast.literal_eval(serialized)
    with open(str(path_results), 'w') as f:
        json.dump(serialized, f)


def load_result(path_results):
    with open(str(path_results), 'r') as data:
        results = json.loads(data.read())
    return results

def get_video_id(video_url):
    url_data = urlparse.urlparse(video_url)
    query = urlparse.parse_qs(url_data.query)
    return query["v"][0]

