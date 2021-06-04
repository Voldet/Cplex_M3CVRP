class Points(object):
    def __init__(self, point_id, lat, lng, server_cost, point_capacity, point_type, working_time_list, name=None):
        """
        The initialization of the points including collection points, parking, and dropping points.
        :param point_id: The id of the point.
        :param lat: The latitude of the point.
        :param lng: The longitude of the point.
        :param server_cost: The server time cost of the point.
        :param point_capacity: The capacity of the point.
        :param point_type: The type of the point. 2 -> parking, 3 -> collection point, 4 -> dropping point.
        :param working_time_list: The list of the working time of the vehicle.  The format is likes that:
                [(float_1, float_2), ...]. If the working time is (7:30, 8:30), then it is (7.5, 8.5)
        """
        self.point_id = point_id
        self.lat = lat
        self.lng = lng
        self.server_cost = server_cost
        self.point_capacity = point_capacity
        self.point_type = point_type
        self.working_time_list = working_time_list
        self.name = name

    def type_transfer(self):
        if self.point_type == 2:
            return 'parking'
        elif self.point_type == 3:
            return 'collection point'
        elif self.point_type == 4:
            return 'dropping point'
        else:
            raise Exception('No this type of the point.')

    def print_info(self):
        print('point_id = {}, lat = {}, lng = {}, server_cost = {}, point_capacity = {}, point_type = {}, '
              'working_time_list = {}, name = {}'.format(self.point_id, self.lat, self.lng, self.server_cost,
                                                         self.point_capacity, self.type_transfer(),
                                                         self.working_time_list, self.name))