import cv2
import numpy as np
import os
from pathlib import Path

def crop_to_square_object(image_path, output_path, target_size=640, padding_pixels=10):
    """
    Crops an image with white background to focus on the object in a 1:1 ratio.
    
    Args:
        image_path: Path to the input image
        output_path: Path to save the cropped image
        target_size: Target size for the output image (square)
        padding_pixels: Fixed padding in pixels around the object
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image {image_path}")
            return False
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find the object (non-white pixels)
        # Adjust threshold value if needed (230 works well for most white backgrounds)
        _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours of the object
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print(f"No object found in {image_path}")
            return False
        
        # Find the largest contour (main object)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding box of the object
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate the center of the object
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Calculate the largest dimension + fixed pixel padding
        max_dim = max(w, h)
        padded_size = max_dim + (2 * padding_pixels)  # Add padding to both sides
        
        # Calculate square boundaries from the center and padded size
        half_size = padded_size // 2
        square_x = center_x - half_size
        square_y = center_y - half_size
        
        # Ensure the square doesn't go outside image boundaries
        if square_x < 0:
            square_x = 0
        if square_y < 0:
            square_y = 0
        if square_x + padded_size > img.shape[1]:
            square_x = img.shape[1] - padded_size
        if square_y + padded_size > img.shape[0]:
            square_y = img.shape[0] - padded_size
            
        # Make sure coordinates don't go negative (if image is too small)
        square_x = max(0, square_x)
        square_y = max(0, square_y)
        
        # Final adjustment to ensure we don't exceed image dimensions
        square_size = min(padded_size, img.shape[0] - square_y, img.shape[1] - square_x)
        
        # Crop the image to square
        cropped = img[square_y:square_y+square_size, square_x:square_x+square_size]
        
        # Resize to target size
        resized = cv2.resize(cropped, (target_size, target_size), interpolation=cv2.INTER_AREA)
        
        # Save the result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, resized)
        
        print(f"Processed: {image_path} -> {output_path}")
        return True
    
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def process_directory(input_dir, output_dir, target_size=640, padding_pixels=10):
    """Process all images in a directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Supported image extensions
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # Process each image
    count = 0
    for ext in extensions:
        for img_path in input_path.glob(f'*{ext}'):
            out_file = output_path / img_path.name
            if crop_to_square_object(str(img_path), str(out_file), target_size, padding_pixels):
                count += 1
    
    print(f"Processed {count} images from {input_dir} to {output_dir}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crop images to 1:1 ratio focusing on objects")
    parser.add_argument("--input", "-i", required=True, help="Input image or directory")
    parser.add_argument("--output", "-o", required=True, help="Output image or directory")
    parser.add_argument("--size", "-s", type=int, default=640, help="Output size (default: 640)")
    parser.add_argument("--padding", "-p", type=int, default=10, help="Padding in pixels around object (default: 10)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_dir():
        # Process all images in directory
        process_directory(args.input, args.output, args.size, args.padding)
    else:
        # Process single image
        crop_to_square_object(args.input, args.output, args.size, args.padding)
