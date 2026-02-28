# /python/export_utils.py
import numpy as np
import os
from datetime import datetime

def save_to_csv(points, out_path, include_header=False, overwrite=True):
    """
    Saves (x, y) points to CSV, with options for headers and overwrite protection.
    
    Args:
        points: Nx2 numpy array of (x, y) coordinates
        out_path: Output file path (will create directories if needed)
        include_header: Whether to include column headers (default: False for MATLAB compatibility)
        overwrite: Whether to overwrite existing files (default: True)
    """
    try:
        # Create directories if they don't exist
        dir_path = os.path.dirname(out_path)
        if dir_path:  # Only create if there's actually a directory path
            os.makedirs(dir_path, exist_ok=True)
            print(f"[save_to_csv] Ensured directory exists: {dir_path}")
        
        # Check if file exists and handle overwrite
        if os.path.exists(out_path) and not overwrite:
            # Create backup filename with timestamp
            base, ext = os.path.splitext(out_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = f"{base}_{timestamp}{ext}"
            print(f"[save_to_csv] File exists, saving as: {out_path}")
        
        # Prepare header if requested
        header = "x,y" if include_header else ""
        
        # Save the file
        np.savetxt(out_path, points, delimiter=',', fmt='%.6f', header=header, comments='')
        
        # Success message with file info
        file_size = os.path.getsize(out_path)
        print(f"[save_to_csv] ✓ Saved {len(points)} points to {out_path}")
        print(f"[save_to_csv] ✓ File size: {file_size:,} bytes")
        
        return out_path  # Return the actual path used (in case of timestamp)
        
    except Exception as e:
        print(f"[save_to_csv] ✗ Error saving file: {e}")
        raise


def save_to_json(points, out_path, metadata=None):
    """
    Saves points to JSON format with optional metadata.
    
    Args:
        points: Nx2 numpy array of (x, y) coordinates
        out_path: Output file path
        metadata: Optional dictionary with additional info (scale, units, etc.)
    """
    import json
    
    try:
        # Create directories if needed
        dir_path = os.path.dirname(out_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Prepare data structure
        data = {
            "points": points.tolist(),
            "num_points": len(points),
            "created": datetime.now().isoformat(),
        }
        
        # Add metadata if provided
        if metadata:
            data["metadata"] = metadata
        
        # Save JSON file
        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size = os.path.getsize(out_path)
        print(f"[save_to_json] ✓ Saved {len(points)} points to {out_path}")
        print(f"[save_to_json] ✓ File size: {file_size:,} bytes")
        
        return out_path
        
    except Exception as e:
        print(f"[save_to_json] ✗ Error saving file: {e}")
        raise


def save_track_summary(points, out_path, track_name="Unknown Track", scale_info=None):
    """
    Saves a comprehensive track summary with statistics.
    
    Args:
        points: Nx2 numpy array of (x, y) coordinates  
        out_path: Output file path
        track_name: Name of the track
        scale_info: Dictionary with scaling information
    """
    try:
        # Create directories if needed
        dir_path = os.path.dirname(out_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Calculate track statistics
        x_coords, y_coords = points[:, 0], points[:, 1]
        track_width = np.max(x_coords) - np.min(x_coords)
        track_height = np.max(y_coords) - np.min(y_coords)
        
        # Estimate track length (sum of distances between consecutive points)
        distances = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))
        track_length = np.sum(distances)
        
        # Create summary text
        summary = [
            f"TRACK SUMMARY REPORT",
            f"=" * 50,
            f"Track Name: {track_name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"BASIC STATISTICS:",
            f"  Number of points: {len(points):,}",
            f"  Track width:      {track_width:.3f}",
            f"  Track height:     {track_height:.3f}",
            f"  Estimated length: {track_length:.3f}",
            f"",
        ]
        
        # Add scale information if provided
        if scale_info:
            summary.extend([
                f"SCALE INFORMATION:",
                f"  Units: {scale_info.get('units', 'Unknown')}",
                f"  Scale factor: {scale_info.get('scale_factor', 'Unknown')}",
                f"  Pixels per foot: {scale_info.get('pixels_per_foot', 'Unknown')}",
                f"",
            ])
        
        # Add coordinate ranges
        summary.extend([
            f"COORDINATE RANGES:",
            f"  X: {np.min(x_coords):8.3f} to {np.max(x_coords):8.3f}",
            f"  Y: {np.min(y_coords):8.3f} to {np.max(y_coords):8.3f}",
            f"",
            f"SAMPLE COORDINATES (first 5 points):",
        ])
        
        # Add sample coordinates
        for i in range(min(5, len(points))):
            x, y = points[i]
            summary.append(f"  Point {i+1:2d}: ({x:8.3f}, {y:8.3f})")
        
        # Write summary file
        with open(out_path, 'w') as f:
            f.write('\n'.join(summary))
        
        file_size = os.path.getsize(out_path)
        print(f"[save_track_summary] ✓ Saved track summary to {out_path}")
        print(f"[save_track_summary] ✓ File size: {file_size:,} bytes")
        
        return out_path
        
    except Exception as e:
        print(f"[save_track_summary] ✗ Error saving file: {e}")
        raise
