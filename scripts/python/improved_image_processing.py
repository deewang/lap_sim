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
    if sensitivity == 'high':
        # Ultra-sensitive: catch any hint of red/pink/orange
        mask1 = cv2.inRange(hsv, (0, 5, 5), (25, 255, 255))      # Very wide red-orange
        mask2 = cv2.inRange(hsv, (160, 5, 5), (185, 255, 255))   # Very wide red-pink
    elif sensitivity == 'normal':
        # Sensitive: good for faded red lines
        mask1 = cv2.inRange(hsv, (0, 30, 30), (15, 255, 255))      # Red-orange range
        mask2 = cv2.inRange(hsv, (165, 30, 30), (180, 255, 255))   # Red-pink range
    else:  # 'low' sensitivity (original)
        # Conservative: only clear red
        mask1 = cv2.inRange(hsv, (0, 70, 70), (10, 255, 255))
        mask2 = cv2.inRange(hsv, (170, 70, 70), (180, 255, 255))
    
    mask = cv2.bitwise_or(mask1, mask2)



    # Clean up noise while preserving thin lines
    # Use smaller blur to avoid eliminating thin lines
    mask = cv2.medianBlur(mask, 1) #number must be odd
    
    # Morphological operations to connect broken parts and remove noise
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Close small gaps in the line
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_small)
    
    # Remove small noise blobs
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small)
    
    # Additional cleanup: remove very small connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    
    # Keep only the largest connected component (main track line)
    if num_labels > 1:  # 0 is background
        # Find the largest component (excluding background at index 0)
        largest_component = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        mask = (labels == largest_component).astype(np.uint8) * 255
        print(f"[extract_centerline] Kept largest component out of {num_labels-1} components")

    # Skeletonize to one-pixel-wide path
    skel = skeletonize(mask > 0)

        
    # Clean up skeleton: remove small disconnected segments
    skel_uint8 = (skel * 255).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skel_uint8, connectivity=8)
    
    if num_labels > 1:  # 0 is background
        # Keep only components that are large enough (filter out small noise)
        min_component_size = 50  # Minimum pixels in a valid track segment
        cleaned_skel = np.zeros_like(skel, dtype=bool)
        
        for i in range(1, num_labels):  # Skip background (0)
            if stats[i, cv2.CC_STAT_AREA] >= min_component_size:
                cleaned_skel |= (labels == i)
        
        skel = cleaned_skel
        print(f"[extract_centerline] Kept {np.sum([stats[i, cv2.CC_STAT_AREA] >= min_component_size for i in range(1, num_labels)])} components out of {num_labels-1}")


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


