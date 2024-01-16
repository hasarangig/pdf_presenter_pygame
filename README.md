# About The Project
PyGame application implemented for the purpose of presenting PDF documents with eyecandy tools. program is implemented using Pygame, which is a popular Python library for creating games and multimedia applications. The application is intended to provide features that go beyond static PDF viewing, enabling dynamic interaction and effective communication with the audience.

# Getting Started
## Prerequisites 
To use the provided code, you'll need to ensure that the required libraries are installed. You can install them using the following commands:

    pip install pygame
    pip install pdf2image
    pip install opencv-python
    pip install numpy    

Please note that the pdf2image library relies on the poppler utility. Make sure you have it installed on your system. You can install it using the following command.

    sudo apt-get install -y poppler-utils

After installing the necessary libraries, you can run the provided code. Ensure that the paths to the PDF file and the input/output folders are correct. Since this applications is implemented to open a one particular PDF file, the user has to provide the location of the PDF file as the pdf_path. a seperate location need to be set as image_folder to save the images that are created once the PDf is converted to images. The paths are set in the following lines:

    pdf_path = os.path.join(os.path.dirname(__file__), "../inputs/sample.pdf")
    image_folder = os.path.join(os.path.dirname(__file__), "../outputs/output_images")

Finally, execute the script, and the PDF Presenter application should run, allowing you to navigate through the images of the PDF, zoom in and out, and add text annotations.

## Installation

Clone the repo

    git clone https://github.com/hasarangig/pdf_presenter_pygame.git

To run the application execute the below command fron from src directory

    python3 pdfpresenter.py 
