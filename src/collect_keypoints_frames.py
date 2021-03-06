"""
record 50 mini videos for each sign
extract keypoints coordinates in real-world meters and store as .npy files
"""
import cv2
import mediapipe as mp
import numpy as np
import os
from modules.feed_connections import detect_video, draw_landmarks
from modules.keypoints import pose_hand_keypoints # self-defined module to extract keypoints coordinates


# Base path to store keypoints coordinates/frame images
base_path_keypoints = os.path.join('data', 'keypoints', 'pose_hands') 
base_path_frames = os.path.join('data', 'frames') 
       
# signs to detect
signs = np.array(['Take care']) # change as needed 'A', 'busy', 'cat', 'D', 'excited', 'finish', 'Hello', 'How', 'I', 'I_me', 'love', 'my', 'name', 'nothing', 'S', 'sign'

# number of videos for one sign, number of frames in one video
n_videos, n_frames = 50, 30

start_video = 0 # for adding more videos on top of existing videos
                 # change the value as needed
# make empty folders to store data
for sign in signs: 
    for video_i in range(n_videos):
        try: 
            os.makedirs(os.path.join(base_path_keypoints, sign, str(start_video + video_i)))
            os.makedirs(os.path.join(base_path_frames, sign, str(start_video + video_i)))
        except:
            pass
        
# demovideo_path = os.path.join(base_path, 'demovideo')

# make an empty folder to store frames of 'Hello' video 1 only for project presentation visualization purpose
# try:
#     os.makedirs(demovideo_path) 
# except:
#     pass

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture video feed from camera '0', webcam on my machine
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)   # set up resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

mp_pose = mp.solutions.pose # pose model
mp_hands = mp.solutions.hands # Hand model
# Set mediapipe model 
hands = mp_hands.Hands(model_complexity=0,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
pose = mp_pose.Pose(min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)
# Loop through signs
for sign in signs:
    # Loop through videos in each sign
    for video_i in range(n_videos):
        # Loop through video frames in each video
        for frame_i in range(n_frames+1): # plus 1 to make the first frame as recording preperation

            # Read feed
            ret, frame = cap.read() # ret is a boolean variable that returns true if the frame is available.
                                    # frame is an image array vector captured

            # detect video feed
            image, res_pose = detect_video(frame, pose)
            image, res_hands = detect_video(image, hands)

            # Draw keypoints and connection landmarks
            draw_landmarks(image, res_pose, res_hands)

            # add break in between recordings
            if frame_i == 0: # beginning of each video
                cv2.putText(image, 'START COLLECTING', (120,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
                cv2.putText(image, 'Collecting frames for {}, Video Number {}'.format(sign, video_i), (15,12), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                # Show to screen
                cv2.imshow('OpenCV Feed', image)
                cv2.waitKey(2000)
            else: 
                cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(sign, video_i), (15,12), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                # Show to screen
                cv2.imshow('OpenCV Feed', image)
                
                # export keypoints
                keypoints = pose_hand_keypoints(res_pose, res_hands)
                keypoints_path = os.path.join(base_path_keypoints, sign, str(start_video + video_i), str(frame_i))
                frames_path = os.path.join(base_path_frames, sign, str(start_video + video_i), f'{frame_i}.jpg')
                
                np.save(keypoints_path, keypoints)
                cv2.imwrite(frames_path, frame)

            # export frames (for project presentation visualization purpose, not necessary if just for exercise)
            # if (sign == 'Hello') and (video_i == 0):
            #     cv2.imwrite(demovideo_path, image)

            # Break out live video with key 'q' 
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # add break before record next sign
    if video_i == 49:
        cv2.waitKey(10000) # break for 10 sec

cap.release()
cv2.destroyAllWindows()