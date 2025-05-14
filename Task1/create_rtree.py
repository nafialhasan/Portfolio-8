import sys
import math

#B sets the maximum capacity for the number of data points or child nodes that each node can hold before it needs to split
B = 4

def main(points_list):
    """
    Constructs an R-tree from data points provided in the parking dataset. When main function from this file is called it triggers the
    development of RTree from parking dataset. This function takes each point and inserts it the rtree object maintaining B = 4 in all
    levels and smallest possible MBR creations.

    Args:
        points_list (list of dict): A list of coordinates with 'x' and 'y' keys in a dictionary from parking_dataset file.

    Returns:
        RTree: An instance of the RTree class that contains all the parking coordinates organized within the tree structure.
    """

    # create the root object of RTree from where the points insertion will be started
    rtree = RTree()
    
    for point in points_list: #insert data points from the root one by one 
        rtree.insert(rtree.root, point) 
 
    return rtree #return the final constructed rtree root with the location of all its childs


class Node(object): #node class
    """
    Foundation of RTree node that can be root, child node or leaf node and hold all the pertinent information. Leaf nodes contain data 
    points, while internal nodes will contain child nodes. Each node maintains a Minimum Bounding Rectangle (MBR) which is constantly 
    updated during the construction of the RTree as new data points are updated if overflow is found in number of child nodes or data 
    points in a leaf node.

    Attributes:
        id (int): To traceback and find any particular node if debugging is required
        child_nodes (list of Node): Child nodes for internal nodes.
        data_points (list of dict): Data points stored as dictionary of x and y coordinate for leaf nodes. If it's an internal node this
        list is empty.
        parent (Node): The parent node in the R-tree. `None` if this node is the root.
        MBR (dict): A dictionary representing the Minimum Bounding Rectangle with keys 'x1', 'y1', 'x2', 'y2'.
    """

    def __init__(self):
        """
        Initializes a new Node with default properties, preparing it either to hold data points (as a leaf) or to be linked to 
        child nodes (as an internal node). The MBR is initialized to undefined values.
        """

        self.id = 0
        # for internal nodes
        self.child_nodes = []
        # for leaf nodes
        self.data_points = []
        self.parent = None #only the root will have no parent after construction is done

        #values of coordinates has been set to -1, assuming all coordinate values will be larger than this.
        #after each point insertion MBR is updated for the associated nodes
        self.MBR = {
            'x1': -1,
            'y1': -1,
            'x2': -1,
            'y2': -1,
        }

    def perimeter(self):
        """
        Calculates the half-perimeter of the node's Minimum Bounding Rectangle (MBR). This metric is used during the insertion process to 
        determine which node would have the least perimeter increase if a new data point were added, helping to maintain optimal 
        tree balance. Only half perimeter has been calculated because this value apart from serving as a basis for comparison does not have
        other functional benefit in the program and multiplying 2 will not change any of the comparisons as both sides will be multiplied.

        Returns:
        float: The calculated half-perimeter of the MBR.
        """

        # only calculate the half perimeter here
        return (self.MBR['x2'] - self.MBR['x1']) + (self.MBR['y2'] - self.MBR['y1'])

    def is_overflow(self):
        """
        Determines whether the node exceeds the set threshold of data points or child nodes specified by B (branching factor). If the node 
        is a leaf, it checks the number of data points; if it's an internal node, it checks the number of child nodes.

        Returns:
            bool: True if the node contains more than B data points or child nodes, False otherwise.
        """

        #if node has no children then data points  are considered.
        if self.is_leaf():
            if self.data_points.__len__() > B: #Checking overflows of data points, B is the upper bound.
                return True
            else:
                return False
        
        #will run else if there are internal nodes. In this case data points list is empty.
        else:
            if self.child_nodes.__len__() > B: #Checking overflows of child nodes, B is the upper bound.
                return True
            else:
                return False

    def is_root(self):
        """
        Checks whether this node is the root of the R-tree.

        Returns:
            bool: True the value of parent is None, otherwise returns False.
        """

        #knowing if there is a parent is important while dealing with overflow
        if self.parent is None:
            return True
        else:
            return False

    def is_leaf(self):
        """
        Checks if the node is a leaf node by calculating number of internal nodes. For an internal node, there will be at least two childs or
        internal nodes.

        Returns:
            bool: True if number of child nodes is 0, False otherwise.
        """

        #all internal nodes must have at least two items in child_nodes list
        if self.child_nodes.__len__() == 0:
            return True
        else:
            return False

