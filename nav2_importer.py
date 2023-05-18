import os
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator

from nav2_blender.templates.nav2 import Nav2


bl_info = {
    'name': 'Nav2 Importer',
    'author': '',
    'version': (1, 0),
    'blender': (3, 3, 0),
    'location': 'File > Import > Nav2 (.nav2)',
    'description': 'Import nav2 files from MGSV (GZ, TPP)',
    'warning': '',
    'wiki_url': '',
    'category': 'Import',
}


def read_nav2_file(context, filepath, dir):
    nav2 = Nav2()
    nav2.Read(os.path.join(dir, filepath))
    return {'FINISHED'}


class Nav2Importer(Operator, ImportHelper):
    bl_idname = 'nav2.import_nav2'
    bl_label = 'Import Nav2 File'

    files: CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        for file in self.files:
            read_nav2_file(context, file.name, self.directory)
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(Nav2Importer.bl_idname, text='Nav2 Importer (.nav2)')


classes = (
    Nav2Importer,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.utils.unregister_class(Nav2Importer)


if __name__ == '__main__':
    register()
    bpy.ops.nav2.import_nav22('INVOKE_DEFAULT')
