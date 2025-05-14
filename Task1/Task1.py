import math
import time
import create_rtree

# Function to load points from a dataset file
def load_points(file_path):
    """
    Reads points from a specified file path and returns them as a list of dictionaries.
    Each dictionary represents a point with an id, x-coordinate, and y-coordinate.
    
    Args:
        file_path (str): Path to the file containing points.
        
    Returns:
        list: A list of dictionaries where each dictionary contains 'id', 'x', and 'y'.
    """
    points = []
    with open(file_path, 'r') as file:
        for line in file:
            data = line.split()
            points.append({'id': int(data[0]), 'x': float(data[1]), 'y': float(data[2])})
    return points

# Function to perform sequential search for the nearest neighbor
def sequential_search(points_list, queries):
    """
    Finds the nearest point for each query by directly comparing the Euclidean distance between the query
    and all points in the points list. This is a baseline method without optimization.

    Args:
        points_list (list): List of points in the dataset.
        queries (list): List of query points.

    Returns:
        float: Total time taken to complete the sequential search for all queries.
    """
    print("Results of sequential search:")
    checkpoint1_time = time.time()  # Start time for performance measurement
    query_results = {}

    for query in queries:
        distance_points = []
        for point in points_list:
            # Calculate Euclidean distance between query and point
            distance = euclidean_distance(point, query)
            distance_points.append([distance, point])
        
        # Find the nearest point based on minimum distance
        nearest_point = min(distance_points, key=lambda x: x[0])
        query_results[query['id']] = nearest_point[1]
        print(f"id = {nearest_point[1]['id']}, x = {nearest_point[1]['x']}, y = {nearest_point[1]['y']} for query {query['id']}")
    
    checkpoint2_time = time.time()  # End time for performance measurement
    print(f"Total time taken for sequential search: {checkpoint2_time - checkpoint1_time} \n")
    return checkpoint2_time - checkpoint1_time

# Function for Best-First Search (BFS) using custom R-tree indexing
def best_first_search(points_list, queries):
    """
    Finds the nearest point for each query by constructing an R-tree index for the dataset and
    using custom R-tree's nearest neighbor search function.

    Args:
        points_list (list): List of points in the dataset.
        queries (list): List of query points.

    Returns:
        float: Total time taken to complete the BFS for all queries.
    """
    # Create R-tree using your custom R-tree implementation
    rtree = create_rtree.main(points_list)

    mindist_points = {}
    print("\nResults of best first search:")
    checkpoint1_time = time.time()

    for query in queries:
        # Find the nearest neighbor in the R-tree using the custom function
        nearest_point = rtree_nearest_neighbor_search(rtree, query)  # Custom nearest neighbor search
        if nearest_point:
            mindist_points[query['id']] = nearest_point
            print(f"id = {nearest_point['id']}, x = {nearest_point['x']}, y = {nearest_point['y']} for query {query['id']}")
        else:
            print(f"No nearest point found for query {query['id']}")

    checkpoint2_time = time.time()
    print(f"Total time taken for best first search: {checkpoint2_time - checkpoint1_time} \n")
    return checkpoint2_time - checkpoint1_time

# Function for Divide and Conquer search with custom R-tree indices
def divide_and_conquer(points_list, queries):
    """
    Uses divide and conquer with custom R-tree indexing to find the nearest neighbor for each query.
    The dataset is divided into two subgroups, each with its own R-tree index.
    The BFS is applied to both subgroups, and the closest match is selected for each query.

    Args:
        points_list (list): List of points in the dataset.
        queries (list): List of query points.

    Returns:
        float: Total time taken to complete the divide and conquer search for all queries.
    """
    # Divide the dataset into left and right subgroups based on x-coordinates
    points_list = sorted(points_list, key=lambda x: x['x'])
    mid_point = len(points_list) // 2
    left, right = points_list[:mid_point], points_list[mid_point:]

    # Create separate R-trees for the left and right subgroups using the custom R-tree
    left_rtree = create_rtree.main(left)
    right_rtree = create_rtree.main(right)
    
    mindist_points = {}
    print("Results of divide and conquer search:")
    checkpoint1_time = time.time()

    # For each query, find nearest neighbor in both subgroups and select the closest
    for query in queries:
        nearest_left = rtree_nearest_neighbor_search(left_rtree, query)  # Custom function
        nearest_right = rtree_nearest_neighbor_search(right_rtree, query)  # Custom function

        # Select the point with the minimum distance to the query
        if nearest_left and nearest_right:
            if euclidean_distance(nearest_left, query) <= euclidean_distance(nearest_right, query):
                nearest_point = nearest_left
            else:
                nearest_point = nearest_right
        elif nearest_left:
            nearest_point = nearest_left
        else:
            nearest_point = nearest_right

        mindist_points[query['id']] = nearest_point
        if nearest_point:
            print(f"id = {nearest_point['id']}, x = {nearest_point['x']}, y = {nearest_point['y']} for query {query['id']}")
        else:
            print(f"No nearest point found for query {query['id']}")

    checkpoint2_time = time.time()
    print(f"Total time taken for divide and conquer search: {checkpoint2_time - checkpoint1_time} \n")
    return checkpoint2_time - checkpoint1_time

