from PIL import Image, ImageColor
import random

def read_file(file):
    with open(file) as source_file:
        source_str = source_file.read()
        source_str = source_str.split("\n")
    
    source_two_d_list = []

    for line in source_str:
        if line.split() != []:
            source_two_d_list.append([int(_) for _ in line.split()])

    return source_two_d_list

class MapData:
    """class to hold topographical data for a map"""
    def __init__(self, data_file):
        self.data_file = data_file
        self.max_value = self.get_max()
        self.min_value = self.get_min()

    def get_width(self):
        return len(self.data_file[0])

    def get_length(self):
        return len(self.data_file)

    def get_grayscale_value(self, coord_x_y):
        max and min values, takes an x,y tuple returns an int for the
        """ gray of the point requested"""
        gray_value = (self.max_value - self.min_value) / 256
        return int((self.data_file[coord_x_y[1]][coord_x_y[0]]-self.min_value) / gray_value)

    def get_min(self):
        """returns the minimum value of the data_file"""
        list_of_mins = []
        for row in self.data_file:
            list_of_mins.append(min(row))
        return min(list_of_mins)

    def get_max(self):
        """returns the maximum value of the data_file"""
        list_of_maxes = []
        for row in self.data_file:
            list_of_maxes.append(max(row))
        return max(list_of_maxes)

    def get_value(self, coord_x_y):
        """takes a coord_x_y tuple and returns the elevation
        value, returning None if not found"""
        try:
            return self.data_file[coord_x_y[1]][coord_x_y[0]]
        except:
            return None

class MapImage:
    """class to hold map images generated from MapData"""
    def __init__(self, map_data):
        """build the map image in grayscale from the data"""
        self.map_data = map_data
        self.image = self.build_image()
    
    def show(self):
        """displays the MapImage"""
        self.image.show()

    def build_image(self):
        """builds the image in RGBA format, grayscale"""
        img = Image.new('RGBA', (self.map_data.get_width(), self.map_data.get_length()) )
        for x in range(self.map_data.get_width()):
            for y in range(self.map_data.get_length()):
                gray_value = self.map_data.get_grayscale_value((x,y))
                img.putpixel((x,y), (gray_value,gray_value,gray_value,255))
        return img
    
    def putpixel(self, column_row_tup, color="red"):
        """for drawing paths, defaults to red"""
        self.image.putpixel(column_row_tup,ImageColor.getcolor(color, "RGBA"))
        return None
    
    def save(self, path):
        """saves the image file to the passed path"""
        self.image.save(path)
        return None

class Pathfinder:
    def __init__(self, map_data, map_image):
        """loads a MapData, MapImage, and defaults"""
        self.map_data = map_data
        self.map_image = map_image
        self.curr_pos = (0,0)
        self.total_delta = 0
        self.path_record = []
    
    def set_start(self, coord_x_y):
        """resets the starting position to the passed coordinates
        and total_delta to 0, takes an (x,y) tuple"""
        self.curr_pos = (coord_x_y[0], coord_x_y[1])
        self.total_delta = 0
        self.path_record = []
        return None

    def get_x(self):
        return self.curr_pos[0]

    def get_y(self):
        return self.curr_pos[1]

    def get_greedy_potenitals(self):
        """returns the next 3 coord tuples for greedy in the
        order: up_right, right, down_right"""
        return (self.get_x()+1,self.get_y()+1), (self.get_x()+1, self.get_y()), (self.get_x()+1, self.get_y()-1)

    def find_greedy_path(self, color="cyan"):
        """finds the path by the greedy algorithm"""
        # draw the starting point
        self.map_image.putpixel(self.curr_pos)
        # move from left to right via the greedy algorithm
        for _ in range(self.map_data.get_width()-self.get_x()-1):
            up_right, right, down_right = self.get_greedy_potenitals()
            next_move_tup = self.get_greedy_move(up_right, right, down_right)
            self.curr_pos = next_move_tup
            self.map_image.putpixel(self.curr_pos, color)

    def get_greedy_move(self, up_right, right, down_right):
        curr_elevation = self.map_data.get_value(self.curr_pos)
        new_moves = {}
        new_elevation = self.map_data.get_value(up_right)
        if new_elevation is not None:
            new_moves[up_right] = abs(curr_elevation-new_elevation)
        new_elevation = self.map_data.get_value(right)
        if new_elevation is not None:
            new_moves[right] = abs(curr_elevation-new_elevation)
        new_elevation = self.map_data.get_value(down_right)
        if new_elevation is not None:
            new_moves[down_right] = abs(curr_elevation-new_elevation)
        right_move_list = sorted(new_moves.items(),key=lambda move: move[1])
        # if there's a tie
        if right_move_list[0][1]==right_move_list[1][1]:
        # and it's a three way tie
            if len(right_move_list) == 3 and right_move_list[0][1]==right_move_list[2][1]:
                right_move = right_move_list[random.randint(0,2)][0]
            # otherwise flip a coin
            else:
                right_move = right_move_list[random.randint(0,1)][0]
        # or choose the winner if it's clear
        else:
            right_move = right_move_list[0][0]
        self.total_delta += new_moves[right_move]
        self.path_record.append(right_move)
        return right_move

    def get_total_delta(self):
        """returns the total elevation change"""
        return self.total_delta

    def get_path_record(self):
        """returns the path record list of (x,y) tuples"""
        return self.path_record

    def retrace_path(self, path_list, color="blue"):
        """retraces a line by a list of tuples"""
        for coord in path_list:
            self.map_image.putpixel(coord, color)
        return None

#andys method  open the file and build the map objecs
file = "elevation_small.txt"
map_data = MapData(read_file(file))
map_image = MapImage(map_data)
pathfinder = Pathfinder(map_data,map_image)

# make a path for every y coordinate, recording them
delta_paths = {}
for y in range(map_data.get_length()):
    pathfinder.set_start((0,y))
    pathfinder.find_greedy_path()
    delta_paths[pathfinder.get_total_delta()] = pathfinder.get_path_record()
# sort them and choose the smallest delta
best_path = sorted(delta_paths.items(),key=lambda delta: delta[0])[0][1]

# redraw that line in red
pathfinder.retrace_path(best_path, "red")
map_image.show()
