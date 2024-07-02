import sys
import numpy as np
import pandas as pd

train = pd.read_table(sys.argv[1])
test = pd.read_table(sys.argv[2])
result = sys.argv[3]

class Node:
    def __init__(self, children = None, attrib_list = None, attrib = None, attrib_value = None, value = None, count = None):
        self.children = children
        self.attrib_list = attrib_list
        self.attrib = attrib
        self.attrib_value = attrib_value
        self.value = value
        self.count = count

class DecisionTree:
    def __init__(self, train:pd.DataFrame, test:pd.DataFrame, result:str):
        self.train = train
        self.test = test
        self.result = result
        self.attrib_list = list(self.train.columns)[:-1]

    def entropy(self, target_col):
        elements, counts = np.unique(target_col, return_counts=True)
        entropy = -np.sum([(counts[i] / np.sum(counts)) * np.log2(counts[i] / np.sum(counts)) for i in range(len(elements))])
        
        return entropy

    def gain_ratio(self, data, attrib):
        total_info = self.entropy(data.iloc[:,-1])
        attrib_info = 0
        split_ratio = 0

        for value in data[attrib].unique():
            value_data = data.loc[data[attrib] == value]
            value_entropy = self.entropy(value_data.iloc[:, -1])
            value_probability = value_data[attrib].count() / data[attrib].count()
            attrib_info += value_probability * value_entropy
            split_ratio -= value_probability * np.log2(value_probability)

        gain = total_info - attrib_info
        gain_ratio = gain/split_ratio

        return gain_ratio

    # Choose attribute among the attrib_list using gain ratio
    def choose_attrib(self, data, attrib_list):
        max = 0
        choose_attrib = None

        for attrib in attrib_list:
            if max <= self.gain_ratio(data, attrib):
                max = self.gain_ratio(data, attrib)
                choose_attrib = attrib

        return choose_attrib

    # Make decision tree
    def make_tree(self, data, attrib_list):
        # Pure
        if len(np.unique(data.iloc[:, -1])) == 1:
            return Node(attrib_list = attrib_list, value = np.unique(data.iloc[:, -1])[0])
        
        # no remaining attrib -> majority
        elif len(attrib_list) == 0:
            majority = data.iloc[:,-1].value_counts().idxmax()
            return Node(attrib_list = attrib_list, value = majority)
        
        # Grow
        else:
            choose_attrib = self.choose_attrib(data, attrib_list)
            elements, counts = np.unique(data[choose_attrib], return_counts=True)
            node = Node(attrib_list = attrib_list, attrib = choose_attrib, children=[])
            for element in elements:
                child = self.make_tree(data.loc[data[choose_attrib]==element], [x for x in attrib_list if x != choose_attrib])
                child.attrib_value = element
                child.count = len(data.loc[data[choose_attrib]==element])
                node.children.append(child)

            return node
    
    # Determine the label for the input
    def decision(self, tree, input):
        while tree.value == None:
            attrib_value = input[tree.attrib]
            no_attrib_value = True
            
            # When attrib_value is exist
            for node in tree.children:
                if node.attrib_value == attrib_value:
                    tree = node
                    no_attrib_value = False
                    break
            
            # When attrib_value is not exist, choose major node
            if no_attrib_value == True:
                max = 0
                for node in tree.children:
                    if max <= node.count:
                        max = node.count
                        tree = node

        return tree.value

    # Make result
    def make_result(self):
        # Make tree
        tree = self.make_tree(self.train, self.attrib_list)

        # Apply class label
        self.test[self.train.columns[-1]] = [self.decision(tree, self.test.iloc[i,:]) for i in range(len(self.test))]

        # Result
        self.test.to_csv(self.result, sep='\t', index=False)


DT = DecisionTree(train, test, result)
DT.make_result()