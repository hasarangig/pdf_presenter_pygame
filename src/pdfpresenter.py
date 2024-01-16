import pygame
import os
from sys import exit
from pdf2image import convert_from_path
import cv2
import numpy as np
from typing import List, Callable
import pygame
import pygame.locals as pl


# Set the window dimensions
window_width = 600
window_height = 800

running = True
darken_blur_effect = False
normal_surface = None
selecting = False
start_pos = None
end_pos = None
highlight_rect = None
fullscreen = False
enable_highlight = False  

# Initialize your fade-in variables
fade_in_alpha = 255 
fade_in_speed = 2

# Create the Pygame window
window = pygame.display.set_mode((window_width, window_height))

pygame.init()
pygame.display.set_caption('PDF Presenter')
clock = pygame.time.Clock()

user_text= ' '
font = pygame.font.SysFont('Arial',24) 
input_rect = pygame.Rect(200,200,140,40)
active=False
color_ac=pygame.Color(255, 255, 255, 128) 
color_pc=pygame.Color('red')
color=color_pc

# Dictionary to store text boxes for each page
text_boxes_by_page = {}

# Get the path to the PDF file
pdf_path = os.path.join(os.path.dirname(__file__), "../inputs/sample.pdf")

# Convert the PDF to images
images = convert_from_path(pdf_path)

# Create a folder to store the images (if it doesn't exist)
image_folder = os.path.join(os.path.dirname(__file__), "../outputs/output_images")
os.makedirs(image_folder, exist_ok=True)

# Save the converted images to the specified folder
for i, image in enumerate(images):
    image_path = os.path.join(image_folder, f'image_{i+1}.jpg')
    image.save(image_path, 'JPEG')
    print(f'Saved image {i+1} to {image_path}')

# Get the list of image files in the folder
image_files = os.listdir(image_folder)


# Load the first image from the folder
current_image_index = 0
if len(image_files) > 0:
    current_image_path = os.path.join(image_folder, image_files[current_image_index])
    image = pygame.image.load(current_image_path)
    image = pygame.transform.scale(image, (window_width, window_height))  
    original_image = image.copy() 


# Store the original image
original_image = image.copy()

# Function to reset the image to its original state
def reset_image():
    global image, normal_surface, darken_blur_effect
    image = original_image.copy()
    normal_surface = None
    darken_blur_effect = False

# Variables for zoomed-in view
zoomed = False
zoomed_rect = None
#zoomed factor and zoomed rectangle position variables
zoom_factor = 2.5
zoomed_x = None
zoomed_y = None
zoomed_offset_x = 0
zoomed_offset_y = 0

def load_new_image(image_path):
    global image, original_image, fade_in_alpha

    # Set the fade alpha to 0 to start a fade-in effect
    fade_in_alpha = 0

    # Load the new image
    new_image = pygame.image.load(image_path)
    new_image = pygame.transform.scale(new_image, (window_width, window_height))

    # Store the original image
    original_image = new_image.copy()

    # Set the final image with full alpha
    new_image.set_alpha(255)
    image = new_image.copy()

# New function for applying fade-in effect
def apply_fade_in_effect():
    global fade_in_alpha

    if fade_in_alpha < 255:
        fade_in_alpha += fade_in_speed
        image.set_alpha(fade_in_alpha)


# Function to handle zoom in
def zoom_in():
    global zoomed_rect, zoomed_offset_x, zoomed_offset_y
    if highlight_rect is not None:
        # Calculate the new width and height based on the zoom factor
        new_width = int(highlight_rect.width * zoom_factor)
        new_height = int(highlight_rect.height * zoom_factor)

        # Calculate the position to display the zoomed area at the center of the screen
        zoomed_x = (window_width - new_width) // 2
        zoomed_y = (window_height - new_height) // 2

        # Create a new zoomed rectangle
        zoomed_rect = pygame.Rect(
            highlight_rect.left - zoomed_offset_x,
            highlight_rect.top - zoomed_offset_y,
            new_width,
            new_height
        )

# Function to handle zoom out
def zoom_out():
    global zoomed_rect, zoomed_offset_x, zoomed_offset_y
    zoomed_rect = None
    zoomed_offset_x = 0
    zoomed_offset_y = 0

