# pip install opencv-python
# pip install pyautogui
# pip install pySmartDL
# pip install colorama
# pip install selenium


import os
import cv2
import pyautogui
import time
from pySmartDL import SmartDL
from urllib.error import URLError
from pySmartDL import SmartDL
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions

num_frames = 5 # Frames extracted per video
DOWNLOAD_FOLDER = "F:\\AI Project\\data\\videos"
DOWNLOAD_FOLDER_DNxHQ = "F:\\AI Project\\data\\videos\\DNxHQ"
DOWNLOAD_FOLDER_H264 = "F:\\AI Project\\data\\videos\\H264"
LOGIN_URL = "https://www.filmhero.com/account#/"
EMAIL = "seltopyt@gmail.com"

driver = webdriver.Chrome()

def login():
    driver.get(LOGIN_URL)
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "uemail"))
    )
    email_field.send_keys(EMAIL)
    login_button = driver.find_element(By.ID, "formbtn")
    login_button.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "passcode"))
    )
    
    time.sleep(20)

    # passcode = ask_passcode()
    # passcode_field = driver.find_element(By.ID, "passcode")
    # passcode_field.send_keys(passcode)
    # sign_in_button = driver.find_element(By.ID, "formbtn")
    # sign_in_button.click()

def ask_passcode():
    user_input = input("Please enter the passcode: ")
    return user_input

def video_menu():
    login()
    time.sleep(1)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "img.header_logo"))
    ).click()

    driver.maximize_window()
    
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Browse Packs"))
    ).click()
    
def wait_for_pack_to_load(pack):
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "gallery_item"))
    )

def get_folder_size():
    total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                     for dirpath, dirnames, filenames in os.walk(DOWNLOAD_FOLDER)
                     for filename in filenames)
    return total_size

def download_clip(download_path, link_url, filename, max_retries=10, retry_delay=5):
    full_path = os.path.join(download_path, filename)
    attempt = 0

    while attempt < max_retries:
        try:
            obj = SmartDL(link_url, full_path)
            obj.start()
            if obj.isFinished():
                print(f"Downloaded '{filename}' to '{download_path}'")
                if 'H264' in filename:
                    print("Finished downloading pair")
                return
            else:
                print(f"Failed to download file from '{link_url}'.")
                for e in obj.get_errors():
                    print(e)
                attempt += 1
        except (URLError, TimeoutError) as e:
            print(f"Attempt {attempt + 1} failed with error: {e}. Retrying after {retry_delay} seconds...")
            time.sleep(retry_delay)
            attempt += 1

    print(f"Failed to download '{filename}' after {max_retries} attempts.")

def element_hover(element):
    element_location = element.location
    element_size = element.size
    browser_position = driver.get_window_rect()
    element_center_x = browser_position['x'] + element_location['x'] + element_size['width'] / 2
    element_center_y = browser_position['y'] + element_location['y'] + element_size['height'] / 2
    pyautogui.moveTo(element_center_x, element_center_y)

def check_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False  # Video can't be opened
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = total_frames // (num_frames + 1)
    for i in range(1, num_frames + 1):
        frame_number = i * frame_interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, _ = cap.read()
        if not ret:
            return False  # Failed to read frame
    return True  # All frames read successfully

def pre_filter(videos_dir_dnqh, videos_dir_h264):
    dnqh_files = os.listdir(videos_dir_dnqh)
    h264_files = os.listdir(videos_dir_h264)

    # Mapping for easier cross-format comparison
    h264_to_dnqh = {f.replace("H264", "DNxHQ"): f for f in h264_files}
    dnqh_to_h264 = {f.replace("DNxHQ", "H264"): f for f in dnqh_files}
    

    # Check DNxHQ files for H264 counterparts and frame integrity
    for dnqh_file in list(dnqh_files):  # Use list to clone because we're modifying the dict
        h264_file = dnqh_file.replace("DNxHQ", "H264")
        if h264_file in dnqh_to_h264:
            # Both files exist, now check frames
            dnqh_path = os.path.join(videos_dir_dnqh, dnqh_file)
            h264_path = os.path.join(videos_dir_h264, h264_file)

            if not (check_video_frames(dnqh_path) and check_video_frames(h264_path)):
                # If frame check fails for either, delete both
                try:
                    os.remove(dnqh_path)
                    os.remove(h264_path)
                    print(Fore.RED + f"Deleted {dnqh_file} and its H264 counterpart due to frame issues.")
                except:
                    try:
                        os.remove(h264_path)
                        print(Fore.RED + f"Deleted {h264_file} due to frame issues.")
                    except Exception as e:
                        pass
        else:
            # H264 counterpart missing, delete DNxHQ file
            os.remove(os.path.join(videos_dir_dnqh, dnqh_file))
            print(Fore.YELLOW + f"Deleted {dnqh_file} from DNxHQ directory; counterpart missing in H264 directory.")

    # Repeat the process for H264 files, checking against DNxHQ counterparts
    for h264_file in list(h264_files):  # Use list to clone because we're modifying the dict
        dnhq_file = h264_file.replace("H264", "DNxHQ")
        if h264_file == dnqh_to_h264.get(dnhq_file):
            # DNxHQ counterpart missing, delete H264 file
            os.remove(os.path.join(videos_dir_h264, h264_file))
            print(Fore.YELLOW + f"Deleted {h264_file} from H264 directory; counterpart missing in DNxHQ directory.")
        else:
            try:
                dnqh_files.remove(dnhq_file)
                print(Fore.YELLOW + "removed")
            except:
                pass
    for dnhq_file in dnqh_files:
        try:
            os.remove(os.path.join(videos_dir_dnqh, dnhq_file))
        except:
            pass
        
