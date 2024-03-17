import os
import cv2
from colorama import init, Fore

num_frames = 3 # Frames extracted per video
videos_dir = r"F:\AI Project\test\footage" # Videos dir
output_dir = r"F:\AI Project\test\frames" # Frames dir
files = os.listdir(videos_dir) # Grab all files from videos dir
video_files = [f for f in files if f.endswith('.mp4')] # Filter only .mp4 files
total_frames_processed = 0 # Total frames exported counter

# Iterate over each video
for video_file in video_files:
    video_path = os.path.join(videos_dir, video_file)
    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Get total num of frames in video

    frame_interval = total_frames // (num_frames + 1) # Calculate which frames to extract (see "css flex spaced evently" for a visual example)


    # Extract and save frames
    for i in range(1, num_frames + 1):
        frame_number = i * frame_interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        total_frames_processed += 1

        # Save frame to output dir
        frame_filename = f'{video_file[:-4]}_f{i}_i{total_frames_processed}.jpg'
        frame_path = os.path.join(output_dir, frame_filename)
        cv2.imwrite(frame_path, frame)

    cap.release()
    print(Fore.GREEN + f"Processed {video_file}. Frames extracted and saved to {output_dir}" + Fore.RESET)

print(Fore.MAGENTA + "All videos processed." + Fore.RESET)