# Function to handle mouse movement
def handle_mouse_movement():
    global zoomed_offset_x, zoomed_offset_y
    if zoomed_rect is not None:
        # Calculate the maximum offset based on the zoomed rectangle size and screen size
        max_offset_x = max(zoomed_rect.width - window_width, 0)
        max_offset_y = max(zoomed_rect.height - window_height, 0)

        # Update the zoomed offset based on the cursor movement
        zoomed_offset_x += pygame.mouse.get_rel()[0]
        zoomed_offset_y += pygame.mouse.get_rel()[1]

        # Clamp the zoomed offset to keep it within the maximum range
        zoomed_offset_x = max(min(zoomed_offset_x, max_offset_x), 0)
        zoomed_offset_y = max(min(zoomed_offset_y, max_offset_y), 0)


# Function to handle going to the previous image
def go_to_previous_image():
    global current_image_index, image, user_text, text_boxes_by_page
    if current_image_index > 0:
        user_text = ''
        text_boxes_by_page[current_image_index] = []  # Clear text boxes for current page
        current_image_index -= 1
        current_image_path = os.path.join(image_folder, image_files[current_image_index])
        image = pygame.image.load(current_image_path)
        image = pygame.transform.scale(image, (window_width, window_height)) 
        load_new_image(current_image_path)  
        apply_fade_in_effect()  # Apply fade-in effect


# Function to handle going to the next image
def go_to_next_image():
    global current_image_index, image, user_text, text_boxes_by_page
    if current_image_index < len(image_files) - 1:
        user_text = ''
        text_boxes_by_page[current_image_index] = []  # Clear text boxes for current page
        current_image_index += 1
        current_image_path = os.path.join(image_folder, image_files[current_image_index])
        image = pygame.image.load(current_image_path)
        image = pygame.transform.scale(image, (window_width, window_height)) 
        load_new_image(current_image_path) 
        apply_fade_in_effect()  # Apply fade-in effect



# Function to handle keyboard events
def handle_keyboard_event(event):
    global darken_blur_effect, esc_clicked,highlight_rect, selecting, fullscreen
    if event.key == pygame.K_KP_PLUS or event.key == pygame.K_PLUS:  # '+' key pressed
        zoom_in()
    elif event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS:  # '-' key pressed
        zoom_out()
    elif event.key == pygame.K_LEFT:  # '<' key pressed
        go_to_previous_image()
    elif event.key == pygame.K_RIGHT:  # '>' key pressed
        go_to_next_image()
    elif event.key == pygame.K_PERIOD or event.key == pygame.K_PERIOD:  # '.' key pressed
        highlight_rect = None 
        darken_blur_effect = False 
        reset_image()  
 
    
