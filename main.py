import cv2
import os
from transformers import pipeline
from PIL import Image

output_directory = "/content/video"
os.makedirs(output_directory, exist_ok=True)

def extract_frames(video_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(output_folder, f'frame_{frame_idx:04d}.png')
        cv2.imwrite(frame_path, frame)
        frame_idx += 1
    cap.release()

def upscale_frame(frame_path, output_path, pipe):
    """Upscales a single frame using Stable Diffusion."""
    frame = Image.open(frame_path).convert("RGB")
    upscaled_frame = pipe(image=frame, height=720, width=1280).images[0]
    upscaled_frame.save(output_path)


def frames_to_video(frames_folder, output_video_path):
    frame_files = sorted([os.path.join(frames_folder, f) for f in os.listdir(frames_folder) if f.endswith('.png')])
    frame = cv2.imread(frame_files[0])
    height, width, layers = frame.shape
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))
    for frame_file in frame_files:
        video.write(cv2.imread(frame_file))
    video.release()

video_path = '/content/sd_video.mp4'
frames_folder = '/content/frames'
upscaled_frames_folder = '/content/upscaled_frames'
output_video_path = os.path.join(output_directory, "hd_video.mp4")

extract_frames(video_path, frames_folder)

from diffusers import StableDiffusionPipeline
import torch

model_id = "CompVis/stable-diffusion-v1-4"
api_token = "hf_gjaWoENmSJRXGXqGWCuBaMsXtt......"    # use you api key from hogging face
pipe = StableDiffusionPipeline.from_pretrained(model_id, variant="fp16", torch_dtype=torch.float16, token=api_token, force_reload=True)

os.makedirs(upscaled_frames_folder, exist_ok=True)
for frame_file in os.listdir(frames_folder):
    frame_path = os.path.join(frames_folder, frame_file)
    output_path = os.path.join(upscaled_frames_folder, frame_file)
    upscale_frame(frame_path, output_path, pipe)

frames_to_video(upscaled_frames_folder, output_video_path)
