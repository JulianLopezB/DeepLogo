from src.video_processing import *
from src.fetch_data import *
from src.paths import *

# TODO: obtener el titulo de video de la url (libreria youtube)

#PATHS
video_url = "https://www.youtube.com/watch?v=2femix89pTE&t=4s"
#video_title = '2020 Eifel Grand Prix Race Highlights'
video_title = get_video_id(video_url)
video_category = 'F1'


# GCLOUD STORAGE PARAMS
bucket_name = 'videos-detection'
video_category = 'F1'
blob_path_video = f'videos_files/{video_category}/{video_title}/video.mp4'
uri_video = f'gs://{bucket_name}/'+blob_path_video

pathIn = path_data / str(video_title + '/input/')
pathIn_Video = pathIn / str(video_title + '.mp4')
pathIn_Frames =  pathIn / 'frames'
pathIn_Frames_Resized = pathIn / 'frames_resized'

pathOut = path_data / str(video_title + '/output/')
path_results= pathOut / 'result.json'
path_annotations = pathOut / 'annotations.csv'
path_logos_video = pathOut / f'{video_title} - Logos.mp4'


if __name__ == "__main__":

    # Creates necssary paths
    print('Creating paths...')
    create_paths(pathOut, pathIn_Frames, pathIn_Frames_Resized)

    # Download Video
    if not os.path.isfile(str(pathIn_Video)):
        if os.path.isfile(str(pathIn / str(video_title + '.mkv'))):
            pathIn_Video = pathIn / str(video_title + '.mkv')
            print('Video already stored in local host')
        else:
            print(f'Downloading video from YouTube\'s url {video_url}...')
            download_video(video_url, pathIn_Video)
        #req.urlretrieve(video_url, pathIn_Video)
    else:
        print('Video already stored in local host')

    if not is_stored(blob_path_video, bucket_name):
        print('Video not stored in GCloud')
        # Upload video-file to GCloud
        print('Uploading video file to GCloud...')
        #upload_blob(bucket_name, str(pathIn_Video), blob_path_video)
        retry_on_connectionerror(upload_blob(bucket_name, str(pathIn_Video), blob_path_video))
        #os.remove(pathIn_Video)
    else:
        #print('Video file already stored in GCloud')
        #print('Downloading tmp video file from GCloud...')
        # Download video file from GCloud
        #url = generate_image_url(blob_path_video, bucket_name)
        #req.urlretrieve(url, pathIn_Video)
        pass

    if not os.path.isfile(str(path_results)):
        # Generate annotated data from Google VideoIntelligence
        print('Getting video annotations from VideoIntelligence API...')
        result = get_video_anno(uri_video)

        # Save annotations as json file
        print('Persisting video annotations...')
        persist_result(result, path_results)

    else:
        print('Annotations already generated for this video')
        result = results = load_result(path_results)

    # Get frames from video and save them
    print('Saving video frames...')
    video_to_frames(pathIn_Video, pathIn_Frames)
    #video_url_to_frames(video_url, pathIn_Frames)


    # Creates dataframe with annotations
    print('Creating dataframe with annotations...')
    DfLogos = anno_to_pandas(pathIn_Video, result)
    DfLogos = DfLogos.sort_values(by='frame')

    # Save annotations
    print('Saving annotations as csv file...')
    DfLogos.to_csv(str(path_annotations))
