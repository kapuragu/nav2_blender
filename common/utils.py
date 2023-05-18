import bpy
import random


def get_random_color():
    r, g, b = [random.random() for i in range(3)]
    return r, g, b, 1


def create_mesh(file_empty, collection_name, mesh_name, vertices=[], edges=[], faces=[]):
    entry_collection_name = f'{file_empty}_{collection_name.split("_")[0]}'
    collection_name = f'{file_empty}_{collection_name}'
    mesh_name = f'{collection_name}_{mesh_name}'

    entry_collection = bpy.data.objects.get(entry_collection_name)
    collection = bpy.data.objects.get(collection_name)

    new_mesh = bpy.data.meshes.new(mesh_name)
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    new_object = bpy.data.objects.new(mesh_name, new_mesh)
    new_object.color = get_random_color()

    bpy.context.scene.collection.objects.link(new_object)
    new_object.parent = collection


def create_empty(file_empty, collection_name):
    if bpy.data.objects.get(file_empty):
        file_collection = bpy.data.objects.get(file_empty)
    else:
        file_collection = bpy.data.objects.new(file_empty, None)
        bpy.context.scene.collection.objects.link(file_collection)

    entry_collection_name = f'{file_empty}_{collection_name.split("_")[0]}'
    collection_name = f'{file_empty}_{collection_name}'

    if bpy.data.objects.get(entry_collection_name):
        entry_collection = bpy.data.objects.get(entry_collection_name)
    else:
        entry_collection = bpy.data.objects.new(entry_collection_name, None)
        bpy.context.scene.collection.objects.link(entry_collection)
        entry_collection.parent = file_collection
    
    if bpy.data.objects.get(collection_name):
        collection = bpy.data.objects.get(collection_name)
    else:
        collection = bpy.data.objects.new(collection_name, None)
        bpy.context.scene.collection.objects.link(collection)
        collection.parent = entry_collection
