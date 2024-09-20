import os
import arcpy
import sqlite3
import zipfile
# import shutil


class SwmzFile:
    def __init__(self, db_path):
        self.db_path = db_path
        self.layers = self.fetch_all_layers()  # Fetch all layers from the feature_layers table

    def get_photos(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT uuid, remarks, photo_path FROM photos"
        cursor.execute(query)
        photos = cursor.fetchall()
        photos_list = [{'uuid': photo[0], 'remarks': photo[1], 'photo_path': photo[2]} for photo in photos]
        conn.close()
        return photos_list

    def fetch_all_layers(self):
        """
        Fetch all layers' UUID, name, and geometry type from the feature_layers table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query to get UUID, name, and geometry type from the feature_layers table
        query = "SELECT uuid, name, geom_type FROM feature_layers"
        cursor.execute(query)
        layers = cursor.fetchall()

        layer_list = [{'uuid': layer[0], 'name': layer[1], 'geom_type': layer[2].lower()} for layer in layers]

        conn.close()
        return layer_list

    def fetch_features(self, layer_uuid):
        """
        Fetch all features related to a specific layer from the features table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query to get all features associated with the layer's UUID
        query = "SELECT uuid, name FROM features WHERE layer_id = ?"
        cursor.execute(query, (layer_uuid,))
        features = cursor.fetchall()

        feature_list = [{'uuid': feature[0], 'name': feature[1]} for feature in features]

        conn.close()
        return feature_list

    def fetch_field_name(self, field_id):
        """
        Fetch all features related to a specific layer from the features table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query to get all features associated with the layer's UUID
        query = "SELECT layer_id, field_name FROM attribute_fields WHERE uuid = ?"
        cursor.execute(query, (field_id,))
        fields = cursor.fetchall()

        field_name = fields[0][1]

        conn.close()
        return field_name


    def fetch_attributes(self, feature_id):
        """
        Fetch all features related to a specific layer from the features table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query to get all features associated with the layer's UUID
        query = "SELECT field_id, value FROM attribute_values WHERE item_id = ?"
        cursor.execute(query, (feature_id,))

        attributes = cursor.fetchall()

        attribute_list = [{'field_name': self.fetch_field_name(attribute[0]), 'value': attribute[1]} for attribute in attributes]

        conn.close()
        return attribute_list




    def fetch_points(self, feature_uuid):
        """
        Fetch points (x, y, elevation) from the points table for a given feature UUID (fid).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query to get all points (x, y, elevation, seq) associated with the feature's UUID (fid)
        query = "SELECT lon, lat, elv, seq FROM points WHERE fid = ?"
        cursor.execute(query, (feature_uuid,))
        points = cursor.fetchall()

        point_data = [{'x': point[0], 'y': point[1], 'elevation': point[2], 'seq':point[3], 'fid':feature_uuid} for point in points]

        conn.close()
        return point_data

    def get_all_layer_data(self):
        """
        Loop through all layers in the database, fetch and return the data depending on the geometry type.
        """
        all_data = []

        for layer in self.layers:
            layer_data = {'layer_name': layer['name'], 'geom_type': layer['geom_type'], 'features': []}

            # Fetch all features for this layer
            features = self.fetch_features(layer['uuid'])

            for feature in features:
                points = self.fetch_points(feature['uuid'])
                attributes = self.fetch_attributes(feature['uuid'], )

                if attributes:
                    attribute_data = attributes
                else:
                    attribute_data = None

                if points:
                    feature_data = {'feature_name': feature['name'], 'attributes': attribute_data,'points': points}
                else:
                    feature_data = {'feature_name': feature['name'], 'attributes': attribute_data, 'points': None}

                layer_data['features'].append(feature_data)

            all_data.append(layer_data)

        return all_data
'''--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

def remove_special_characters(input_string):
        out_string = input_string.replace("'", "_").replace(" ", "_").replace(".", "_").replace("(", "_").replace(")", "_").replace(":", "_").replace(";", "_").replace("!", "_").replace("?", "_").replace("&", "_").replace("*", "_").replace("+", "_").replace("-", "_").replace("=", "_").replace("|", "_").replace("/", "_").replace("'", "_").replace('"', "_").replace(",", "_").replace("<", "_").replace(">", "_").replace("[", "_").replace("]", "_").replace("{", "_").replace("}", "_").replace("`", "_").replace("~", "_").replace("^", "_").replace("$", "_").replace("%", "_").replace("@", "_").replace("#", "_").replace("!", "_").replace("?", "_").replace("&", "_").replace("*", "_").replace("+", "_").replace("-", "_").replace("=", "_").replace("|", "_").replace("\\", "_").replace("/", "_").replace("'", "_").replace('"', "_").replace(",", "_").replace("<", "_").replace(">", "_").replace("[", "_")
        out_string = out_string.replace("__", "_")
        out_string = out_string.replace("__", "_")
        if len(out_string)>60:
            return out_string[:59]
        if not out_string[0].isalpha():
            out_string = "_"+ out_string
        return out_string

def lat_long_to_utm(longitude, latitude):
    # Calculate UTM zone
    utm_zone = int((longitude + 180) / 6) + 1

    # Determine if it's in the northern or southern hemisphere
    hemisphere = 'N' if latitude >= 0 else 'S'

    # Define EPSG code for UTM
    epsg_code = 32600 + utm_zone if hemisphere == 'N' else 32700 + utm_zone

    # Create a SpatialReference object for the calculated UTM zone
    sr_utm = arcpy.SpatialReference(epsg_code)

    # Create a PointGeometry object with WGS 84 (EPSG: 4326)
    point = arcpy.Point(longitude, latitude)
    sr_wgs84 = arcpy.SpatialReference(4326)
    point_geom = arcpy.PointGeometry(point, sr_wgs84)

    # Project the point to UTM
    point_utm = point_geom.projectAs(sr_utm)

    # Extract the X and Y coordinates in UTM
    x_utm = point_utm.centroid.X
    y_utm = point_utm.centroid.Y

    return [x_utm, y_utm]


def plot_points(layer_name, attributes, points):

    workspace = arcpy.env.workspace
    # print(workspace)
    # workspace = "D:/ArcgisPro_Projects/AlwyasTemp/Test.gdb"
    layer_name_edited = remove_special_characters(layer_name)

    fc_path = workspace + "/" + layer_name_edited
    print(layer_name_edited)

    if arcpy.Exists(fc_path):
        print("Layer already exists")
    else:
        feature_class = arcpy.management.CreateFeatureclass(workspace, layer_name_edited, "POINT", spatial_reference = arcpy.SpatialReference(4326))

        for field in attributes:
            field_name = remove_special_characters(field['field_name'])
            arcpy.management.AddField(feature_class, field_name, "TEXT")

    with arcpy.da.InsertCursor(fc_path, ['SHAPE@XY', *[remove_special_characters(field['field_name']) for field in attributes]]) as cursor:
        for point in points:
            x, y = point['x'], point['y']
            cursor.insertRow([(x, y), *[field['value'] for field in attributes]])
    return fc_path



def plot_lines(layer_name, attributes, points,f_name):

    workspace = arcpy.env.workspace
    # print(workspace)
    # workspace = "D:/ArcgisPro_Projects/AlwyasTemp/Test.gdb"
    layer_name_edited = remove_special_characters(layer_name)

    fc_path = workspace + "/" + layer_name_edited
    print(layer_name_edited)

    if arcpy.Exists(fc_path):
        pass
    else:
        feature_class = arcpy.management.CreateFeatureclass(workspace, layer_name_edited, "POLYLINE", spatial_reference = arcpy.SpatialReference(4326))

        for field in attributes:
            field_name = remove_special_characters(field['field_name'])
            arcpy.management.AddField(feature_class, field_name, "TEXT")


    with arcpy.da.InsertCursor(fc_path, ['SHAPE@', *[remove_special_characters(field['field_name']) for field in attributes]]) as cursor:
        array = arcpy.Array()
        sorted_points = sorted(points, key=lambda p: p['seq'])
        for point in sorted_points:
            # Create an array of points for the line
            for x,y in [(point['x'], point['y']),]:
                array.add(arcpy.Point(x, y))
        i = 0
        for i in range(array.count):
            i += 1
        polyline = arcpy.Polyline(array, spatial_reference=arcpy.SpatialReference(4326))
        # Insert the polyline geometry and attributes (length and name)
        cursor.insertRow([polyline, *[field['value'] for field in attributes]])

    return [fc_path, f_name, points, layer_name]



def plot_polygons(layer_name, attributes, points):
    workspace = arcpy.env.workspace
    # print(workspace)
    # workspace = "D:/ArcgisPro_Projects/AlwyasTemp/Test.gdb"
    layer_name_edited = remove_special_characters(layer_name)

    fc_path = workspace + "/" + layer_name_edited
    print(layer_name_edited)

    if arcpy.Exists(fc_path):
        print("Layer already exists")
    else:
        feature_class = arcpy.management.CreateFeatureclass(workspace, layer_name_edited, "POLYGON", spatial_reference = arcpy.SpatialReference(4326))

        for field in attributes:
            field_name = remove_special_characters(field['field_name'])
            arcpy.management.AddField(feature_class, field_name, "TEXT")


    with arcpy.da.InsertCursor(fc_path, ['SHAPE@', *[remove_special_characters(field['field_name']) for field in attributes]]) as cursor:
        array = arcpy.Array()
        sorted_points = sorted(points, key=lambda p: p['seq'])
        for point in sorted_points:
            # Create an array of points for the line
            for x,y in [(point['x'], point['y']),]:
                array.add(arcpy.Point(x, y))

        polygon_geom = arcpy.Polygon(array, spatial_reference=arcpy.SpatialReference(4326))
        # Insert the polyline geometry and attributes (length and name)
        cursor.insertRow([polygon_geom, *[field['value'] for field in attributes]])

    return fc_path

def attach_photos(swFile,dir_path, db_path):

    workspace = arcpy.env.workspace
    fc_path_photos = workspace + "/Photos"
    fc_path_photos_table = workspace + "/Photos_Table"
    feature_class = None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get all points (x, y, elevation, seq) associated with the feature's UUID (fid)
    query = "SELECT item_id, value, field_id FROM attribute_values WHERE data_type = 'Photo'"
    cursor.execute(query)
    points = cursor.fetchall()

    photos_from_point_data = [{'uuid': point[0], 'remarks': swFile.fetch_field_name(point[2]), 'photo_path': point[1]} for point in points]

    direct_photos = swFile.get_photos()

    photos_list = direct_photos + photos_from_point_data
    photos_list = [photo for photo in photos_list if len(photo['photo_path'])>0]
    if len(photos_list) == 0:
        arcpy.AddMessage("No photos found")
        return

    arcpy.AddMessage("Total "+ str(len(photos_list)) + " photos found")   # COUNT OF PHOTOS

    # arcpy.AddMessage([photo for photo in photos_list])
    All_Points = [swFile.fetch_points(photo['uuid'])[0] for photo in photos_list]
    unique_points ={item['fid']: item for item in All_Points}.values()


    '''------------------create Photos Feature Class---------------------'''

    if arcpy.Exists(fc_path_photos):
        # arcpy.AddMessage("----Photos Layer already exists----")
        arcpy.management.DisableAttachments(fc_path_photos) #Disabling already existing Attachments

    else:
        # arcpy.AddMessage("----Adding Photos Layer----")
        feature_class = arcpy.management.CreateFeatureclass(workspace, "Photos", "POINT", spatial_reference = arcpy.SpatialReference(4326))
        arcpy.management.AddField(feature_class, "uuid", "TEXT")
        arcpy.management.AddField(feature_class, "Remarks", "TEXT")
        arcpy.management.AddField(feature_class, "Photo_Path", "TEXT")

    ''' ---------------------Add Photos Data to Feature Class----------------------'''
    unique_check_list = []
    layer_count_not_added = 0
    for photo in photos_list:
        if photo['uuid'] not in unique_check_list:
                unique_check_list.append(photo['uuid'])
                Points = swFile.fetch_points(photo['uuid'])
                if len(Points) < 2:
                    for point in Points:
                        with arcpy.da.InsertCursor(fc_path_photos, ['SHAPE@XY', 'uuid', 'Remarks','Photo_Path']) as cursor:
                            x, y = point['x'], point['y']
                            print(x,y)
                            cursor.insertRow([(x, y), photo['uuid'], photo['remarks'], photo['photo_path']])
                else:
                    layer_count_not_added += 1

    arcpy.AddMessage("Total Photos Attached: "+ str(len(unique_check_list)-layer_count_not_added))

    ''' ----------------------------Create Photos Table------------------------------'''
    if arcpy.Exists(fc_path_photos_table):
        pass
    else:
        feature_class = arcpy.management.CreateTable(workspace, "Photos_Table")
        arcpy.management.AddField(fc_path_photos_table, "uuid", "TEXT")
        arcpy.management.AddField(fc_path_photos_table, "photo_path", "TEXT")

    ''' ----------------------------Add Photos Data to Photos Table------------------------------'''
    for photo in photos_list:
        with arcpy.da.InsertCursor(fc_path_photos_table, ['uuid', 'photo_path']) as cursor:
            cursor.insertRow([photo['uuid'],photo['photo_path']])


    arcpy.management.EnableAttachments(fc_path_photos)
    photo_path = dir_path +"/Photos"

    # edit = arcpy.da.Editor(workspace)
    # edit.startEditing(False, True)
    # edit.startOperation()

    arcpy.management.AddAttachments(
        in_dataset="Photos",
        in_join_field="uuid",
        in_match_table="Photos_Table",
        in_match_join_field="uuid",
        in_match_path_field="photo_path",
        in_working_folder=photo_path,
        )

    # edit.stopOperation()
    # edit.stopEditing(True)
    return fc_path_photos




if __name__ == '__main__':

    workspace = arcpy.env.workspace

    dir = workspace.split("\\")
    dir.pop()
    cwd = "/".join(dir)
    arcpy.AddMessage("Current Working Directory = " +cwd)

    # Get input parameters from ArcGIS Pro tool (db_path)

    swmz_path = arcpy.GetParameterAsText(0)

    arcpy.AddMessage("SWMZ Path = " + swmz_path)
    new_directory = "Extracted"
    dir_path = cwd+"/"+new_directory
    if os.path.exists(dir_path):
        # shutil.rmtree(dir_path + "/Projects")
        # arcpy.AddMessage("Existing Extraction Directory Found and Removed")
        # os.makedirs(dir_path)
        # arcpy.AddMessage("New Extraction Directory Created")
        # arcpy.AddMessage("-------------------------------------------")
        pass
    else:
        os.makedirs(dir_path)

    with zipfile.ZipFile(swmz_path,'r') as zip_ref:
        zip_ref.extractall(dir_path)

    # for root, dir, files in os.walk(dir_path):
    #     for file in files:
    #         if file.endswith('.swm2'):
    #             db_path = os.path.join(root, file)
    #             # arcpy.AddMessage(db_path)

    db_name = swmz_path.split('\\')[-1].split('.')[0] + '.swm2'
    db_path = dir_path + r"/Projects/"+ db_name
    arcpy.AddMessage("Database Name : "+ db_name)
    arcpy.AddMessage("----------------------------------------------------------")
    # db_path =r"C:\Users\Anil\Desktop\Projects\Paya Pani Katuwal ko Ghar cheu Kulo IP.swm2"
    list_point_fc_path = []
    list_line_fc_path = []
    list_polygon_fc_path = []
    line_points = []

    #create an swmz file object
    sw_file = SwmzFile(db_path)

    layer_data = sw_file.get_all_layer_data()
    # arcpy.AddMessage(layer_data)
    for layer in layer_data:
        i= 0
        for feature in layer['features']:
            if layer['geom_type'].lower() == 'point':
                if layer['features'][i]['attributes']:
                    a = plot_points(layer['layer_name'], layer['features'][i]['attributes'], layer['features'][i]['points'])
                else:
                    attrbutes = [{'field_name':'NO_FIELD', 'value':'NO DATA'}]
                    a = plot_points(layer['layer_name'], attrbutes, layer['features'][i]['points'])
                if a not in list_point_fc_path:
                    list_point_fc_path.append(a)
                i += 1

            elif layer['geom_type'].lower() == 'line':
                attributes = layer['features'][i]['attributes']
                if layer['features'][i]['attributes']:
                    b = plot_lines(layer['layer_name'], attributes, layer['features'][i]['points'], layer['features'][i]['feature_name'])
                else:
                    attrbutes = [{'field_name':'NO_FIELD', 'value':'NO DATA'}]
                    b = plot_lines(layer['layer_name'], attributes, layer['features'][i]['points'], layer['features'][i]['feature_name'])

                if b[0] not in list_line_fc_path:
                    list_line_fc_path.append(b[0])
                i += 1
                # arcpy.AddMessage(b)
                line_point_single = [b[1], b[2], b[3]]
                if line_point_single not in line_points:
                    line_points.append(line_point_single)

                # arcpy.AddMessage(line_point_single)
                # arcpy.AddMessage("---------------------------------------------")
                # arcpy.AddMessage(line_points)
                # plot_points("Canal", [{'field_name':'haha', 'value':'hahahaahahahaha'}],layer['features'][0]['points'])
            elif layer['geom_type'].lower() == 'polygon':
                attributes = layer['features'][i]['attributes']
                if layer['features'][i]['attributes']:
                    c = plot_polygons(layer['layer_name'], attributes, layer['features'][i]['points'])
                else:
                    attrbutes = [{'field_name':'NO_FIELD', 'value':'NO DATA'}]
                    c = plot_polygons(layer['layer_name'], attrbutes, layer['features'][i]['points'])
                if c not in list_polygon_fc_path:
                    list_polygon_fc_path.append(c)
                i += 1

            else:
                arcpy.AddMessage("Invalid Geometry Type")

        if remove_special_characters(layer['layer_name']) in [x.split('/')[-1] for x in list_point_fc_path] + [x.split('/')[-1] for x in list_line_fc_path] + [x.split('/')[-1] for x in list_polygon_fc_path]:
            arcpy.AddMessage(layer['layer_name']+" Added")

    # arcpy.AddMessage("Attaching Photos")
    fc_path_photos = attach_photos(sw_file,dir_path,db_path)

    '''Add Line Data in Table Format'''
    feature_class = None
    i = 1
    # arcpy.AddMessage(line_points)
    if len(line_points)>0:
        # arcpy.AddMessage("Line Points to TABLE")
        for line in line_points:
            points = line[1]
            # arcpy.AddMessage(points)
            table_name = remove_special_characters(line[0])
            if len(line[0])<1:
                table_name = remove_special_characters(line[2]) + str(i)
                i+=1
            feature_class = arcpy.management.CreateTable(workspace, table_name)
            arcpy.management.AddField(feature_class, "X", "DOUBLE")
            arcpy.management.AddField(feature_class, "Y", "DOUBLE")
            arcpy.management.AddField(feature_class, "Z", "DOUBLE")
            for point in points:
                utm_xy = lat_long_to_utm(point['x'], point['y'])                     #CONVERTING LAT LONG TO UTM X AND Y
                with arcpy.da.InsertCursor(feature_class, ['X', 'Y', 'Z']) as cursor:
                    cursor.insertRow([utm_xy[0], utm_xy[1], point['elevation']])

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    active_map = aprx.activeMap

    if active_map:
        for fc_path in list_point_fc_path:
            if fc_path.split("/")[-1] not in [layers.name for layers in active_map.listLayers()]:
                active_map.addDataFromPath(fc_path)
        for fc_path in list_line_fc_path:
            if fc_path.split("/")[-1] not in [layers.name for layers in active_map.listLayers()]:
                active_map.addDataFromPath(fc_path)
        for fc_path in list_polygon_fc_path:
            if fc_path.split("/")[-1] not in [layers.name for layers in active_map.listLayers()]:
                active_map.addDataFromPath(fc_path)

        if arcpy.Exists(workspace+"/Photos"):
            if fc_path_photos.split("/")[-1] not in [layers.name for layers in active_map.listLayers()]:
                active_map.addDataFromPath(fc_path_photos)
    arcpy.AddMessage("----------------------------------------------------------")
    arcpy.AddMessage("Import Completed")