# Helper function for nearest neighbor search in your custom R-tree
def rtree_nearest_neighbor_search(rtree, query):
    """
    Finds the nearest neighbor for a given query point using the custom R-tree.
    This is a placeholder function that should implement the nearest neighbor search
    specific to your custom R-tree structure.

    Args:
        rtree (RTree): The custom R-tree constructed for the dataset.
        query (dict): The query point with 'x' and 'y' coordinates.

    Returns:
        dict: The nearest point or None if no point is found.
    """
    min_distance = float('inf')
    nearest_point = None

    nodes_to_visit = [rtree.root]
    while nodes_to_visit:
        node = nodes_to_visit.pop(0)
        if node.is_leaf():
            for point in node.data_points:
                distance = euclidean_distance(point, query)
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = point
        else:
            # For internal nodes, check MBRs to see if they could contain a closer point
            for child in node.child_nodes:
                if mbr_min_distance(child.MBR, query) < min_distance:
                    nodes_to_visit.append(child)

    return nearest_point

# Function to calculate Euclidean distance between two points
def euclidean_distance(point1, point2):
    """
    Calculates the Euclidean distance between two points in 2D space.

    Args:
        point1 (dict): The first point with 'x' and 'y' coordinates.
        point2 (dict): The second point with 'x' and 'y' coordinates.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.sqrt((point2['x'] - point1['x']) ** 2 + (point2['y'] - point1['y']) ** 2)

# Function to compute minimum distance from MBR to a query point
def mbr_min_distance(mbr, query):
    """
    Calculates the minimum distance from a query point to an MBR (Minimum Bounding Rectangle).

    Args:
        mbr (dict): The MBR with keys 'x1', 'y1', 'x2', 'y2'.
        query (dict): The query point with 'x' and 'y' coordinates.

    Returns:
        float: The minimum distance from the MBR to the query point.
    """
    dx = max(mbr['x1'] - query['x'], 0, query['x'] - mbr['x2'])
    dy = max(mbr['y1'] - query['y'], 0, query['y'] - mbr['y2'])
    return math.sqrt(dx ** 2 + dy ** 2)

# Main function to load datasets, run searches, and display results
def main():
    """
    Main function to:
    1. Load the points from the dataset file and the query file.
    2. Run sequential search, best-first search, and divide-and-conquer approaches.
    3. Print results and performance metrics for each method.
    """
    points_list = load_points("shop_dataset.txt")  # Load points from shop dataset
    queries = load_points("query_points.txt")  # Load query points

    # Execute each search method and measure time taken
    ss_time = sequential_search(points_list, queries)
    bfs_time = best_first_search(points_list, queries)
    dcs_time = divide_and_conquer(points_list, queries)

    # Print summary of time taken by each method
    print("\nSummary of time taken for each search:")
    print(f"Total time taken for sequential search: {ss_time}")
    print(f"Average time taken for sequential search: {ss_time / len(queries)}\n")
    print(f"Total time taken for best first search: {bfs_time}")
    print(f"Average time taken for best first search: {bfs_time / len(queries)}\n")
    print(f"Total time taken for divide and conquer search: {dcs_time}")
    print(f"Average time taken for divide and conquer search: {dcs_time / len(queries)}\n")

if __name__ == '__main__':
    main()
