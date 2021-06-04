# !/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：M3CVRP
@Author  ：Ziyuan Ye
@Email   : yezy2020@mail.sustech.edu.cn
@Date    ：6/3/2021 3:23 PM
'''

from object.Dataloader import DataLoader
import time
import copy
from docplex.mp.model import *
import numpy as np
import math
import sys

num_vehicle = 2
num_trip = 2
car_capacity = [72000] * num_vehicle
car_time = [8] * num_vehicle


class cplex_m3cvrp(object):
    def __init__(self, distance_file_path: str, vehicle_file_path: str, collection_file_path: str,
                 parking_file_path: str, dropping_file_path: str):

        self.data_loader = DataLoader(vehicle_file_path=vehicle_file_path,
                                      collection_point_file_path=collection_file_path,
                                      parking_file_path=parking_file_path,
                                      dropping_file_path=dropping_file_path,
                                      distance_file_path=distance_file_path)
        # the list of the id of the all collection points
        self.total_collection_point = list(
            self.data_loader.collection_data.keys())
        # the list of the id of the all vehicles
        self.all_vehicle_id_list = list(self.data_loader.vehicle_data.keys())
        # the dictionary of the parking to its own vehicles
        self.parking_vehicles_dic = {}
        for p in self.data_loader.parking_data.keys():
            self.parking_vehicles_dic[p] = []
        for v in self.all_vehicle_id_list:
            self.parking_vehicles_dic[self.data_loader.vehicle_data[v].parking_id].append(
                v)
        # the threshold of the method classify_collection_point
        self.threshold = 200
        # the additional time threshold of the working time of the vehicle
        self.time_threshold = 0


def cplex_solver():
    start_time = time.time()
    mdl = Model(name="M3CVRP")

    # ================================ Initialization ================================
    data = cplex_m3cvrp(
        # distance_file_path='data/1_rebuttal_dataset/30sites_distance.csv',
        # distance_file_path='data/1_rebuttal_dataset/40sites_distance.csv',
        # distance_file_path='data/1_rebuttal_dataset/50sites_distance.csv',
        distance_file_path='data/1_rebuttal_dataset/60sites_distance.csv',
        # distance_file_path='data/1_rebuttal_dataset/70sites_distance.csv',
        # distance_file_path='data/big_data/small_data_distance.csv',
        # distance_file_path='data/big_data/mid_data_distance.csv',
        #    distance_file_path='data/big_data/FinalResult.csv',
        vehicle_file_path='data/big_data/VehicleData4.json',
        #   collection_file_path='data/big_data/ExtractPoints.json',
        # collection_file_path='data/1_rebuttal_dataset/30sites.json',
        # collection_file_path='data/1_rebuttal_dataset/40sites.json',
        # collection_file_path='data/1_rebuttal_dataset/50sites.json',
        collection_file_path='data/1_rebuttal_dataset/60sites.json',
        # collection_file_path='data/1_rebuttal_dataset/70sites.json',
        #    collection_file_path='data/big_data/small_data_set.json',
        # collection_file_path='data/big_data/mid_data_set.json',
        parking_file_path='data/big_data/ParkingLots.json',
        dropping_file_path='data/big_data/Dropping.json')

    collection_key = list(data.data_loader.collection_data.keys())
    collection_data = data.data_loader.collection_data

    depots_name = list(data.data_loader.parking_data.keys())
    depots_index = []
    for i in depots_name:
        depots_index.append(int(data.data_loader.position_index_dic[i]))

    dump_name = list(data.data_loader.dropping_data.keys())
    dumps_index = []
    for i in dump_name:
        dumps_index.append(int(data.data_loader.position_index_dic[i]))

    time_matrix = data.data_loader.time_matrix

    distance_mat = data.data_loader.distance_matrix
    inf = np.inf
    for i in range(distance_mat.shape[0]):
        distance_mat[i][i] = inf\

    num_vertex = distance_mat.shape[0]
    judge_list = [(k, t, i, j) for k in range(num_vehicle) for t in range(num_trip)
                  for i in range(num_vertex) for j in range(num_vertex)]
    judge_dict = mdl.binary_var_dict(judge_list, name="x")

    u_list = [(k, i) for k in range(num_vehicle)
              for i in range(num_vertex)]  # avoid loop
    u_dict = mdl.continuous_var_dict(u_list, name="u")

    collection_index = [i for i in range(num_vertex - 6)]

    service_cost_list = [0] * (num_vertex)
    for c_key in collection_key:
        service_cost_list[data.data_loader.position_index_dic[c_key]
        ] = collection_data[c_key].server_cost / 3600

    # ================================ target function ================================
    mdl.minimize(mdl.sum(distance_mat[i][j] * judge_dict[k, t, i, j]
                         for k in range(num_vehicle) for t in range(num_trip)
                         for i in range(num_vertex) for j in range(num_vertex)))

    # ================================ constraints for judge matrix ================================

    # constraint1: All collection site only can be served once. All the collection sites should be served.
    for j in collection_index:
        obj1 = mdl.sum(judge_dict[k, t, i, j]
                       for k in range(num_vehicle) for t in range(num_trip)
                       for i in range(num_vertex))
        mdl.add_constraint(obj1 == 1)

    # constraint2: All vehicles should depart form the depot in their first trip.
    for k in range(num_vehicle):
        obj2 = mdl.sum(judge_dict[k, 0, i, j]
                       for i in depots_index
                       for j in collection_index)
        mdl.add_constraint(obj2 == 1)

    # constraint3: All vehicles will not go the depot except the last trip.
    for k in range(num_vehicle):
        for t in range(num_trip - 1):
            obj_2 = mdl.sum(judge_dict[k, t, i, j]
                            for i in range(num_vertex)
                            for j in depots_index)
            mdl.add_constraint(obj_2 == 0)

    # constraint4: All vehicles will not go to dump site when they are in depots.
    for k in range(num_vehicle):
        for t in range(num_trip):
            obj__2 = mdl.sum(judge_dict[k, t, i, j]
                             for i in depots_index
                             for j in dumps_index)
            mdl.add_constraint(obj__2 == 0)

    # constraint5: For all vehicles, except the last trip, the dumping site where the vehicle went in the previous trip
    # will be the beginning of the next trip.
    for k in range(num_vehicle):
        for t in range(num_trip):
            obj3 = mdl.sum(judge_dict[k, t, i, j]
                           for i in collection_index
                           for j in dumps_index)
            mdl.add_constraint(obj3 == 1)

    # constraint6: All trips must have one and only one path from the collection site to the dump site.
    for k in range(num_vehicle):
        for t in range(num_trip - 1):
            for j in dumps_index:
                pre_obj = mdl.sum(judge_dict[k, t, i, j]
                                  for i in range(num_vertex))
                succeed_obj = mdl.sum(
                    judge_dict[k, t + 1, j, i] for i in collection_index)
                mdl.add_constraint(pre_obj == succeed_obj)

    # constraint7: On the last trip of all vehicles, they will definitely go to the dump site before going to the depot.
    for k in range(num_vehicle):
        obj4 = mdl.sum(judge_dict[k, num_trip - 1, i, j]
                       for i in dumps_index for j in depots_index)
        mdl.add_constraint(obj4 == 1)

    # constraint8: The dump site constraint in the last trip.
    for k in range(num_vehicle):
        for j in dumps_index:
            pre_obj = mdl.sum(judge_dict[k, num_trip - 1, i, j]
                              for i in range(num_vertex))
            succeed_obj = mdl.sum(
                judge_dict[k, num_trip - 1, j, i] for i in depots_index)
            mdl.add_constraint(pre_obj == succeed_obj)

    # constraint9: The vehicle will not go to any site after returning to the depot in the last trip.
    for k in range(num_vehicle):
        obj5 = mdl.sum(judge_dict[k, num_trip - 1, i, j]
                       for i in depots_index for j in range(num_vertex))
        mdl.add_constraint(obj5 == 0)

    # ========================== Variables Constraints ==========================
    # constraint10: Except for the first trip, the vehicles from the dump sites,
    # besides going to the depot, may also visit one or more collection sites.
    for k in range(num_vehicle):
        for t in range(1, num_trip):
            obj6 = mdl.sum(judge_dict[k, t, i, j]
                           for i in dumps_index for j in collection_index)
            mdl.add_constraint(obj6 <= 1)

    # constraint11: There is a collection sites visited, there must be a path from it.
    for k in range(num_vehicle):
        for t in range(num_trip):
            for line in collection_index:
                obj_col = mdl.sum(
                    judge_dict[k, t, i, line] for i in range(num_vertex))
                obj_row = mdl.sum(
                    judge_dict[k, t, line, i] for i in range(num_vertex - 3))
                mdl.add_constraint(obj_col == obj_row)

    # constraint12: Vehicles cannot directly visit the depot after visiting any collection point
    mdl.add_constraint(mdl.sum(judge_dict[k, t, i, j]
                               for k in range(num_vehicle)
                               for t in range(num_trip)
                               for i in collection_index
                               for j in depots_index) == 0)

    # ========================== Time Constraints & Loading Constraints ============================
    # constraint13: Time Constraints
    for k in range(num_vehicle):
        obj9 = mdl.sum(judge_dict[k, t, i, j] *
                       (time_matrix[i][j] + service_cost_list[j])
                       for t in range(num_trip)
                       for i in range(num_vertex)
                       for j in range(num_vertex)
                       )
        mdl.add_constraint(obj9 <= car_time[k])

    # constraint14: Loading Constraints
    for k in range(num_vehicle):
        for t in range(num_trip):
            obj10 = mdl.sum(judge_dict[k, t, i, j] *
                            collection_data[data.data_loader.index_id_dic[j]
                            ].point_capacity
                            for i in range(num_vertex)
                            for j in collection_index)
            mdl.add_constraint(obj10 <= car_capacity[k])

    # ========================== Avoid self-loop ============================
    # constraint15: Avoid loop u_{k,i} \geq u_{k,j} + 1 - inf(1-\sum_{t \in trip}x_{k,t,i,j})
    #                       u_{k,i} \geq 0
    large_num = 100000
    mid_num = large_num / num_vertex - 1
    for k in range(num_vehicle):
        for i in range(num_vertex):
            for j in range(num_vertex - 6):
                obj11 = mdl.sum(judge_dict[k, t, i, j] for t in range(num_trip))
                mdl.add_constraint(u_dict[k, i] >= u_dict[k, j] + 1 - large_num * (1 - obj11))

    for k in range(num_vehicle):
        for i in range(num_vertex):
            mdl.add_constraint(u_dict[k, i] >= 0)

    for k in range(num_vehicle):
        for i in range(num_vertex):
            mdl.add_constraint(u_dict[k, i] <= num_vertex + mid_num)

    # constraint16: depot can not have self-loop

    for k in range(num_vehicle):
        for t in range(num_trip):
            obj12 = mdl.sum(judge_dict[k, t, i, j]
                            for i in depots_index
                            for j in depots_index)
            mdl.add_constraint(obj12 == 0)

    # constraint17: dumps can not have self-loop
    for k in range(num_vehicle):
        for t in range(num_trip):
            obj13 = mdl.sum(judge_dict[k, t, i, j]
                            for i in dumps_index
                            for j in dumps_index)
            mdl.add_constraint(obj13 == 0)

    # ================================ Result Evaluation ================================
    # mdl.print_information()
    mdl.solve()
    mdl.print_solution()
    print(mdl.objective_value)
    end_time = time.time()
    print("\n", "final time cost = ", end_time - start_time)

    # result demonstration
    count = num_vertex ** 2 * num_trip
    f = "small.txt"
    np.set_printoptions(threshold=np.inf)

    for k in range(num_vehicle):
        temp_array = np.zeros(count).reshape(num_trip, num_vertex, num_vertex)
        print(temp_array.shape)
        index = 0
        temp_i = []
        temp_j = []
        for t in range(num_trip):
            for i in range(num_vertex):
                for j in range(num_vertex):
                    if judge_dict[k, t, i, j].solution_value == 1:
                        temp_i.append(i)
                        temp_j.append(j)
                        if j < 200:
                            index += 1
                        temp_array[t][i][j] = 1
        print("the vehicle {}'s i are {}".format(k, temp_i))
        print("the vehicle {}'s j are {}".format(k, temp_j))
        # with open(f,"a+") as file:
        #     file.write("\n current vehicle is {}, current solution is \n {}".format(k,temp_array))
        # print("\n current vehicle is {}, current solution is \n {}".format(k,None))
        print("index = ", index)


if __name__ == '__main__':
    start = time.time()
    cplex_solver()