class RTree(object): #R tree class
    """
    This class handles the dynamic organization of the nodes

    Attributes:
        root (Node): The initial node of the R-tree, acting as the operator for all insertions and structural adjustments.
    """    

    def __init__(self):
        """        
        Initializes an R-tree by setting up a root node, ready for adding data points.
        """

        self.root = Node() #Create a root

    def insert(self, u, p): # insert p(data point) to u (MBR)
        """
        Inserts a data point into the R-tree, starting from the specified node. If the node is a leaf, the data point is added directly.
        If the node overflows as a result, overflow handling procedures are triggered. If it's not a leaf, the function recursively
        finds the appropriate subtree to continue the insertion, ensuring the data point is placed optimally to maintain low MBR enlargement.

        Args:
            node (Node): The node from which to start the insertion.
            data_point (dict): The data point to insert, typically a dictionary with 'x' and 'y' coordinates.

        Returns:
            None: This method modifies the R-tree structure in-place and does not return a value.
        """

        #determing if the passed node has any children. If not then data points will be considered, otherwise child nodes
        if u.is_leaf(): 
            self.add_data_point(u, p) #add the data point and update the corresponding MBR
            if u.is_overflow():
                self.handle_overflow(u) #handle overflow for leaf nodes
        else:
            v = self.choose_subtree(u, p) #choose a subtree to insert the data point to miminize the perimeter sum
            self.insert(v, p) #until the passed node is a leaf node keep continue to check the next layer recursively
            self.update_mbr(v) #update the MBR for inserting the data point

    def choose_subtree(self, u, p): 
        """
        Selects the most appropriate subtree to insert a new data point, minimizing the perimeter increase of the MBR. This selection is 
        crucial for maintaining the spatial efficiency of the R-tree. The method compares the increase in perimeter for each child node's 
        MBR and chooses the one with the smallest increase.

        Args:
            node (Node): The internal node from whose children the subtree will be chosen.
            data_point (dict): The data point that needs to be inserted.

        Returns:
            Node: The chosen child node that offers the least increase in perimeter if the data point were added.
        """

        if u.is_leaf(): #find the leaf and insert the data point
            return u
        else:
            min_increase = sys.maxsize #set an initial value
            best_child = None
            for child in u.child_nodes: #check each child to find the best node to insert the point 
                if min_increase > self.peri_increase(child, p): #is the increase in parameter for given node and point smaller
                    min_increase = self.peri_increase(child, p) #then change the min_increase
                    best_child = child #and update the best_child
            return best_child

    def peri_increase(self, node, p): # calculate the increase of the perimeter after inserting the new data point
        """
        Calculates the potential increase in the perimeter of a node's Minimum Bounding Rectangle (MBR) if a new data point were added.
        This function evaluates the hypothetical change in perimeter by considering the extents of the current MBR and the location of
        the new data point, aiding in the decision-making process for subtree selection during insertions.

        Args:
            node (Node): The node for which the perimeter increase needs to be calculated, typically a child in an internal node.
            data_point (dict): The new data point to be inserted, containing 'x' and 'y' coordinates.

        Returns:
            float: The calculated increase in perimeter that would result from adding the data point to the node's MBR. This value
            helps in choosing the subtree that would minimize spatial enlargement.
        """

        # new perimeter - original perimeter = increase of perimeter
        origin_mbr = node.MBR
        x1, x2, y1, y2 = origin_mbr['x1'], origin_mbr['x2'], origin_mbr['y1'], origin_mbr['y2']
        
        #the maximum and minimum x and y coordinates constructs a new MBR. Calculate perimeter increase from perimeter of new and original MBR
        increase = (max([x1, x2, p['x']]) - min([x1, x2, p['x']]) +
                    max([y1, y2, p['y']]) - min([y1, y2, p['y']])) - node.perimeter()
        return increase


    def handle_overflow(self, u):
        """
        Handles the overflow condition within a node by splitting the node into two when the number of child nodes or data points
        exceeds the maximum capacity defined by B. If the overflowing node is the root, a new root is created to accommodate the split.
        Otherwise, the split nodes are managed under the existing parent to maintain tree balance and ensure minimal area enlargement.

        Args:
            node (Node): The node that has exceeded its capacity and needs to be split.

        Returns:
            None: This method modifies the tree structure in-place by splitting the overflowing node and potentially creating a new root.
        """

        #get the best split of two MBR based on whether u is a leaf node or an internal node.
        u1, u2 = self.split(u) #u1 u2 are the two splits returned by the function "split"
        # if u is root, create a new root with s1 and s2 as its' children
        if u.is_root():
            new_root = Node() #this will replace the existing root. as a result data points are removed as well to be replaced by child nodes
            self.add_child(new_root, u1) 
            self.add_child(new_root, u2)
            self.root = new_root
            self.update_mbr(new_root)
        # if u is not root, delete u, and set s1 and s2 as u's parent's new children
        else:
            w = u.parent #parent from which u1 and u2 child nodes have been created
            # copy the information of s1 into u
            w.child_nodes.remove(u)
            self.add_child(w, u1) #link the two splits and update the corresponding MBR
            self.add_child(w, u2)
            if w.is_overflow(): #check the parent node recursively until B condition is satisfied
                #split might happen in multiple layers
                self.handle_overflow(w) 
            
    def split(self, u):
        """
        Splits an overflowing node into two separate nodes to maintain the balance and efficiency of the R-tree structure. This method 
        evaluates different splitting strategies based on the spatial distribution of the data points or child nodes within the node. 
        The split is optimized to minimize the combined perimeter of the resulting nodes, ensuring efficient space utilization and tree 
        balance. The function considers multiple dimensions and attempts to find the best possible split to minimize future overlap and 
        increase in perimeter.

        Args:
            node (Node): The node to be split, which has exceeded its capacity due to insertion.

        Returns:
            tuple: A pair of nodes resulting from the split, ensuring that each node does not exceed the maximum capacity and
            maintains a balanced distribution of data points or child nodes.

        Details:
            The method evaluates potential splits by sorting data points or child nodes by their 'x' and 'y' coordinates and then
            iteratively testing different split points. For each possible split, the method calculates the perimeter of the 
            hypothetical resulting nodes. The split that results in the lowest combined perimeter is chosen.
            
            The process includes:
            - For leaf nodes: Sorting data points based on their coordinates and testing each possible division from 0.4B to 1.2B (calculated using math.ceil) 
            of the total number of points, ensuring that each node adheres to the capacity constraints.
            - For internal nodes: Sorting child nodes by the coordinates of their MBRs and similarly testing for the optimal split point.
            
            After determining the best split, the parent-child relationships and the MBRs of the resulting nodes are updated accordingly.

        """

        # split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perimeter = sys.maxsize
        # u is a leaf node
        if u.is_leaf():
            m = u.data_points.__len__()
            # create two different kinds of divides
            divides = [sorted(u.data_points, key=lambda data_point: data_point['x']),
                       sorted(u.data_points, key=lambda data_point: data_point['y'])] #sorting the points based on X dimension and Y dimension
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations to find a near-optimal one
                    s1 = Node()
                    s1.data_points = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.data_points = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter(): 
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        # u is a internal node
        else:
            # create four different kinds of divides
            m = u.child_nodes.__len__()
            divides = [sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x1']), #sorting based on MBRs
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x2']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y1']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y2'])]
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations
                    s1 = Node()
                    s1.child_nodes = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.child_nodes = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        for child in best_s1.child_nodes:
            child.parent = best_s1
        for child in best_s2.child_nodes:
            child.parent = best_s2

        return best_s1, best_s2


    def add_child(self, node, child):
        """
        Adds a child node to an existing node's list of children and updates the MBR of the parent node to encompass the new child's MBR.
        This method ensures the spatial integrity of the tree by maintaining an encompassing MBR that accurately represents all its children.

        Args:
            node (Node): The parent node to which the child will be added.
            child (Node): The child node to be added to the parent node.

        Returns:
            None: This method updates the tree structure in-place by adding a child node and modifying the parent's MBR.
        """
            
        node.child_nodes.append(child) #add child nodes to the current parent (node) and update the MBRs. It is used in handeling overflows
        child.parent = node 
        #update the MBR to reflect the effect of adding a child
        if child.MBR['x1'] < node.MBR['x1']: 
            node.MBR['x1'] = child.MBR['x1']
        if child.MBR['x2'] > node.MBR['x2']:
            node.MBR['x2'] = child.MBR['x2']
        if child.MBR['y1'] < node.MBR['y1']:
            node.MBR['y1'] = child.MBR['y1']
        if child.MBR['y2'] > node.MBR['y2']:
            node.MBR['y2'] = child.MBR['y2']

    def add_data_point(self, node, data_point):
        """
        Adds a data point to a leaf node and updates the node's MBR to include this new point. This method is crucial for maintaining
        the accuracy of the spatial indexing as new data points are continuously added to the tree.

        Args:
            node (Node): The leaf node to which the data point will be added.
            data_point (dict): The data point to add, defined by a dictionary with 'x' and 'y' coordinates.

        Returns:
            None: Modifies the leaf node by adding a new data point and updating its MBR in-place.
        """
        
        #add data points to the leaf node
        node.data_points.append(data_point)

        #update the MBR to reflect the append of a new data point
        if data_point['x'] < node.MBR['x1']:
            node.MBR['x1'] = data_point['x']
        if data_point['x'] > node.MBR['x2']:
            node.MBR['x2'] = data_point['x']
        if data_point['y'] < node.MBR['y1']:
            node.MBR['y1'] = data_point['y']
        if data_point['y'] > node.MBR['y2']:
            node.MBR['y2'] = data_point['y']


    def update_mbr(self, node):
        """
        Updates the Minimum Bounding Rectangle (MBR) of a node to accurately represent all its child nodes or data points.
        This method is essential for the proper functioning of the R-tree, ensuring that each node's MBR correctly encompasses
        all spatial data it contains or references.

        Args:
            node (Node): The node whose MBR will be updated.

        Returns:
            None: Updates the node's MBR in-place to include all contained or referenced spatial data, ensuring accurate spatial indexing.
        """
        
        x_list = []
        y_list = []
        
        #dynamic way to updaye the MBR. For leaf node x and y coordinates of data points will be considered to update MBR 
        if node.is_leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        else: #for internal nodes x1, x2, y1  and y2 coordinates of all child nodes for that parent will be considered
            x_list = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_list = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
        new_mbr = { #min and max values of x and y is the MBR
            'x1': min(x_list),
            'x2': max(x_list),
            'y1': min(y_list),
            'y2': max(y_list)
        }
        node.MBR = new_mbr
