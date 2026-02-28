# /python/image_processing.py
import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt

def extract_centerline(image_path: str, sensitivity = 'normal', show_images=False):
    """
    Reads the input track image, isolates the red centerline, and extracts pixel coordinates along it.
    Returns: Nx2 numpy array of (x, y) points in pixel coordinates.
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Convert to HSV and isolate red color
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Adjust sensitivity based on parameter

    if sensitivity == 'endurance2023':  # same as 'high for now'
        mask1 = cv2.inRange(hsv, (0, 5, 5), (25, 255, 255))      
        mask2 = cv2.inRange(hsv, (160, 5, 5), (185, 255, 255)) 
    elif sensitivity == 'endurance2025':  # same as 'normal' for now
        # Sensitive: good for faded red lines
        mask1 = cv2.inRange(hsv, (0, 30, 30), (15, 255, 255))      # Red-orange range
        mask2 = cv2.inRange(hsv, (165, 30, 30), (180, 255, 255))   # Red-pink range

    elif sensitivity == 'high':
        # Ultra-sensitive: catch any hint of red/pink/orange
        mask1 = cv2.inRange(hsv, (0, 5, 5), (25, 255, 255))      # Very wide red-orange
        mask2 = cv2.inRange(hsv, (160, 5, 5), (185, 255, 255))   # Very wide red-pink
    elif sensitivity == 'normal':
        # Sensitive: good for faded red lines
        mask1 = cv2.inRange(hsv, (0, 30, 30), (15, 255, 255))      # Red-orange range
        mask2 = cv2.inRange(hsv, (165, 30, 30), (180, 255, 255))   # Red-pink range
    elif sensitivity == 'low':
        # Conservative: only clear red
        mask1 = cv2.inRange(hsv, (0, 70, 70), (10, 255, 255))
        mask2 = cv2.inRange(hsv, (170, 70, 70), (180, 255, 255))
    else:
        raise ValueError(f"Unknown sensitivity setting: {sensitivity}")
    
    mask = cv2.bitwise_or(mask1, mask2)



    # Clean up noise
    mask = cv2.medianBlur(mask, 3) #number must be odd

    # Skeletonize to one-pixel-wide path
    skel = skeletonize(mask > 0)

    # Extract (y, x) coordinates and convert to (x, y)
    coords = np.column_stack(np.where(skel))
    coords = np.flip(coords, axis=1)  # (x, y) order


    # Show intermediate masks if required
    # Display images if requested
    if show_images:
        plt.figure(figsize=(15, 5))
        
        # Original image
        plt.subplot(1, 4, 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')
        plt.axis('off')
        
        # Red mask
        plt.subplot(1, 4, 2)
        plt.imshow(mask, cmap='gray')
        plt.title('Red Color Mask')
        plt.axis('off')
        
        # Cleaned mask
        plt.subplot(1, 4, 3)
        plt.imshow(mask, cmap='gray')
        plt.title('Cleaned Mask')
        plt.axis('off')
        
        # Final skeleton
        plt.subplot(1, 4, 4)
        plt.imshow(skel, cmap='gray')
        plt.title('Skeleton (Final Result)')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()

    print(f"[extract_centerline] Extracted {len(coords)} raw points")
    return coords