t_key_pressed = False
adding_text = False  # New variable to track adding text to rectangle

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                if esc_clicked: 
                    highlight_rect = None
                    darken_blur_effect = False
                    esc_clicked = False  
            elif event.key == pygame.K_h:  # 'H' key pressed to enable/disable highlight
                enable_highlight = not enable_highlight
            elif event.key == pygame.K_RETURN:  # Enter key pressed
                if fullscreen:
                    pygame.display.set_mode((window_width, window_height))
                else:
                    pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
                fullscreen = not fullscreen
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                start_pos = pygame.mouse.get_pos()
                selecting = True
                input_rect.collidepoint(event.pos)
                active = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  # '<' key pressed
                go_to_previous_image()
            elif event.key == pygame.K_RIGHT:  # '>' key pressed
                go_to_next_image()
            elif event.key == pygame.K_KP_PLUS or event.key == pygame.K_PLUS:  # '+' key pressed
                zoom_in()
            elif event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS:  # '-' key pressed
                zoom_out()
            elif event.key == pygame.K_t:  # 'T' key pressed to add a sticky note
                t_key_pressed = True
                selecting = False  # Set selecting to False to allow drawing a rectangle after adding a sticky 
                adding_text = True  # Set adding_text to True when 'T' key is pressed
                #active = True  # Set active to True for text input
            elif active == True:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text+=event.unicode
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  
                selecting = False
                end_pos = pygame.mouse.get_pos()
                highlight_rect = pygame.Rect(start_pos[0], start_pos[1], end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
                darken_blur_effect = True  
            else:
                highlight_rect = None
                darken_blur_effect = False 
                reset_image()
        
    
    
        
    handle_mouse_movement()

    # Handle fade-in effect if active
    if fade_in_alpha < 255:
        fade_in_alpha += fade_in_speed
        image.set_alpha(fade_in_alpha)
    
    # Clear the window
    window.fill((255, 255, 255))

    # Blit the image onto the window
    window.blit(image, (0, 0))


    if active:
      color=color_ac
    else:
      color=color_pc

    # Render the text input rectangle and text when the 'T' key is pressed
    if t_key_pressed:
        text_surface = font.render(user_text, True, (0, 0, 255))
        input_rect = pygame.Rect(10, 10, max(140, text_surface.get_width() + 20), 40)  # Update the input_rect size
        pygame.draw.rect(window, color, input_rect, 1)
        window.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        input_rect.w = max(100, text_surface.get_width() + 10)
        adding_text = True 
        # After rendering the text, store the text box in the dictionary and rendering the text boxes for the current page
        if current_image_index in text_boxes_by_page:
            for text_box in text_boxes_by_page[current_image_index]:
                if text_box['text'].strip():  # Only render if there's actual text
                    pygame.draw.rect(window, color, text_box['rect'], 1)
                    text_surface = font.render(text_box['text'], True, (0, 0, 0))
                    window.blit(text_surface, (text_box['rect'].x + 5, text_box['rect'].y + 5))
    else:
        if adding_text:  # Only reset adding_text and t_key_pressed if they were True
            adding_text = False
            t_key_pressed = False

        # Render the text boxes for the current page
        if current_image_index in text_boxes_by_page:
            for text_box in text_boxes_by_page[current_image_index]:
                if text_box['text'].strip():  # Only render if there's actual text
                    pygame.draw.rect(window, color, text_box['rect'], 1)
                    text_surface = font.render(text_box['text'], True, (0, 0, 0))
                    window.blit(text_surface, (text_box['rect'].x + 5, text_box['rect'].y + 5))
    

     # Draw the highlighted area
    if selecting:
        pygame.draw.rect(window, (255, 0, 0),
                         (start_pos[0], start_pos[1], pygame.mouse.get_pos()[0] - start_pos[0],
                          pygame.mouse.get_pos()[1] - start_pos[1]), 2)
    elif highlight_rect is not None:
        pygame.draw.rect(window, (255, 0, 0), highlight_rect, 2)


    # Darken and blur the screen except for the selected part
    if not adding_text and active and highlight_rect is not None and darken_blur_effect is not None:
        darken_blur_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        darken_blur_surface.fill((0, 0, 0, 200)) 
        pygame.draw.rect(darken_blur_surface, (255, 255, 255, 0), highlight_rect, 0) 
        window.blit(darken_blur_surface, (0, 0))
    else:
        darken_blur_effect = False 

    

    # Zoomed-in view
    if zoomed_rect is not None:
        # Check if the zoomed rectangle goes beyond the image boundaries
        if zoomed_rect.left < 0:
            zoomed_rect.left = 0
        if zoomed_rect.right > image.get_width():
            zoomed_rect.right = image.get_width()
        if zoomed_rect.top < 0:
            zoomed_rect.top = 0
        if zoomed_rect.bottom > image.get_height():
            zoomed_rect.bottom = image.get_height()

        # Calculate the position to display the zoomed area at the center of the screen
        zoomed_x = (window_width - zoomed_rect.width) // 2
        zoomed_y = (window_height - zoomed_rect.height) // 2

        # Get the zoomed area from the original image
        zoomed_area = image.subsurface(zoomed_rect)

        # Scale the zoomed area to fit the window
        zoomed_area = pygame.transform.scale(zoomed_area, (window_width, window_height))

        # Create a copy of the original image
        image_copy = image.copy()

        # Convert the image copy to a numpy array
        image_array = pygame.surfarray.array3d(image_copy)

        # Blur the background outside the zoomed area
        blurred_array = cv2.GaussianBlur(image_array, (25, 25), 0)

        # Convert the blurred array back to a Pygame surface
        blurred_surface = pygame.surfarray.make_surface(blurred_array)

        # Blit the blurred background onto the window
        window.blit(blurred_surface, (0, 0))

        # Blit the zoomed area onto the window at the center with the zoomed offset
        window.blit(zoomed_area, (zoomed_x - zoomed_offset_x, zoomed_y - zoomed_offset_y))



    

    # Update the display
    pygame.display.update()
    

# Quit Pygame
pygame.quit()

