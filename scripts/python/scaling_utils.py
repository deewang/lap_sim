# /python/scaling_utils.py
import numpy as np
import matplotlib.pyplot as plt

def scale_to_meters(points, pixelsPerFootScale, show_visualization=False):
    """
    Scales (x, y) coordinates from pixels to meters.
    scale: pixels per foot.
    Returns: Nx2 numpy array in meters.
    """

    scale = 0.3048 / pixelsPerFootScale  # meters per pixel
    scaled = points * scale
    
    # Calculate track dimensions for comparison
    pixel_width = np.max(points[:, 0]) - np.min(points[:, 0])
    pixel_height = np.max(points[:, 1]) - np.min(points[:, 1])
    meter_width = np.max(scaled[:, 0]) - np.min(scaled[:, 0])
    meter_height = np.max(scaled[:, 1]) - np.min(scaled[:, 1])
    
    print(f"[scale_to_meters] Applied scale: {scale:.6f} m/px ({pixelsPerFootScale} pixels/foot)")
    print(f"[scale_to_meters] Track dimensions - Pixels: {pixel_width:.1f} x {pixel_height:.1f}, Meters: {meter_width:.2f} x {meter_height:.2f}")
    
    # Visualization if requested
    if show_visualization:
        plt.figure(figsize=(16, 8))
        
        # Plot 1: Original pixel coordinates
        plt.subplot(1, 2, 1)
        plt.plot(points[:, 0], -points[:, 1], 'b-', linewidth=2, alpha=0.8)  # Flip Y for correct orientation
        plt.scatter(points[0, 0], -points[0, 1], c='green', s=100, marker='o', label='Start', zorder=5)
        plt.scatter(points[-1, 0], -points[-1, 1], c='red', s=100, marker='x', label='End', zorder=5)
        
        plt.title('BEFORE SCALING: Pixel Coordinates', fontsize=14, fontweight='bold')
        plt.xlabel('X (pixels)', fontsize=12)
        plt.ylabel('Y (pixels) - Flipped for correct orientation', fontsize=12)
        
        # Add dimension annotations
        plt.text(0.02, 0.98, f'Track Width: {pixel_width:.0f} pixels', 
                transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        plt.text(0.02, 0.90, f'Track Height: {pixel_height:.0f} pixels', 
                transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        plt.text(0.02, 0.82, f'Scale: {pixelsPerFootScale:.1f} pixels/foot', 
                transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.legend()
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Scaled meter coordinates
        plt.subplot(1, 2, 2)
        plt.plot(scaled[:, 0], -scaled[:, 1], 'purple', linewidth=2, alpha=0.8)  # Flip Y for correct orientation
        plt.scatter(scaled[0, 0], -scaled[0, 1], c='green', s=100, marker='o', label='Start', zorder=5)
        plt.scatter(scaled[-1, 0], -scaled[-1, 1], c='red', s=100, marker='x', label='End', zorder=5)
        
        plt.title('AFTER SCALING: Real-World Coordinates', fontsize=14, fontweight='bold')
        plt.xlabel('X (meters)', fontsize=12)
        plt.ylabel('Y (meters) - Flipped for correct orientation', fontsize=12)
        
        # Add dimension annotations
        plt.text(0.02, 0.98, f'Track Width: {meter_width:.2f} meters', 
                transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        plt.text(0.02, 0.90, f'Track Height: {meter_height:.2f} meters', 
                transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        plt.text(0.02, 0.82, f'Scale: {scale:.6f} m/pixel', 
                transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # Add scale reference lines
        if meter_width > 10:  # If track is reasonably large
            # Add 10m reference line
            ref_length_m = 10
            ref_length_px = ref_length_m / scale
            x_start = np.min(scaled[:, 0]) + meter_width * 0.1
            y_ref = np.min(-scaled[:, 1]) + (np.max(-scaled[:, 1]) - np.min(-scaled[:, 1])) * 0.1
            
            plt.plot([x_start, x_start + ref_length_m], [y_ref, y_ref], 'k-', linewidth=4)
            plt.text(x_start + ref_length_m/2, y_ref - (np.max(-scaled[:, 1]) - np.min(-scaled[:, 1])) * 0.05, 
                    '10m', ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.legend()
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        
        # Add overall title
        plt.suptitle(f'Track Scaling Transformation: {pixelsPerFootScale} pixels/foot → Real World Coordinates', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        plt.tight_layout()
        plt.show()
        
        # Print detailed comparison
        print("\n" + "="*60)
        print("SCALING TRANSFORMATION SUMMARY")
        print("="*60)
        print(f"Input Scale Factor: {pixelsPerFootScale:.2f} pixels per foot")
        print(f"Conversion Factor: {scale:.6f} meters per pixel")
        print(f"")
        print(f"DIMENSIONS COMPARISON:")
        print(f"  Original (pixels):  {pixel_width:.0f} × {pixel_height:.0f}")
        print(f"  Scaled (meters):    {meter_width:.2f} × {meter_height:.2f}")
        print(f"")
        print(f"TRACK STATISTICS:")
        print(f"  Number of points:   {len(points)}")
        print(f"  Track perimeter:    ~{np.sum(np.sqrt(np.sum(np.diff(scaled, axis=0)**2, axis=1))):.2f} meters")
        print("="*60)
    
    return scaled

