bl_info = {
    "name": "ViewSync",
    "description": "用于同步视图",
    "author": "Authors name",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "N键菜单 视图同步",
    "wiki_url": "",
    "category": "BlackSpree" }
    

import bpy
from .view_synchronous import register_view_synchronous, unregister_view_synchronous

def register():
    register_view_synchronous()

def unregister():
    unregister_view_synchronous()

if __name__ == "__main__":
    register()