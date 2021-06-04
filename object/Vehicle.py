class Vehicle(object):
    def __init__(self, vehicle_id, parking_id, car_number, max_capacity, speed, working_time_list,
                 current_time_cost=0, current_capacity=0):
        """
        The initialization of the vehicle information.
        :param vehicle_id: The id of the vehicle.
        :param parking_id: The id of the parking where the vehicle start off.
        :param car_number: The license pate of the vehicle
        :param max_capacity: The max capacity of the vehicle and the unit is L.
        :param speed: The average speed of the vehicle and the unit is m/s.
        :param working_time_list: The list of the working time of the vehicle.  The format is likes that:
                [(float_1, float_2), ...]. If the working time is (7:30, 8:30), then it is (7.5, 8.5)
        :param current_time_cost: The current time cost of the vehicle including the time cost in the road and at the
                collection point.  The unit is s.
        :param current_capacity: The current capacity of the vehicle and the unit is L.
        """
        self.car_id = vehicle_id
        self.parking_id = parking_id
        self.car_number = car_number
        self.max_capacity = max_capacity
        self.speed = speed
        self.working_time_list = working_time_list
        self.current_time_cost = current_time_cost
        self.current_capacity = current_capacity
        self.time_index = 0
        self.total_time_cost = 0
        self.time_transfer(self.working_time_list[self.time_index])
        self.mileage_list = []
        self.route_dic = {}

    def time_transfer(self, time_tuple):
        self.total_time_cost = (time_tuple[1] - time_tuple[0]) * 3600

    def print_info(self):
        print('car_id = {}, parking_id = {}, car_number = {}, max_capacity = {}, speed = {}, working_time_list = {}, '
              'current_time_cost = {}, current_capacity = {}, total_time_cost = {}, total_mileage = {}, route_dic = {}'
              .format(self.car_id, self.parking_id, self.car_number, self.max_capacity, self.speed,
                      self.working_time_list, self.current_time_cost, self.current_capacity, self.total_time_cost,
                      sum(self.mileage_list), self.route_dic))