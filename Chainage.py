import arcpy
import os

def meters_to_degrees(meters, polyline): #----NOT USED HERE-----
    """
    Convert a distance in meters to degrees using the centroid of the polyline.

    :param meters: Distance in meters to convert.
    :param polyline: Polyline geometry.
    :return: Distance in degrees.
    """
    # Earth's radius in meters
    earth_radius = 6378137

    # Get the centroid of the polyline
    centroid = polyline.centroid

    # Extract the latitude from the centroid
    latitude = centroid.Y

    # Convert latitude to radians
    lat_rad = latitude * (3.14159265358979 / 180)

    # Calculate the change in degrees
    degrees = (meters / (earth_radius * arcpy.sa.Cos(lat_rad))) * (180 / 3.14159265358979)

    return degrees

def plot_chainage(input_line_feature, output_point_feature, chainage_int):

    # Set environment settings
    arcpy.env.overwriteOutput = True

    current_workspace = arcpy.env.workspace
    input_polyline = input_line_feature
    output_points = os.path.join(current_workspace +"/"+ output_point_feature)
    distance_interval = int(chainage_int)                        # Distance in meters
    sr_wgs84 = arcpy.SpatialReference(4326)         # WGS 1984
    sr_utm45 = arcpy.SpatialReference(32645)        # Web Mercator for distance calculation

    # Create a feature class for the output points
    arcpy.management.CreateFeatureclass(current_workspace, out_name=output_point_feature, geometry_type="POINT", spatial_reference=sr_wgs84)

    # Add 'chainage' field to store the cumulative distance
    arcpy.management.AddField(output_points, "chainage", "TEXT")

    in_memory_fc = "in_memory/reprojected_polyline"
    projected_polyline_in_memory = arcpy.Project_management(input_polyline, in_memory_fc, sr_utm45)  # current_workspace + "/Projected_" + input_polyline


    # Cursor for writing to the output points feature class
    with arcpy.da.InsertCursor(output_points, ["SHAPE@", "chainage"]) as cursor:
        with arcpy.da.SearchCursor(projected_polyline_in_memory, ["SHAPE@"]) as polyline_cursor:
            for row in polyline_cursor:
                polyline = row[0]
                length = polyline.getLength('PLANAR','METERS')  # Calculate geodesic length in meters
                arcpy.AddMessage(length)
                num_points = int(length // distance_interval) + 1
                if (length % distance_interval)>0:
                    num_points =  int(length // distance_interval) + 2 # Number of points to create

                for i in range(num_points):
                    distance_along = i * distance_interval

                    if distance_along > length:
                        distance_along = length

                    # Get the point at the specified distance along the polyline
                    point = polyline.positionAlongLine(distance_along, use_percentage=False) #meters_to_degrees(distance_along,polyline)

                    # Calculate the chainage in 0+000 format
                    km = int(distance_along // 1000)
                    meters = int(distance_along % 1000)
                    chainage = f"{km}+{meters:03d}"

                    # Insert the point and chainage into the output points feature class
                    cursor.insertRow([point, chainage])

        arcpy.AddMessage("Point creation along polylines completed.")


    aprx = arcpy.mp.ArcGISProject("CURRENT")
    active_map = aprx.activeMap
    # Add the output points feature class to the map

    active_map.addDataFromPath(output_points)

    # enable label in layer
    layer = active_map.listLayers(output_point_feature)[0]
    layer.showLabels = True

    return


if __name__ == "__main__":

    input_layer = arcpy.GetParameterAsText(0)
    output_layer = arcpy.GetParameterAsText(1)
    interval = arcpy.GetParameterAsText(2)

    plot_chainage(input_layer, output_layer, interval)