import bpy
import gpu
from bpy.props import IntProperty,BoolProperty,StringProperty,PointerProperty,CollectionProperty
from bpy.utils import register_class,unregister_class

class view_synchronous_info_view(bpy.types.PropertyGroup):
    """
    对于每个3D视图的结构体
    """
    # 自身
    view:IntProperty(name="view")
    # 是否开始同步
    start_synchronous:BoolProperty(name="start_synchronous",default=False)
    # 同步目标
    target:IntProperty(name="target",default=-1)

class view_synchronous_info_workspace(bpy.types.PropertyGroup):
    """
    对于工作区的结构体
    """
    # 是否开启标识
    is_tag:BoolProperty(name="开启标记")
    # 当前处理的对象
    target:IntProperty(name="当前对象",default=-1)
    # 
    infos:CollectionProperty(type=view_synchronous_info_view)

def synchronous():
    global_info = bpy.context.workspace.view_synchronous_info_workspace
    areas = bpy.context.screen.areas
    buf = []
    for index in range(0,len(global_info.infos)):
        info = global_info.infos[index]
        if info.view > 0 and info.view < len(areas) and areas[info.view].type == 'VIEW_3D':
            buf.append(info.view)
            if info.start_synchronous and info.target > 0 and info.target < len(areas) and areas[info.target].type == 'VIEW_3D':
                areas[info.view].spaces[0].region_3d.view_matrix = areas[info.target].spaces[0].region_3d.view_matrix
        else:
            global_info.infos.remove(index)
    for index in range(len(areas)):
        if areas[index].type == 'VIEW_3D' and not index in buf:
            i = global_info.infos.add()
            i.view = index



class view_synchronous(bpy.types.Panel):
    bl_label = "视图同步"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BetaToolBox"

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="RENDER_RESULT")

    def draw(self, context):
        layout = self.layout
        global_info = context.workspace.view_synchronous_info_workspace
        areas = context.screen.areas
        local = context.space_data
        # 显示当前视图编号
        row = layout.row()
        row.label(text="当前试图序号")
        for index in range(0,len(areas)):
            if areas[index].spaces[0] == local:
                row.label(text=str(index))
        # 显示当前选择试图
        row = layout.row()
        row.label(text="当前选择视图")
        if(global_info.target < 0):
            row.label(text="无")
        else:
            row.label(text=str(global_info.target))
        row.operator(operator="beta.next_view",text="",icon='TRIA_RIGHT')
        # 显示当前视图同步信息
        box = layout.box()
        flage = True
        for info in global_info.infos:
            flage = True
            if areas[info.view].spaces[0] == local:
                flage = False
                row = box.row()
                row.label(text="跟踪目标")
                if info.target < 0:
                    row.label(text="无")
                else:
                    row.label(text=str(info.target))
                row.operator("beta.set_target",text="设置目标")
                box.prop(info,"start_synchronous",text="开始跟踪目标")
                break
        if flage:
            box.label(text="当前视图未同步")


class next_view(bpy.types.Operator):
    bl_idname = "beta.next_view"
    bl_label = "Next View"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global_info = context.workspace.view_synchronous_info_workspace
        areas = context.screen.areas
        if global_info.target >= len(areas) or areas[global_info.target].type != 'VIEW_3D' or areas[global_info.target].spaces[0] == context.space_data:
            global_info.target = -1
        index = global_info.target + 1
        while True:
            if index == len(areas):
                if global_info.target == -1:
                    break
                index = 0
            if areas[index].type == 'VIEW_3D' and areas[index].spaces[0] != context.space_data:
                global_info.target = index
                break
            index += 1
            if index == global_info.target:
                break
        return {"FINISHED"}

class set_target(bpy.types.Operator):
    bl_idname = "beta.set_target"
    bl_label = "Set Target"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        areas = context.screen.areas
        global_info = context.workspace.view_synchronous_info_workspace
        for info in global_info.infos:
            flage = False
            if areas[info.view].spaces[0] == context.space_data:
                info.target = global_info.target
        return {"FINISHED"}

def register_view_synchronous():
    register_class(view_synchronous)
    register_class(set_target)
    register_class(next_view)
    register_class(view_synchronous_info_view)
    register_class(view_synchronous_info_workspace)
    bpy.types.WorkSpace.view_synchronous_info_workspace = PointerProperty(type=view_synchronous_info_workspace)
    bpy.types.SpaceView3D.draw_handler_add(synchronous,(),'WINDOW','POST_VIEW')

def unregister_view_synchronous():
    unregister_class(view_synchronous)
    unregister_class(set_target)
    unregister_class(next_view)
    unregister_class(view_synchronous_info_view)
    unregister_class(view_synchronous_info_workspace)
    bpy.types.SpaceView3D.draw_handler_remove(synchronous,(),'WINDOW','POST_VIEW')