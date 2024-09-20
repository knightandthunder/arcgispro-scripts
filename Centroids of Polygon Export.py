import arcpy
import os

def ExportPoints(in_layer, out_table, f_name):

    workspace = arcpy.env.workspace
    current_workspace = workspace.replace("\\", "/")

    # Set the input feature layer (replace 'your_layer' with the actual layer name)
    input_layer = in_layer

    # Set the field name from which you want to export values
    field_name = f_name

    # Set the output table (replace with your desired output table path)
    output_table = os.path.join(current_workspace +"/"+ out_table)

    # Create an empty list to store centroid coordinates and field values
    output_data = []

    # Start an UpdateCursor to iterate over selected polygons
    with arcpy.da.SearchCursor(input_layer, ["SHAPE@", field_name]) as cursor:
        for row in cursor:
            polygon = row[0]
            field_value = row[1]

            # Get the centroid of the polygon
            centroid = polygon.centroid

            # Extract x and y coordinates
            x = centroid.X
            y = centroid.Y

            # Append the values to the output list
            output_data.append((x, y, field_value))

    # Define the fields for the output table
    output_fields = ["X", "Y", field_name]

    # Create the output table
    arcpy.AddMessage(output_table)
    arcpy.management.CreateTable(current_workspace, out_table)

    # Add fields for X, Y, and the specified field
    arcpy.management.AddField(output_table, "X", "DOUBLE")
    arcpy.management.AddField(output_table, "Y", "DOUBLE")
    arcpy.management.AddField(output_table, field_name, "TEXT")  # Adjust field type as needed

    # Insert the centroid coordinates and field values into the table
    with arcpy.da.InsertCursor(output_table, output_fields) as insert_cursor:
        for data in output_data:
            insert_cursor.insertRow(data)

    arcpy.AddMessage("Table export complete.")



if __name__ == "__main__":

    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(2)
    param2 = arcpy.GetParameterAsText(1)

    ExportPoints(param0, param1,param2)