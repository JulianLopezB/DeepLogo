import pandas as pd
import argparse
from src.utils import concatenate_anno
import pickle

# ARGS 

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--category", type=str,
                    help="Video category (example: F1, Tennis, Futbol)")

args = parser.parse_args()

video_category = args.category

output_file = f'./data/video-files/{video_category}/{video_category}.csv'

#outfile = open(output_file, "wb")
df = concatenate_anno('./data/video-files/', video_category).reset_index(drop=True)
#pickle.dump(df, outfile)
#outfile.close()

df.to_csv(output_file)
#df.to_json(output_file)
