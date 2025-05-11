#!/usr/bin/env python
"""
Image Resizer CLI Tool
Resize images to 1200px width, maintain aspect ratio, add border, and convert to JPG
"""

from PIL import Image
import os
import sys
import argparse

def add_border(image, border_width=1, border_color=(0, 0, 0)):
    """
    Add a border to the image.
    
    Args:
        image: PIL Image object
        border_width: Width of the border in pixels
        border_color: RGB tuple for border color (default is black)
    
    Returns:
        PIL Image object with border
    """
    width, height = image.size
    new_width = width + border_width * 2
    new_height = height + border_width * 2
    
    bordered_image = Image.new('RGB', (new_width, new_height), border_color)
    bordered_image.paste(image, (border_width, border_width))
    return bordered_image

def resize_and_process_image(input_path, output_path):
    """
    Resize image to 1200 pixels wide while maintaining aspect ratio,
    add a 1-pixel black border, and save as JPG.
    
    Args:
        input_path: Path to the input image
        output_path: Path to save the processed image
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Calculate new dimensions while maintaining aspect ratio
            original_width, original_height = img.size
            new_width = 1200
            new_height = int((new_width / original_width) * original_height)
            
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Add 1-pixel black border
            bordered_img = add_border(resized_img)
            
            # Save as JPG
            bordered_img.save(output_path, 'JPEG', quality=95)
            print(f"Successfully processed: {input_path} -> {output_path}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def process_directory(input_dir, output_dir):
    """
    Process all images in a directory.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save processed images
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all image files
    image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.tiff')
    image_files = [f for f in os.listdir(input_dir) 
                 if f.lower().endswith(image_extensions)]
    
    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        output_path = os.path.join(output_dir, os.path.splitext(image_file)[0] + '.jpg')
        resize_and_process_image(input_path, output_path)

def main():
    parser = argparse.ArgumentParser(description='Resize images to 1200px width, maintain aspect ratio, add border, and convert to JPG')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    
    args = parser.parse_args()
    
    input_path = args.input
    output_path = args.output
    
    if os.path.isdir(input_path):
        process_directory(input_path, output_path)
    else:
        resize_and_process_image(input_path, output_path)

if __name__ == "__main__":
    main()
