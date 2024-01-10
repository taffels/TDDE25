""" This file contains function and classes for the Artificial Intelligence used in the game.
"""

import math
from collections import defaultdict, deque

import pymunk
from pymunk import Vec2d
import gameobjects
# from ctf import shot_sound
import sounds

# NOTE: use only 'map0' during development!

# 3 degrees, a bit more than we can turn each tick
MIN_ANGLE_DIF = math.radians(3)


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """ Compute the difference between two angles.
    """
    return (angle1 % (2 * math.pi)) - (angle2 % (2 * math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank, game_objects_list, tanks_list, space, currentmap):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.space = space
        self.currentmap = currentmap
        self.flag = None
        self.max_x = currentmap.width - 1
        self.max_y = currentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.latest_shot_list = [0]
        self.update_grid_pos()

        self.allow_metalbox = False

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """ Main decision function that gets called on every tick of the game.
        """
        # for obj in self.game_objects_list:
        #     obj.update()
        #     obj.post_update()
        self.maybe_shoot()
        next(self.move_cycle)

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot.
        """
        tank_angle = self.tank.body.angle - (math.pi / 2)
        tank_position = self.tank.body.position
        start = Vec2d(-0.5 * math.cos(tank_angle) + tank_position[0], -0.5 * math.sin(tank_angle) + tank_position[1])
        end = Vec2d(tank_position[0] - self.currentmap.width * math.cos(tank_angle), tank_position[1] - self.currentmap.height * math.sin(tank_angle))
        radius = 0
        shape_filter = pymunk.ShapeFilter()
        raycast_segment = self.space.segment_query_first(
            start, end, radius, shape_filter)  # Creates a raycast

        if hasattr(raycast_segment, 'shape'):  # Check what the raycast returns
            if hasattr(raycast_segment.shape, 'parent'):
                game_object = raycast_segment.shape.parent
                if isinstance(game_object, gameobjects.Tank) or (isinstance(
                        game_object, gameobjects.Box) and (game_object.destructable or game_object.movable)):
                    if gameobjects.pygame.time.get_ticks(
                    ) - self.latest_shot_list[0] > 1000:
                        sounds.shot_sound.play()
                        self.game_objects_list.append(
                            self.tank.shoot(self.space))
                        self.latest_shot_list[0] = (
                            gameobjects.pygame.time.get_ticks())

    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """
        while True:
            self.update_grid_pos()
            path = self.find_shortest_path()
            if len(path) <= 1:
                # Allowing metal box
                self.allow_metalbox = True
                yield
                continue

            self.allow_metalbox = False
            path.popleft()
            goal_coord = path.popleft() + Vec2d(0.5, 0.5)
            yield

            target_angle = angle_between_vectors(
                self.tank.body.position, goal_coord)
            tank_angle = self.tank.body.angle
            diff_angle = periodic_difference_of_angles(tank_angle, target_angle)
            # self.tank.update()

            if diff_angle < -math.pi:  # Tank angle < -180 degrees
                self.tank.turn_left()
                # self.tank.update()

            elif 0 > diff_angle > -math.pi:  # 0 > Tank angle > -180
                self.tank.turn_right()
                # self.tank.update()

            elif math.pi > diff_angle > 0:  # 180 > Tank angle > 0
                self.tank.turn_left()
                # self.tank.update()

            else:  # Turns right
                self.tank.turn_right()
                # self.tank.update()

            while abs(diff_angle) >= MIN_ANGLE_DIF:  # While diff angle is larger than the angle diff
                diff_angle = periodic_difference_of_angles(
                    target_angle, self.tank.body.angle)
                # self.tank.update()
                yield
            self.tank.stop_turning()
            # self.tank.update()

            new_dist = goal_coord.get_distance(self.tank.body.position)
            current_dist = 1000

            while (new_dist - current_dist) <= 0:
                #Accelerates
                self.tank.accelerate()
                current_dist = goal_coord.get_distance(self.tank.body.position)
                yield
                new_dist = goal_coord.get_distance(self.tank.body.position)
                yield
            self.tank.stop_moving()
            yield

    def find_shortest_path(self):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """
        queue = deque()
        shortest_path = []
        source = self.grid_pos
        visited = set(source.int_tuple)
        node = self.get_tile_neighbors(source)
        queue.append((source, []))


        while len(queue) != 0:
            target, path = queue.popleft()
            neighbors = node
            if self.get_target_tile() == target:
                path.append(target)
                shortest_path = path
                break
            neighbors = self.get_tile_neighbors(target)
            for neighbor in neighbors:
                if neighbor.int_tuple not in visited:
                    queue.append((neighbor, path + [target]))
                    visited.add(neighbor.int_tuple)
        return deque(shortest_path)

    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.flag = self.get_flag()  # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
        if self.flag is None:
            # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible if it is grass
            or a wooden box.
        """
        neighbors = []  # Find the coordinates of the tiles' four neighbors
        position = coord_vec
        # "Creates" all the neighboring tiles of an ai tank
        right_neighbor = position + Vec2d(1, 0)
        left_neighbor = position + Vec2d(-1, 0)
        up_neighbor = position + Vec2d(0, -1)
        down_neighbor = position + Vec2d(0, 1)
        # Append all the neighboring tiles
        neighbors.append(right_neighbor)
        neighbors.append(left_neighbor)
        neighbors.append(up_neighbor)
        neighbors.append(down_neighbor)
        # Filter out the ones neighboring tiles that either is out of map
        # bounds or that isn't grass tile
        return filter(self.filter_tile_neighbors, neighbors)

    def filter_tile_neighbors(self, coord):
        """ Used to filter the tile to check if it is a neighbor of the tank.
        """
        # Checks if the tile is not either out of the map bounds and is not a box
        # if (coord[0] >= 0 and coord[0] <= self.currentmap.width-1) and (coord[1] >= 0 and coord[1] <= self.currentmap.height-1) and self.currentmap.boxAt(coord[0],coord[1]) == 0:
        #     return True
        # else: #This tile is not visitable
        #     return False
        tile = coord
        # If tile is outside the map
        if coord[0] > self.max_x or coord[1] > self.max_y or coord[0] < 0 or coord[1] < 0:
            return False
        box_type = self.currentmap.boxAt(tile[0], tile[1])
        if box_type == 1:  # Stone wall
            return False
        if box_type == 2:  # Wood box
            return True
        if box_type == 3:  # Metal box
            # returns True if allowed to pass through metalboxes
            return self.allow_metalbox
        else:  # The tile is grass and should thus be visitable
            return True

    def unfair_ai(self):
        if self.tank.flag is None:
            self.tank.max_speed = gameobjects.Tank.NORMAL_MAX_SPEED * 1.5
        else:
            self.tank.max_speed = gameobjects.Tank.NORMAL_MAX_SPEED * 1.2

        for obj in self.game_objects_list:
            if isinstance(obj, gameobjects.Bullet):
                bullet = obj
                if self.tank == bullet.parent:
                    bullet.max_speed = gameobjects.Bullet.BULLET_MAX_SPEED * 2
                    bullet.acceleration = gameobjects.Bullet.BULLET_ACCELERATION * 2

        self.tank.base_hp = 10
