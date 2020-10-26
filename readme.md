## Welcome to DeepLogo.ai ©

An early stage project to track brand logos in images and videos across the web. Measure brand visibility in social networks context and search the web for marketing highlights and brand safety. Companies spend millions of dollars to track brand mentions but they ignore one powerful part of the message: the image. 

DeepLogo.ai uses computer vision technologies and advanced AI algorithms to detect logos in images and videos and to automate visual content discovery in social media.
 
<p float="center">
  <img src="static/a9231fbb-0272-40c9-8178-66e883d83813.jpeg" width="33%" />
  <img src="static/b61426dc-dc89-4ab7-9496-7264f490c088.jpeg" width="33%" /> 
  <img src="static/375f3a12-b4cb-4656-a360-1e4ce982a9ba.jpeg" width="33%" />
</p>

The initial project consists of 3 steps:

- A) Build an ETL pipeline to fetch annotated data from a YouTube's video using Google's VideoIntelligence API
- B) Use this data to train a deep neural network
- C) Deploy and serve the model as a RESTful API (Model as a Service)

## A) ETL Pipeline to get annotated data from a YouTube's video using Video Intelligence API

### What it does?
- 1) Download video from YouTube's url
- 2) Upload video to GCloud Storage
- 3) Get video annotations of YouTube's video from VideoIntellige API
- 4) Get frames from video and saves it locally
- 5) Process annotations and frames and prepares data for model training
- 6) Upload processed frames and annotations for model training to GCloud Storage

### Usage

`$ pip install -r requirements.txt`  
`$ python pipeline.py -u $VIDEO_URL -c $VIDEO_CATEGORY`

Example
`$ python pipeline.py -u https://www.youtube.com/watch?v=TB5yhZdF8SI -c F1`


### Output
- Video file (.mp4 or .mkv)
- Raw results from VideoIntelligence API (.json)
- Annotations with raw results (.csv)

For model training:
- Procesed Frames (.zip with .jpgs)
- Processed annotations (.csv)


## B) Training a Model
See https://medium.com/swlh/how-to-leverage-gcp-free-tier-to-train-your-custom-object-detection-with-yolov5-c0dde7a3c189
