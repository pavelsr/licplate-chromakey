import io
import os
import requests
import gradio as gr
from PIL import ImageDraw, ImageFont

def create_error_image(input_image, error_message):
    """
    Creates an error image with the specified error message drawn on it.
    
    Args:
        input_image: Original input PIL.Image.
        error_message: Error message to be displayed.
    
    Returns:
        PIL.Image instance with the error message.
    """
    # Create a copy of the input image to draw the error message
    error_image = input_image.copy()
    draw = ImageDraw.Draw(error_image)
    
    # Load a TrueType font with the desired size
    try:
        font = ImageFont.truetype("arial.ttf", 24)  # Replace with your font and size
    except IOError:
        # Fallback to default font if arial is not available
        font = ImageFont.load_default()
    
    # Define text position
    text_position = (10, 10)  # Top-left corner
    
    # Calculate text size using textbbox (instead of textsize)
    bbox = draw.textbbox((0, 0), error_message, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw a translucent rectangle as a background for the text
    rectangle_position = (
        text_position[0] - 5,
        text_position[1] - 5,
        text_position[0] + text_width + 10,
        text_position[1] + text_height + 10
    )
    draw.rectangle(rectangle_position, fill="red")
    
    # Draw the error message
    draw.text(text_position, error_message, fill="white", font=font)
    return error_image


def process_image(input_image, min_confidence):
    """
    This function takes an input image and returns it as the output image.
    Args:
        input_image: Input image as a PIL.Image instance.
    Returns:
        PIL.Image instance (the same as input).
    """
    try:
        image_buffer = io.BytesIO()
        input_image.save(image_buffer, format="JPEG")
        image_buffer.seek(0)
        files = {
            'image': ('image.jpg', image_buffer, 'image/jpeg')
        }
        url = os.getenv("YOLO_LICPLATE_ENDPOINT", "http://localhost:32168/v1/vision/custom/license-plate")
        response = requests.post(url, files=files, data={ 'min_confidence': min_confidence })

        if response.status_code != 200:
            error_message = f"Error: Received status code {response.status_code} from the YOLO_LICPLATE server."
            return create_error_image(input_image, error_message)


        response_data = response.json()

        if "predictions" not in response_data or not response_data["predictions"]:
            error_message = "Error: No predictions found in the response."
            return create_error_image(input_image, error_message)
        
        bbox = response_data["predictions"][0]
        draw = ImageDraw.Draw(input_image)
        draw.rectangle( [bbox['x_min'], bbox['y_min'], bbox['x_max'], bbox['y_max']], fill="green")
        return input_image
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return create_error_image(input_image, error_message)

# Create a Gradio interface
interface = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Image(type="pil"),
        gr.Slider(0, 1, step=0.01, value=0.4, label="Minimum Confidence")
    ],
    outputs=gr.Image(type="pil"),
    title="Licence Plate Area Processor",
    description="Upload an image, and get the result near. Must return chromakey of licence plate area"
)

# Launch the Gradio app
if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860, share=True, debug=True)