def export_frames(videos_dir, output_dir):
    files = os.listdir(videos_dir) # Grab all files from videos dir

    total_frames_processed = 0 # Total frames exported counter
    # Iterate over each video
    for video_file in files:
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

def frame_to_1080p(source_folder, destination_folder):
    # List all files in the source folder
    files = os.listdir(source_folder)
    for file in files:
        src_path = os.path.join(source_folder, file) # Construct the full path to the source frame
        frame = cv2.imread(src_path) # Read the frame
        # Check if the frame was successfully read
        if frame is None:
            print(f"Failed to read {file}. Skipping...")
            continue
        resized_frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_AREA) # Resize the frame to 1080p
        dest_path = os.path.join(destination_folder, file) # Construct the full path to the destination of the resized frame
        # Save the resized frame
        cv2.imwrite(dest_path, resized_frame)
        print(f"Resized and saved {file} to {destination_folder}.")

def remove_useless_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):  # Make sure it's a file
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def process_gallery():
    video_menu()
    last_page = False


    while get_folder_size() <= 1 * 1024**4 and not last_page:  # 1TB in bytes
        # wait packs_list
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "searchresults"))
        )
        packs_list = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults > li.gallery_item")
        last_page = True
        # iterate over packs_list
        packs = len(packs_list)

        for i in range(packs):
            packs_list = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults > li.gallery_item")
            pack = packs_list[i]
            wait_for_pack_to_load(pack)
            
            # Check if the current li is not the "Show More" button by looking for the specific img tag
            if not pack.find_elements(By.CSS_SELECTOR, "img#showmore"):
                ActionChains(driver).key_down(Keys.CONTROL).click(pack).key_up(Keys.CONTROL).perform()  # Clicking on a gallery item to navigate to its detail page
                driver.switch_to.window(driver.window_handles[1])
                # wait for clips_list
                time.sleep(1)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.gallery")))
                clips_list = driver.find_elements(By.CSS_SELECTOR, "ul.gallery > li")

                package_title = driver.find_element(By.CSS_SELECTOR, "h1.packhead_title").text
                # iterate over clips_list
                for clip_index, clip in enumerate(clips_list, start=1):
                    download_span = driver.find_element(By.CLASS_NAME, "plan_downloads")
                    ActionChains(driver).move_to_element(clip).perform()
                    element_hover(clip)
                    
                    dnx_link_element = clip.find_element(By.XPATH, ".//a[contains(text(), 'DNx')]")
                    dnx_link = dnx_link_element.get_attribute('href')
                    dnx_filename = base_filename = f"{package_title}_DNxHQ_{clip_index}.mov"
                    dnx_filename = dnx_filename.replace(" ", "_")
                    download_clip(DOWNLOAD_FOLDER_DNxHQ, dnx_link, dnx_filename)

                    h264_link_element = clip.find_element(By.XPATH, ".//a[contains(text(), 'H264')]")
                    h264_link = h264_link_element.get_attribute('href')
                    h264_filename = base_filename = f"{package_title}_H264_{clip_index}.mov"
                    h264_filename = h264_filename.replace(" ", "_")
                    download_clip(DOWNLOAD_FOLDER_H264, h264_link, h264_filename)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                # Return to the list of gallery items
            else:
                last_page = False
                pack.click()  # Click the "Show More" button
                break  # Exit the loop to allow page to refresh and load more items

        pre_filter(DOWNLOAD_FOLDER_DNxHQ, DOWNLOAD_FOLDER_H264)

        print("exporting frames for DNxHQ")
        export_frames(DOWNLOAD_FOLDER_DNxHQ, r"F:\AI Project\data\videos\frames\4k\DNxHQ_frames_4k") # takes only a few frames, deletes corrupt videos.
        print("resizing DNxHQ frames")
        frame_to_1080p(r"F:\AI Project\data\videos\frames\4k\DNxHQ_frames_4k", r"F:\AI Project\data\videos\frames\1080p\DNxHQ_frames_1080p")
        print("deleting remains")
        remove_useless_files(DOWNLOAD_FOLDER_DNxHQ)
        remove_useless_files(r"F:\AI Project\data\videos\frames\4k\DNxHQ_frames_4k")

        print("exporting frames for H264")
        export_frames(DOWNLOAD_FOLDER_H264, r"F:\AI Project\data\videos\frames\4k\H264_frames_4k") # takes only a few frames, deletes corrupt videos..
        print("resizing H264 frames")
        frame_to_1080p(r"F:\AI Project\data\videos\frames\4k\H264_frames_4k", r"F:\AI Project\data\videos\frames\1080p\H264_frames_1080p")
        print("deleting remains")
        remove_useless_files(DOWNLOAD_FOLDER_H264)
        remove_useless_files(r"F:\AI Project\data\videos\frames\4k\H264_frames_4k")
        print("finished both DNxHQ and H264, starting next cycle")

    input("Press Enter to close the browser and exit the script...")


# Example usage
if __name__ == "__main__":
    process_gallery()
