import random
import numpy as np
import math
import copy
import matplotlib.pyplot as plt

# Simulated annealing class
class SimulatedAnnealing:
    max_distance = 10

    # Constructor
    # Accepts argument for which "type" of simulated annealing we are running
    # 1: Cost function just based on distance
    # 2: Cost function based on distance + population density
    # 3: Cost function based on distance + population density with a penalty on population density according to Euclidean distance
    # 4: Same cost function as 3 but with a different acceptance probability
    def __init__(self, type):
        self.type = type
        self.max_distance = 10

    # Calculates "cost" of a particular map by taking the average over all locations of minimum distance to another node
    def cost(self, map):
        # Get all dropoff zones of map
        dropoff_zones = map.dropoff_zones.keys()

        # Get all locations on the map
        coordinates = map.coordinates.keys()

        # Get the number of locations that we have and initialize a sum to take the average later
        num_coordinates = len(coordinates)
        sum = 0.0

        # Loop through locations on map
        for location in coordinates:
            # Initialize minimum distance
            min_distance = float('inf')

            # Loop through dropoff zones
            for zone in dropoff_zones:
                # If the neighbor is the same point, then skip
                if location == zone:
                    continue

                # Calculate Euclidean distance to neighbor
                distance = np.linalg.norm(np.subtract(location, zone))

                # Minimize over all distances
                min_distance = min(min_distance, distance)

            # Add minimum distance to sum
            population_density = map.coordinates[location]['population_density']

            if self.type == 1:
                sum += min_distance
            elif self.type == 2:
                sum += min_distance + population_density
            else:
                sum += min_distance + (min_distance / self.max_distance) * population_density

        # Return average of distances
        return sum / num_coordinates

    # Generates neighboring state of given map by randomly moving dropoff zones around until all locations are within an arbitrary distance from a dropoff zone
    def neighbor(self, map):
        # Check if all locations are within an arbitrary distance of a dropoff zone
        all_within_distance = False

        while not all_within_distance:
            all_within_distance = True

            # Swap a random dropoff zone in the map
            random_dropoff_zone = random.choice(map.dropoff_zones.keys())
            del map.dropoff_zones[random_dropoff_zone]
            map.add_random_dropoff_zone()

            # Get all coordinates of map
            coordinates = map.coordinates.keys()

            # Get all dropoff zones of map
            dropoff_zones = map.dropoff_zones.keys()

            # Loop through coordinates
            for location in coordinates:
                # Initialize minimum distance
                min_distance = float('inf')

                # Track if the location is within an arbitrary distance from a dropoff zone
                location_within_distance = False

                # Loop through neighbors
                for zone in dropoff_zones:
                    # If the neighbor is the same point, then skip
                    if location == zone:
                        continue

                    # Calculate Euclidean distance to neighbor
                    distance = np.linalg.norm(np.subtract(location, zone))

                    # Is this distance within the arbitrary distance?
                    if distance <= self.max_distance:
                        location_within_distance = True
                        break

                # If this location is not within the distance, then we must make another swap in the graph
                if not location_within_distance:
                    all_within_distance = False
                    break

        return map

    # Calculates acceptance probability for a new map solution
    def acceptance_probability(self, old_cost, new_cost, T):
        try:
            if new_cost <= old_cost:
                return 1
            else:
                if self.type == 4:
                    return math.exp((old_cost - new_cost) / T)
                if self.type == 3:
                    return math.exp((old_cost - new_cost) / 10000 / T)
                if self.type == 2:
                    return math.exp((old_cost - new_cost) / 10000 / T)
                else:
                    return math.exp((old_cost - new_cost) / T)
        except OverflowError:
            return float('inf')

    # Performs simulated annealing on a city map
    def anneal(self, map):
        # Get cost of the input
        old_cost = self.cost(map)
        initial_cost = self.cost(map)

        # Initialize annealing values
        T = 1.0
        T_min = 0.001
        decay = 0.9

        final_map = copy.deepcopy(map)

        iterations = 0
        graph_data = []

        # Iterate until we hit the max number of iterations
        while T > T_min:
            i = 1

            # Generate 100 unique neighbors
            while i <= 50:
                iterations += 1
                new_map = self.neighbor(map)
                new_cost = self.cost(new_map)
                ap = self.acceptance_probability(old_cost, new_cost, T)

                # If new solution is accepted then we update
                if ap >= .5:
                    map = copy.deepcopy(new_map)
                    final_map = copy.deepcopy(new_map)
                    old_cost = new_cost
                    graph_data.append((iterations, old_cost))

                i += 1

            T *= decay

        plt.clf()

        plt.xlim(0, iterations)
        plt.ylim(0, initial_cost)

        # Break up x and y coordinates into their own list
        try:
            x, y = zip(*graph_data)
            x = list(x)
            y = list(y)
        except ValueError:
            x = []
            y = []

        # Plot dropoff zones
        plt.plot(x, y, c='r')

        plt.savefig('results/graph_simulated_annealing_%d.png' % self.type)

        return final_map
