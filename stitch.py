import bpy
import csv
import sys

###################################Get Selected Images Starts###################  

#Get two closest numbers
def almostEqual(a, b):
    eps = 10**-2
    return abs(a - b) < eps

#Get bag time list according to distance series
def get_bag_time_list(path):
    # Set the distance in blender between the camera panes
    pane_x_distance = 0.9369

    # Set the distance in odometry (meters) between camera images
    pipe_photo_interval = 0.2794 
    bag_time_list = []
    odom_csv_location = path + "/odometry_filtered.csv"

    #Read the odometry CSV, get bag time needed for images
    odom_csv = csv.reader(open(odom_csv_location, "r"), delimiter=",")
    j = 0
    for idx, content in enumerate(odom_csv):
        if(idx == 0):
            continue
        location = float(content[7])
        bag_time = int(float(content[0]))
        if(almostEqual(j*pipe_photo_interval, location)):
            bag_time_list.append(bag_time)
            j += 1
    return bag_time_list

#correspond bag time with image name
def get_image_list(path, bag_time_list):
    img_csv = csv.reader(open(path, "r"), delimiter=",")
    img_name_list = []
    j = 1
    for idx, content in enumerate(img_csv):
        if(idx == 0):
            continue
        bag_time = int(float(content[0]))
        img_name = content[-1]
        if(j < len(bag_time_list) and bag_time == bag_time_list[j]):
            img_name_list.append(img_name)
            j += 1
    return img_name_list

#Pack four kinds of images as a dictionary 
def get_selected_imags(bag_path):
    #get bag time list
    bag_time_list = get_bag_time_list(bag_path)
    
    #set images path
    white_left_location = bagFolder + "/left_white_image_raw_compressed.csv"
    white_right_location = bagFolder + "/right_white_image_raw_compressed.csv"
    uv_left_location = bagFolder + "/left_uv_image_raw_compressed.csv"
    uv_right_location = bagFolder + "/right_uv_image_raw_compressed.csv"
    
    #get images lists
    white_left_imgs = get_image_list(white_left_location, bag_time_list)
    white_right_imgs = get_image_list(white_right_location, bag_time_list)
    uv_left_imgs = get_image_list(uv_left_location, bag_time_list)
    uv_right_imgs = get_image_list(uv_right_location, bag_time_list)

    #set output dictionary
    imgs = dict()
    imgs["white"] = dict()
    imgs["white"]["left"] = white_left_imgs
    imgs["white"]["right"] = white_right_imgs
    imgs["uv"] = dict()
    imgs["uv"]["left"] = uv_left_imgs
    imgs["uv"]["right"] = uv_right_imgs

    return imgs
###################################Get Selected Images Ends##################### 

###################################Stitch Images Starts#########################       

#Setup for Blender
def setup():
    #variables for stitching
    global pane_x_distance
    pane_x_distance = 0.9369
    global pane_z_distance
    pane_z_distance = 3.03562
    global left_pane_name
    left_pane_name = "Left Camera Texture"
    global right_pane_name
    right_pane_name = "Right Camera Texture"

    #feed bag file folder path from terminal
    global bagFolder
    argv = sys.argv
    bagFolder = str(argv[argv.index("--") + 1:][0])
    #bagFolder = "/Users/lili/Desktop/peipei_data_2017-08-09-19-57-12"

    global imgs
    imgs = get_selected_imags(bagFolder)
    global numOfImgsSelected
    numOfImgsSelected = len(imgs["uv"]["left"])

    #set camera orthograpic scale value
    bpy.data.cameras['Camera'].ortho_scale = numOfImgsSelected

    #set camera position
    bpy.data.objects['Camera'].location[0] = pane_x_distance + float(0.46845 * numOfImgsSelected)#5.15295
    bpy.data.objects['Camera'].location[1] = - numOfImgsSelected

    #set scene resolution
    bpy.data.scenes['Scene'].render.resolution_x = 937 * numOfImgsSelected
    bpy.data.scenes['Scene'].render.resolution_y = 6072


def unwarpImg(imgType, offset):
    #For left images stitching
    left_imgs = imgs[imgType]["left"]
    bpy.data.objects['Camera'].location[2] = offset
    i = 1
    for img in left_imgs:
        #unselect all objects 
        for obj in bpy.data.objects:
            obj.select = False

        # Add a left camera pane on top
        bpy.data.objects[left_pane_name].select = True
        bpy.ops.object.duplicate()
        new_pane = bpy.context.selected_objects[0]
        new_pane.location.x += pane_x_distance * i
        new_pane.location.z += offset
        i += 1

        #creat new material and assign name
        newMatName = "newMaterialLeft" + imgType + str(i)
        newCol = bpy.data.materials.new(newMatName)

        #add new material to selected object
        getActiveObj = bpy.context.selected_objects[0]
        getActiveObj.active_material = newCol

        #get new material
        mat = bpy.data.materials[newMatName] #need know exact name

        #add nodes
        mat.use_nodes = True

        #add texture node
        nodes = mat.node_tree.nodes 
        material_output = nodes.get("Material Output")
        node_texture =  nodes.new(type = 'ShaderNodeTexImage')        
        imagePath = bagFolder +  "/" +img
        node_texture.image = bpy.data.images.load(imagePath)
        node_texture.projection = "FLAT"
        node_texture.location = (new_pane.location.x, new_pane.location.y)

        #link texture to BSDF
        links = mat.node_tree.links
        link = links.new(node_texture.outputs[0], nodes.get("Diffuse BSDF").inputs[0])


    #For left images stitching
    right_imgs = imgs[imgType]["right"]
    i = 1
    for img in right_imgs:
        #unselect all objects 
        for obj in bpy.data.objects:
            obj.select = False

        # Add a left camera pane on top
        bpy.data.objects[right_pane_name].select = True
        bpy.ops.object.duplicate()
        new_pane = bpy.context.selected_objects[0]
        new_pane.location.x += pane_x_distance * i
        new_pane.location.z += offset
        i += 1

        #creat new material and assign name   
        newMatName = "newMaterialRight" + imgType + str(i)
        newCol = bpy.data.materials.new(newMatName)

        #add new material to selected object
        getActiveObj = bpy.context.selected_objects[0]
        getActiveObj.active_material = newCol

        #get new material
        mat = bpy.data.materials[newMatName]

        #add nodes
        mat.use_nodes = True

        #add texture node
        nodes = mat.node_tree.nodes 
        material_output = nodes.get("Material Output")
        node_texture =  nodes.new(type = 'ShaderNodeTexImage')
        imagePath = bagFolder + "/" + img
        node_texture.image = bpy.data.images.load(imagePath)
        node_texture.projection = "FLAT"
        node_texture.location = (new_pane.location.x, new_pane.location.y)

        #link texture to BSDF
        links = mat.node_tree.links
        link = links.new(node_texture.outputs[0], nodes.get("Diffuse BSDF").inputs[0])
    

    #render and save image (it takes time, especially when image is large)
    bpy.data.scenes['Scene'].render.filepath = bagFolder + "unwarpped" + imgType + 'Image.jpg'
    bpy.ops.render.render(write_still=True )
    

def main():
    setup()
    unwarpImg("white", - (2*pane_z_distance + 1.0))
    unwarpImg("uv", 2*pane_z_distance + 1.0)
    print("Unwarpping Finished!")
    
main()
###################################Stitch Images Ends#########################       
