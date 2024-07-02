import sys
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

input = pd.read_table(sys.argv[1], header=None, names=["idx", "X","Y"])
cluster_n = int(sys.argv[2]) # 넘으면 적은 클러스터 제거
Eps = int(sys.argv[3])
MinPts = int(sys.argv[4])

class DBSCAN:
    def __init__(self, input:pd.DataFrame, cluster_n:int, Eps:int, MinPts:int):
        self.input = input
        self.cluster_n = cluster_n
        self.Eps = Eps
        self.MinPts = MinPts
        self.cluster_label = 0
        self.labels = np.full(len(input), -1) # -1 : undefined
    
    def rangeQuery(self, point_idx):
        point = self.input.iloc[point_idx,[1,2]].values.reshape(1,-1)
        distances = cdist(point, self.input.iloc[:,[1,2]].values, metric="euclidean") # L2 norm
        self.input["dist"] = distances.flatten()
        return list(self.input[self.input["dist"]<self.Eps]["idx"]) # index of neighbors

    def makeLabels(self):
        for point_idx in range(len(self.input)):
            if self.labels[point_idx] != -1:
                continue

            neighbors = self.rangeQuery(point_idx)

            if len(neighbors) < self.MinPts:
                self.labels[point_idx] = 0 # 0 : Noise
                continue

            self.cluster_label += 1
            self.labels[point_idx] = self.cluster_label
            neighbors.remove(point_idx)
            seeds = neighbors[:] # make seeds

            for seed_idx in seeds: # expanding neighbors & labeling
                if self.labels[seed_idx] == 0:
                    self.labels[seed_idx] = self.cluster_label

                if self.labels[seed_idx] != -1:
                    continue

                neighbors = self.rangeQuery(seed_idx)
                self.labels[seed_idx] = self.cluster_label

                if len(neighbors) < self.MinPts:
                    continue

                new = set(neighbors) - set(seeds) # remove dup
                seeds.extend(new)

    def makeFile(self):
        self.makeLabels()
        self.input["label"] = self.labels
        label_counts = self.input["label"].value_counts()
        sorted_index_dict = {value: self.input.index[self.input["label"] == value].tolist() for value in label_counts.index}
        cnt = 0
        file_name = sys.argv[1][:-4]
        for label, index in sorted_index_dict.items():
            if int(label) == 0:
                continue
            temp = pd.DataFrame(index)
            temp.to_csv(file_name+'_cluster_%d.txt' % cnt, index=False, header = None) # output format : input#_cluster_i.txt 
            cnt+= 1
            if cnt == self.cluster_n: # max number of clusters
                break

dbscan = DBSCAN(input, cluster_n, Eps, MinPts)
dbscan.makeFile()