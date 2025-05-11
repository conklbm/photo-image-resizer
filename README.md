# Photo Resizer Plus Border

A tool that resizes images to 1200 pixels wide while maintaining aspect ratio, adds a 1-pixel black border, and converts to JPG format.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Process a single image:
```bash
python image_resizer.py input_image.png output_image.jpg
```

### Process all images in a directory:
```bash
python image_resizer.py input_directory output_directory
```

The tool will automatically:
1. Resize the image to 1200 pixels wide while maintaining aspect ratio
2. Add a 1-pixel black border
3. Convert to JPG format
4. Save the processed image(s) to the specified output location

## Supported Input Formats
- PNG
- JPG
- JPEG
- WEBP
- TIFF

## Output Format
All output images will be in JPG format with 95% quality.
