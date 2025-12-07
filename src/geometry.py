# geometry.py
import numpy as np
from .medium import Region


def calculate_direction_cosines(x, y, z, x_prev, y_prev, z_prev):
    delta_x = x - x_prev
    delta_y = y - y_prev
    delta_z = z - z_prev
    delta_s = np.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
    return delta_x / delta_s, delta_y / delta_s, delta_z / delta_s

def count_coordinates_in_boundary(coordinates, x_bounds, y_bounds, z_bounds):
    """
    Counts the number of coordinates within the specified boundaries.

    Args:
        coordinates (list of tuples): List of (x, y, z) coordinate tuples.
        x_bounds (tuple): Min and max values for the x-coordinate.
        y_bounds (tuple): Min and max values for the y-coordinate.
        z_bounds (tuple): Min and max values for the z-coordinate.

    Returns:
        int: Number of coordinates within the specified boundaries.
    """
    return sum(
        x_bounds[0] <= x <= x_bounds[1] and
        y_bounds[0] <= y <= y_bounds[1] and
        z_bounds[0] <= z <= z_bounds[1]
        for x, y, z in coordinates
    )

def get_primitive_surfaces(surface_list):
    """
    Recursively extracts actual geometric surfaces (Planes, Spheres, etc.)
    from a list that might contain nested Regions.
    """
    primitives = []
    for surface in surface_list:
        # Check if the surface is actually a nested Region
        if isinstance(surface, Region):
            # RECURSION: Go deeper to find the primitives inside
            primitives.extend(get_primitive_surfaces(surface.surfaces))
        else:
            # It's a real surface (Plane, Sphere, etc.)
            primitives.append(surface)
    return primitives

def calculate_nearest_boundary(state, regions, u, v, w):
    x, y, z = state["x"], state["y"], state["z"]
    nearest_distance = float("inf")
    nearest_point = None
    nearest_region = None
    nearest_surface = None  # <--- Initialized here

    # Iterate over all regions provided (Global, Local, etc.)
    for region in regions:

        # FIX 1: Flatten the surfaces to handle nested CSG regions
        # If 'region' is a Union of two Boxes, this gets the Planes of those Boxes.
        primitives = get_primitive_surfaces(region.surfaces)

        for surface in primitives:
            # Solve for distance
            distance = surface.nearest_surface_method(x, y, z, u, v, w)

            # Basic validation (forward only)
            if distance is not None and distance >= 0:

                # Check if this is the closest valid intersection found so far
                if distance < nearest_distance:

                    # Calculate candidate point
                    candidate_point = (x + distance * u, y + distance * v, z + distance * w)

                    # Verify the point actually belongs to the region
                    # (Necessary for CSG operations like Intersection/Difference)
                    if region.contains(*candidate_point):

                        nearest_distance = distance
                        nearest_point = candidate_point
                        nearest_region = region

                        # FIX 2: Actually assign the variable!
                        # Now the code block at the bottom won't be dead.
                        nearest_surface = surface

    # Handle escape
    if nearest_point is None:
        return None, None, float('inf')

    return nearest_point, nearest_region, nearest_distance

def calculate_void_si_max(mediums):
    # Find the void medium
    void_medium = next((m for m in mediums if m.is_void), None)
    if void_medium:
        x_range = void_medium.x_bounds[1] - void_medium.x_bounds[0]
        y_range = void_medium.y_bounds[1] - void_medium.y_bounds[0]
        z_range = void_medium.z_bounds[1] - void_medium.z_bounds[0]
        # Diagonal of the bounding box
        si_max = np.sqrt(x_range**2 + y_range**2 + z_range**2)
        return si_max
    return float('inf')  # No void medium, no limit
