
# define a dictionary to store the road name and road code pairs
road_dict = {}

# define a function to generate the road code
def get_road_code(road_class, road_name):
    # check if the road name has already been assigned a road code
    if road_name in road_dict:
        return road_dict[road_name]
    else:
        # get the count of road codes that start with the same road class
        count = sum([1 for code in road_dict.values() if code.startswith(road_class)])
        # generate the new road code
        new_code = f"{road_class}{count+1:03d}"
        # add the road name and road code pair to the dictionary
        road_dict[road_name] = new_code
        return new_code


get_road_code(!Road_Class!, !Road_Name!)
