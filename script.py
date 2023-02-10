import requests
import time
import replicate
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

# Add your Twitter API credentials
access_token = os.getenv("TWITTER_TOKEN")
access_token_secret = os.getenv("TWITTER_TOKEN_SECRET")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)


def post_image():
    # Get the current epoch time
    current_epoch = int(time.time())

    # Define the API endpoint and the parameters for the request
    model = replicate.models.get("stability-ai/stable-diffusion")
    version = model.versions.get(
        "f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2dc5dd04895e042863f1")

    inputs = {
        # Input prompt
        'prompt': str(current_epoch),

        # Specify things to not see in the output
        # 'negative_prompt': ...,

        # Width of output image. Maximum size is 1024x768 or 768x1024 because
        # of memory limits
        'width': 1024,

        # Height of output image. Maximum size is 1024x768 or 768x1024 because
        # of memory limits
        'height': 768,

        # Prompt strength when using init image. 1.0 corresponds to full
        # destruction of information in init image
        'prompt_strength': 0.8,

        # Number of images to output.
        # Range: 1 to 4
        'num_outputs': 1,

        # Number of denoising steps
        # Range: 1 to 500
        'num_inference_steps': 50,

        # Scale for classifier-free guidance
        # Range: 1 to 20
        'guidance_scale': 7.5,

        # Choose a scheduler.
        'scheduler': "DPMSolverMultistep",
    }

    # Get the generated image URL
    image_url = version.predict(**inputs)[0]

    # Download the image
    response = requests.get(
        image_url)
    open(f"image{current_epoch}.jpg", "wb").write(response.content)

    # Post the image to Twitter
    with open(f"image{current_epoch}.jpg", "rb") as image:
        media_response = api.media_upload(filename=f"image{current_epoch}.jpg")
        print(media_response)
        status = api.update_status_with_media(
            status="Generated image using replicate.com's stable-diffusion API #imagegeneration #AI", filename=f"image{current_epoch}.jpg", file=image)


post_image()
