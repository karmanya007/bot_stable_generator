import requests
import time
import twitter
import replicate

# Add your Twitter API credentials
bearer_token = "${{ secrets.TWITTER_BEARER_TOKEN }}"

# Authenticate with Twitter API v2
client = twitter.Client(bearer_token=bearer_token)

def post_image():
    # Get the current epoch time
    current_epoch = int(time.time())

    # Define the API endpoint and the parameters for the request
    model = replicate.models.get("stability-ai/stable-diffusion")
    version = model.versions.get("f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2dc5dd04895e042863f1")

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
    image_url = version.predict(inputs)[0]

    # Download the image
    response = requests.get(image_url)
    open(f"image{current_epoch}.jpg", "wb").write(response.content)

    # Post the image to Twitter
    with open(f"image{current_epoch}.jpg", "rb") as image:
        media_response = client.media.upload(media=image)
        media_id = media_response["media_id"]
        tweet = client.status.update(status="Generated image using replicate.com's stable-diffusion API #imagegeneration #AI", media_ids=[media_id])

post_image()
