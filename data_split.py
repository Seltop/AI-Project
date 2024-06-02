import os
import shutil
import random
from tqdm import tqdm

def move_files(src_dir_X, src_dir_Y, dest_dir_X, dest_dir_Y, test_ratio=0.1):
    # Get list of files in both directories
    files_X = set(os.listdir(src_dir_X))
    files_Y = set(os.listdir(src_dir_Y))

    # Ensure the files match by name
    common_files = list(files_X.intersection(files_Y))

    # Determine the number of files to move
    num_files_to_move = int(len(common_files) * test_ratio)

    # Randomly select files to move
    files_to_move = random.sample(common_files, num_files_to_move)

    # Ensure destination directories exist
    os.makedirs(dest_dir_X, exist_ok=True)
    os.makedirs(dest_dir_Y, exist_ok=True)

    # Move the files
    for file_name in tqdm(files_to_move, desc="Moving files"):
        src_path_X = os.path.join(src_dir_X, file_name)
        dest_path_X = os.path.join(dest_dir_X, file_name)
        shutil.move(src_path_X, dest_path_X)

        src_path_Y = os.path.join(src_dir_Y, file_name)
        dest_path_Y = os.path.join(dest_dir_Y, file_name)
        shutil.move(src_path_Y, dest_path_Y)

    print(f"Moved {num_files_to_move} files to {dest_dir_X} and {dest_dir_Y}")

# Specify your directories
src_dir_X = "F:/AI Project/data/videos/frames/1080p/DNxHQ_frames_1080p"
src_dir_Y = "F:/AI Project/data/videos/frames/1080p/H264_frames_1080p"
dest_dir_X = "F:/AI Project/data/test/DNxHQ"
dest_dir_Y = "F:/AI Project/data/test/H264"

# Move 10% of files from both directories to the test directories
move_files(src_dir_X, src_dir_Y, dest_dir_X, dest_dir_Y, test_ratio=0.1)