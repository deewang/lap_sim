# /python/path_extraction.py
import numpy as np
from scipy import interpolate
from scipy.spatial import distance
import matplotlib.pyplot as plt

def smooth_path(rawpoints, show_visualization=False, startPoint = [0,0], smoothness=0, max_jump_distance=50):
    """
    Orders and smooths the input (x, y) points.
    Returns a resampled Nx2 numpy array with evenly spaced points.
    """
    # --- Step 1: rough ordering with distance-based stopping ---
    # Sort points by proximity to form a path (simple nearest-neighbor walk)

    
    if startPoint != [0,0]:
        start_index = findIndexOfClosestPoint(rawpoints, startPoint)
        points = np.concatenate([rawpoints[start_index:], rawpoints[:start_index]]) # shift starting point
    else :
        points = rawpoints.copy()

    num_points = len(points)
    ordered = [points[0]]
    remaining = points[1:].tolist()
    
    while remaining:
        last = ordered[-1]
        dists = np.linalg.norm(np.array(remaining) - last, axis=1) #distance from last point to ALL other points
        min_dist = np.min(dists)
        
        # Stop if the closest point is too far away (indicates jump to noise)
        if min_dist > max_jump_distance:
            print(f"[smooth_path] Stopping at {len(ordered)} points - next closest point is {min_dist:.1f} pixels away (threshold: {max_jump_distance})")
            break
        
        # Optional: Stop if we've completed a circuit (close to starting point)
        if len(ordered) > 100:  # Only check after we have some points
            dist_to_start = np.linalg.norm(np.array(remaining)[np.argmin(dists)] - ordered[0])
            if dist_to_start < 10 and len(ordered) > len(points) * 0.8:  # Close to start and most points processed
                print(f"[smooth_path] Circuit completed at {len(ordered)} points - close to starting point")
                break
            
        idx = np.argmin(dists) #find the index of the closest point
        ordered.append(remaining.pop(idx))
        if len(ordered) % 500 == 0:
            print(f"[smooth_path] Progress: {len(ordered)} points ordered")

    ordered = np.array(ordered)

    # --- Step 2: spline smoothing ---
    tck, u = interpolate.splprep([ordered[:, 0], ordered[:, 1]], s=smoothness)
    u_new = np.linspace(0, 1, num_points)
    x_smooth, y_smooth = interpolate.splev(u_new, tck)

    smoothed = np.column_stack([x_smooth, y_smooth])
    print(f"[smooth_path] Generated {len(smoothed)} smooth points")
    
    # Visualization if requested
    if show_visualization:
        plt.figure(figsize=(15, 5))
        
        # Plot 1: Original unordered points
        plt.subplot(1, 3, 1)
        plt.scatter(points[:, 0], -points[:, 1], c='red', s=1, alpha=0.6)  # Flip Y axis
        plt.title(f'Original Points (Unordered)\n{len(points)} points')
        plt.xlabel('X (pixels)')
        plt.ylabel('Y (pixels) - Flipped for correct orientation')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Ordered points (connected)
        plt.subplot(1, 3, 2)
        plt.plot(ordered[:, 0], -ordered[:, 1], 'b-', linewidth=1, alpha=0.7)  # Flip Y axis
        plt.scatter(ordered[0, 0], -ordered[0, 1], c='green', s=50, marker='o', label='Start')  # Flip Y axis
        plt.scatter(ordered[-1, 0], -ordered[-1, 1], c='red', s=50, marker='x', label='End')  # Flip Y axis
        plt.title(f'Ordered Path\n{len(ordered)} points')
        plt.xlabel('X (pixels)')
        plt.ylabel('Y (pixels) - Flipped for correct orientation')
        plt.legend()
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Final smooth path
        plt.subplot(1, 3, 3)
        plt.plot(smoothed[:, 0], -smoothed[:, 1], 'purple', linewidth=1)  # Flip Y axis
        plt.scatter(smoothed[0, 0], -smoothed[0, 1], c='green', s=50, marker='o', label='Start')  # Flip Y axis
        plt.scatter(smoothed[-1, 0], -smoothed[-1, 1], c='red', s=50, marker='x', label='End')  # Flip Y axis
        plt.title(f'Smoothed Path\n{len(smoothed)} points')
        plt.xlabel('X (pixels)')
        plt.ylabel('Y (pixels) - Flipped for correct orientation')
        plt.legend()
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    return smoothed


def findIndexOfClosestPoint(points, target):
    min_dist = float('inf')
    min_index = -1
    for i, (x, y) in enumerate(points):
        dist = np.linalg.norm(np.array([x, y]) - target)
        if dist < min_dist:
            min_dist = dist
            min_index = i
    print(f"[findIndexOfClosestPoint] Closest point to {target} is at index {min_index} with distance {min_dist:.2f}")
    return min_index