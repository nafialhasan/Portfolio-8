# Portfolio 8: Spatial Data Algorithms - Nearest Neighbour and Skyline Search

This repository contains my solutions for **Portfolio 8** in the **Big Data Analytics course (COMP6210)**.  
The assignment focuses on implementing spatial data search algorithms, including **Nearest Neighbour Search** and **Skyline Search**, using **custom R-tree indexing and Python algorithms**.

## Contents

### Task 1: Nearest Neighbour Search

The objective of this task was to find the nearest facility for each query point using different search methods and compare their efficiency.

#### Approaches Implemented:
- **Sequential Scan:** Brute-force method by calculating Euclidean distance to all facilities.
- **Best First Search (BFS) with R-tree:** Efficient nearest neighbour search using custom R-tree indexing.
- **Divide-and-Conquer BFS with R-tree:** Splitting dataset into subsets and applying BFS separately, then merging results.

#### Files:
- `Task1/Task1.py`: Implementation of Nearest Neighbour Search algorithms.
- `Task1/create_rtree.py`: Custom R-tree creation module.
- `Task1/shop_dataset.txt`: Dataset containing shop/facility coordinates.
- `Task1/query_points.txt`: Dataset containing user query locations.
- `Task1/output_task1.txt`: Results of Nearest Neighbour Search methods.

### Task 2: Skyline Query Search

The objective of this task was to identify skyline points (non-dominated points) based on multiple attributes like cost and area.

#### Approaches Implemented:
- **Sequential Skyline Scan**
- **BBS Skyline Search with R-tree**
- **Divide-and-Conquer BBS Skyline Search**

#### Files:
- `Task2/Task2.py`: Implementation of Skyline Search algorithms.
- `Task2/create_rtree.py`: Custom R-tree creation module (reused).
- `Task2/city1.txt`: Dataset containing city facilities data.
- `Task2/output_task2_city1.txt`: Results and timings for Skyline Search methods.


## Tools and Technologies

- **Python**
- **Custom R-tree Implementation**
- **MrJob (MapReduce) for distributed processing (Task 1, additional analysis)**

## Contact Information

For any queries or further information, feel free to contact me at [nafialhasan@gmail.com](mailto:nafialhasan@gmail.com).  
You can also connect with me on [LinkedIn](https://www.linkedin.com/in/nafialhasan/).
