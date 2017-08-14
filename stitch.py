import bpy
import csv

#variables for stitching
pane_x_distance = 0.9369
left_pane_name = "Left Camera Texture"
right_pane_name = "Right Camera Texture"

#bag file folder depends on your laptop
bagFolder = "/Users/lili/Desktop/peipei_data_2017-08-09-19-57-12/"

#find number of images from image csv files
#open one of the image csv file
csvName = "right_uv_image_raw_compressed.csv"
imgCsvPath = bagFolder + csvName 
numOfImgs = int((len(list(csv.reader(open(imgCsvPath, "r"), delimiter=","))) - 1) / 2)
numOfImgsSelected = numOfImgs / 8

#set camera orthograpic scale value
bpy.data.cameras['Camera'].ortho_scale = numOfImgsSelected

#set camera position
bpy.data.objects['Camera'].location[0] = float(0.46845 * (numOfImgsSelected + 1))#5.15295
bpy.data.objects['Camera'].location[1] = - numOfImgsSelected

#set scene resolution
bpy.data.scenes['Scene'].render.resolution_x = 937 * numOfImgsSelected
bpy.data.scenes['Scene'].render.resolution_y = 6072

########################################For Left################################
def unwarpImg(imgType):
    for i in range(0, numOfImgs, 8):
        #unselect all objects 
        for obj in bpy.data.objects:
            obj.select = False

        # Add a left camera pane on top
        bpy.data.objects[left_pane_name].select = True
        bpy.ops.object.duplicate()
        new_pane = bpy.context.selected_objects[0]
        new_pane.location.x += pane_x_distance * (i / 8)

        #creat new material and assign name
        newMatName = "newMaterialLeft" + str(i)
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
        imageFolder = bagFolder + "left_" + imgType + "_image_raw_compressed/0000000"
        if(i < 10):
            tmp = "00" + str(i) + ".jpg"
        elif(i < 100):
            tmp = "0" + str(i) + ".jpg"
        else:
            tmp = str(i) + ".jpg"
        imagePath = imageFolder + tmp
        node_texture.image = bpy.data.images.load(imagePath)
        node_texture.projection = "FLAT"
        node_texture.location = (new_pane.location.x, new_pane.location.y)

        #link texture to BSDF
        links = mat.node_tree.links
        link = links.new(node_texture.outputs[0], nodes.get("Diffuse BSDF").inputs[0])

    ##################################For Right####################################
    for i in range(0, numOfImgs, 8):
        #unselect all objects 
        for obj in bpy.data.objects:
            obj.select = False

        # Add a left camera pane on top
        bpy.data.objects[right_pane_name].select = True
        bpy.ops.object.duplicate()
        new_pane = bpy.context.selected_objects[0]
        new_pane.location.x += pane_x_distance * (i / 8)

        #creat new material and assign name   
        newMatName = "newMaterialRight" + str(i)
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
        imageFolder = bagFolder + "right_" + imgType + "_image_raw_compressed/0000000"
        if(i < 10):
            tmp = "00" + str(i) + ".jpg"
        elif(i < 100):
            tmp = "0" + str(i) + ".jpg"
        else:
            tmp = str(i) + ".jpg"
        imagePath = imageFolder + tmp
        node_texture.image = bpy.data.images.load(imagePath)
        node_texture.projection = "FLAT"
        node_texture.location = (new_pane.location.x, new_pane.location.y)

        #link texture to BSDF
        links = mat.node_tree.links
        link = links.new(node_texture.outputs[0], nodes.get("Diffuse BSDF").inputs[0])

        #render and save image (it takes time, especially when image is large)
        bpy.data.scenes['Scene'].render.filepath = '/Users/lili/Desktop/PipeDream/Blender/unwarpped' + imgType + '.jpg'
        bpy.ops.render.render( write_still=True )
unwarpImg("white")

'''
blender --background /Users/lili/Desktop/PipeDream/Blender/new_mesh.blend --python /Users/lili/Desktop/PipeDream/Blender/stitch.py
--render-output //pipe_texture --render-format PNG --use-extension 1 --render-frame 0
'''