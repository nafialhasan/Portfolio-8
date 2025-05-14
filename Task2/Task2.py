import time
import create_rtree



def read_dataset(file_path):
    # This function reads the dataset from a file and converts it into a list of dictionaries.
    with open(file_path, 'r') as file:  # Open the file in read mode.
        points_list = []  # Initialize an empty list to store the data points.
        for line in file:  # Iterate over each line in the file.
            parts = line.strip().split()  # Strip leading/trailing whitespace and split by space.
            # Create a dictionary for the point with id, x, and y values.
            point = {'id': parts[0], 'x': float(parts[1]), 'y': float(parts[2])}
            points_list.append(point)  # Add the point to the list of points.
        return points_list  # Return the list of points.

def sequential_scan_skyline(datasets):
    # This function performs a sequential scan to find the skyline points across multiple datasets.
    all_points = []  # List to hold points from all datasets.
    for dataset in datasets:  # Loop through each dataset file path.
        all_points.extend(read_dataset(dataset))  # Read and add points from each dataset to the list.

    skyline = []  # List to hold the skyline points.
    for point in all_points:  # Iterate over each point in the combined list.
        # Check if there's no point that dominates the current point.
        if not any(dominates(other_point, point) for other_point in all_points):
            skyline.append(point)  # If not dominated, add to skyline list.

    # Remove duplicates by converting to a dictionary and back to list, then sort.
    unique_skyline_points = {p['id']: p for p in skyline}.values()
    sorted_skyline_points = sorted(unique_skyline_points, key=lambda p: (p['x'], -p['y']))

    return sorted_skyline_points  # Return the sorted list of unique skyline points.

def mindist_to_origin(mbr):
    # Since we're considering minimum price and maximum area, we use 'x1' and 'y2'.
    return mbr['x1']**2 + mbr['y2']**2

def bbs_skyline_search(rtree):
    skyline = []  # Initialize an empty list for skyline points
    L = []  # Initialize an empty list for nodes sorted by mindist to origin
    
    # Insert the MBR of the root into the list
    L.append((mindist_to_origin(rtree.root.MBR), rtree.root))
    # Sort the list by mindist to origin
    L.sort(key=lambda x: x[0])
    
    while L:
        # Remove the first entry from the list
        _, node = L.pop(0)
        
        if node.is_leaf():
            # Process leaf nodes
            for point in node.data_points:
                if not any(dominates(sky_point, point) for sky_point in skyline):
                    # Update the skyline if 'point' is not dominated by any point in the skyline
                    skyline = [sky_point for sky_point in skyline if not dominates(point, sky_point)]
                    skyline.append(point) # add 'point' to the skyline
        
        else:
            # Process internal nodes
            for child in node.child_nodes:
                child_mbr_point = {'x': child.MBR['x1'], 'y': child.MBR['y2']} # Since we're aiming for minimum cost and maximum area
                if not any(dominates(sky_point, child_mbr_point) for sky_point in skyline):
                    # If the MBR is not dominated, add its children to the list
                    L.append((mindist_to_origin(child.MBR), child))
            # Sort the list again after new insertions
            L.sort(key=lambda x: x[0])
    
    return skyline  # Return the list of skyline points


def dominates(a, b): # a dominates b if price of a is less or equal but area of a is higher
    return a['x'] <= b['x'] and a['y'] >= b['y'] and (a['x'] < b['x'] or a['y'] > b['y'])

def divide_dataset(points_list, dimension='x'):
    # This function divides the dataset into two subspaces based on the median value of the specified dimension.
    sorted_points = sorted(points_list, key=lambda p: p[dimension])  # Sort points by the given dimension.
    mid_index = len(sorted_points) // 2  # Find the middle index.
    # Return two halves of the sorted list as separate subspaces.
    return sorted_points[:mid_index], sorted_points[mid_index:]

def bbs_divide_and_conquer(points_list):
    # This function applies the BBS algorithm using a divide-and-conquer strategy.
    subspace1, subspace2 = divide_dataset(points_list)  # Divide the dataset into two subspaces.
    
    # Construct an R-tree for each subspace and perform BBS to find the skyline in each.
    rtree1 = create_rtree.main(subspace1)
    rtree2 = create_rtree.main(subspace2)
    
    skyline1 = bbs_skyline_search(rtree1)
    skyline2 = bbs_skyline_search(rtree2)
    
    combined_skyline = skyline1 + skyline2  # Combine the skylines from both subspaces.
    
    # Perform a final dominance check to remove dominated points and get the final skyline.
    final_skyline = []
    for point in combined_skyline:
        if not any(dominates(other_point, point) for other_point in combined_skyline):
            final_skyline.append(point)
    
    return final_skyline  # Return the final list of skyline points.

# Main function to execute all skyline algorithms and output results
def main():
    dataset_path = "city1.txt"  # Specify the dataset path
    output_file_path = "output_task2_city1.txt"  # Define output file path

    points_list = read_dataset(dataset_path)
    
    with open(output_file_path, 'w') as output_file:
        print("Output file opened successfully.")
            
        # Perform Sequential Scan Skyline Search
        start_time = time.time()
        skyline_points = sequential_scan_skyline([dataset_path])
        end_time = time.time()
        output_file.write("Sequential Scan Skyline Results:\n")
        for point in skyline_points:
            output_file.write(f"{point['id']} {point['x']} {point['y']}\n")
        output_file.write(f"Sequential Scan Time: {end_time - start_time}\n\n")
        output_file.flush()  # Force writing to the file
        print("Sequential Scan Skyline Results written to file.")
            
        # Build the R-tree from the points list and then perform BBS Skyline Search
        rtree = create_rtree.main(points_list)  # Create an RTree object from points_list
        start_time = time.time()
        bbs_skyline_points = bbs_skyline_search(rtree)  # Pass the RTree object
        end_time = time.time()
        
        output_file.write("BBS Skyline Search Results:\n")
        for point in bbs_skyline_points:
            output_file.write(f"{point['id']} {point['x']} {point['y']}\n")
        output_file.write(f"BBS Execution Time: {end_time - start_time}\n\n")
        output_file.flush()  # Force writing to the file
        print("BBS Skyline Search Results written to file.")
            
        # Perform BBS with Divide-and-Conquer Skyline Search
        start_time = time.time()
        final_skyline = bbs_divide_and_conquer(points_list)
        end_time = time.time()
        
        output_file.write("BBS with Divide-and-Conquer Skyline Results:\n")
        for point in final_skyline:
            output_file.write(f"{point['id']} {point['x']} {point['y']}\n")
        output_file.write(f"Execution Time: {end_time - start_time}\n")
        output_file.flush()  # Force writing to the file
        print("BBS with Divide-and-Conquer Skyline Results written to file.")

if __name__ == "__main__":
    main()
