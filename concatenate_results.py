import pandas as pd
import argparse
from src.utils import concatenate_anno

# ARGS 

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--category", type=str,
                    help="Video category (example: F1, Tennis, Futbol)")

args = parser.parse_args()

video_category = args.category

output_file = f'{video_category}.csv'

df = concatenate_anno('.data/video-files/', video_category)
df.to_csv(output_file)