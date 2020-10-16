import argparse
from src.video_processing import *
from src.process_annotations import *
from src.fetch_data import *
from src.paths import *

# ARGS 

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", type=str,
                    help="Youtube URL")
parser.add_argument("-c", "--category", type=str,
                    help="Video category (example: F1, Tennis, Futbol)")

args = parser.parse_args()

video_url = args.url
video_category = args.category

#video_url = 'https://www.youtube.com/watch?v=TB5yhZdF8SI'
#video_url = "https://www.youtube.com/watch?v=EmZtTd1YRmA"
#video_url = "https://www.youtube.com/watch?v=2femix89pTE&t=4s"

# PARAMS
#ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#chunk_size = 1024 * 1024  # 1MB
chunk_size = 512 * 512 # 0.5MB

video_title = get_video_id(video_url)

config = write_config(video_title, video_category)

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

bucket_name = config['BUCKET']['bucket_name']
video_category = config['BUCKET']['video_category']

if __name__ == "__main__":


    # 1) CREATES PATHS
    print('Creating paths...')
    create_paths(pathOut, pathIn_Frames, pathIn_Frames_Resized)

    
    # 2) DOWNLOAD VIDEO
    if not os.path.isfile(str(pathIn_Video)):
        if os.path.isfile(str(pathIn + str(video_title + '.mkv'))):
            pathIn_Video = pathIn + str(video_title + '.mkv')
            print('Video already stored in local host')
        else:
            print(f'Downloading video from YouTube...')
            download_video(video_url, pathIn_Video)
            if os.path.isfile(str(pathIn + str(video_title + '.mkv'))):
                pathIn_Video = pathIn + str(video_title + '.mkv')
        #req.urlretrieve(video_url, pathIn_Video)
    else:
        print('Video already stored in local host')


    # 3) STORE IN CLOUD STORAGE
    blob_path_video = f'videos_files/{video_category}/{video_title}/video.mp4'

    if not is_stored(blob_path_video, bucket_name):
        print('Video not stored in GCloud')
        # Upload video-file to GCloud
        print('Uploading video file to GCloud Storage...')
        #upload_blob(bucket_name, str(pathIn_Video), blob_path_video)
        #retry_on_connectionerror(upload_blob(bucket_name, str(pathIn_Video), blob_path_video))
        fileType = 'application/mp4'
        upload_file_to_gstore(bucket_name, str(pathIn_Video), blob_path_video, fileType, chunk_size)
        #os.remove(pathIn_Video)
    else:
        print('Video file already stored in GCloud Storage')
        #print('Downloading tmp video file from GCloud...')
        # Download video file from GCloud
        #url = generate_image_url(blob_path_video, bucket_name)
        #req.urlretrieve(url, pathIn_Video)
        pass

    # 4) GET VIDEO ANNOTATIONS FROM VIDEO INTELLIGENCE
    if not os.path.isfile(str(path_results)):
        # Generate annotated data from Google VideoIntelligence
        print('Getting video annotations from VideoIntelligence API...')
        uri_video = f'gs://{bucket_name}/'+blob_path_video
        result = get_video_anno(uri_video)

        # Save annotations as json file
        print('Persisting video annotations...')
        persist_result(result, path_results)

    else:
        print('Results (JSON)  already generated for this video')

    blob_path_results = f'videos_files/{video_category}/{video_title}/results.json'
    if not is_stored(blob_path_results, bucket_name):
        fileType = 'application/json'
        upload_file_to_gstore(bucket_name, str(path_results), blob_path_results, fileType, chunk_size)
        print('Video annotations uploaded to GCLoud')

    else:
        print('Results (JSON) already stored in GCloud')    


     # 5) GET FRAMES FROM VIDEO 
    lenght = count_frames(pathIn_Video)
    NUM_FRAMES = len([name for name in os.listdir(str(pathIn_Frames))])
    if abs(lenght - NUM_FRAMES) < 10:
        print('Frames already stored in disk')
    else:
        delete_path_content(pathIn_Frames)
        # Get frames from video and save them
        print('Saving video frames to disk')
        video_to_frames(pathIn_Video, pathIn_Frames)
        #video_url_to_frames(video_url, pathIn_Frames)

    # 6) CREATE CSV WITH RAW ANNOTATINOS 
    if not os.path.isfile(str(path_annotations)):
        # Creates dataframe with annotations
        print('Creating dataframe with raw annotations...')
        result = results = load_result(path_results)
        annotations_df = anno_to_pandas(pathIn_Video, result)
        annotations_df = annotations_df.sort_values(by='frame')
        # Save annotations
        print('Saving annotations as csv file...')
        annotations_df.to_csv(str(path_annotations))

    else:
        print('Video annotations (.csv) already stored in disk')
        annotations_df = pd.read_csv(path_annotations, index_col=[0]).sort_values(by='frame')

    blob_path_anno = f'videos_files/{video_category}/{video_title}/annotations.csv'
    if not is_stored(blob_path_anno, bucket_name):
        fileType = 'text/csv'
        upload_file_to_gstore(bucket_name, str(path_annotations), blob_path_anno, fileType, chunk_size)
        print('Video annotations (.csv) uploaded to GCLoud')
    else:
        print('Video annotations (.csv) already stored in GCloud') 


    # 7) PROCESS ANNOTATIONS

    if not os.path.isfile(str(path_model_data)):
        print('Creating data (.csv) for model training...')
        data = create_data(annotations_df, NUM_FRAMES)
        data = populate_data(data)
        print('Saving data (.csv) for model training...')
        data.to_csv(path_model_data)
    else:
        print('Data for model training already generated and stored in disk')
        data = pd.read_csv(str(path_model_data))

    blob_model_data = f'videos_files/{video_category}/{video_title}/data.csv'
    if not is_stored(blob_model_data, bucket_name):
        fileType = 'text/csv'
        upload_file_to_gstore(bucket_name, str(path_model_data), blob_model_data, fileType, chunk_size)
        print('Data for model training (.csv) uploaded to GCLoud')
    else:
        print('Data for model training (.csv) already stored in GCloud') 

    # 8) UPLOAD ZIP WITH FRAMES
    if not os.path.isfile(str(pathIn_Frames_zip)):
        print('Compressing frames (.zip) for model training...')
        # Comprimo frames_resized folder into frames.zip
        zip_dir(pathIn_Frames_Resized, pathIn_Frames_zip)
        print('Saving frames compressed data (.zip) for model training...')
    else:
        print('Compressed frames (.zip) for model training already generated and stored in disk')


    blob_path_frames = f'videos_files/{video_category}/{video_title}/frames.zip'
    if not is_stored(blob_path_frames, bucket_name):
        fileType = 'application/x-zip-compressed'
        upload_file_to_gstore(bucket_name, str(pathIn_Frames_zip), blob_path_frames, fileType, chunk_size)
        print('Compressed frames (.zip) uploaded to GCLoud')
    else:
        print('Compressed frames (.zip) already stored in GCloud') 