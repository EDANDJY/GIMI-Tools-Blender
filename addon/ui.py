import bpy
from bpy.props import BoolProperty, StringProperty, PointerProperty, IntProperty, FloatProperty
from .. import bl_info
from .settings import GIMI_Settings


class GIMI_PT_MainPanel(bpy.types.Panel):
    """GIMI Tools 主面板"""
    bl_label = "GIMI Tools"
    bl_idname = "GIMI_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GIMI Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.gimi_tools_settings
        
        # 模式选择 - 两列布局
        grid = layout.grid_flow(row_major=False, columns=2, even_columns=True, even_rows=True)
        grid.prop(settings, "tool_mode", expand=True)
        
        layout.separator()
        
        # 根据模式显示不同的设置
        if settings.tool_mode == 'FRAME_IMPORT':
            self.draw_frame_import_ui(layout, settings)
        elif settings.tool_mode == 'IMPORT':
            self.draw_import_ui(layout, settings)
        elif settings.tool_mode == 'EXPORT':
            self.draw_export_ui(layout, settings)
        elif settings.tool_mode == 'MERGE':
            self.draw_merge_ui(layout, settings)
        elif settings.tool_mode == 'AUTO_DAMAGE':
            self.draw_auto_damage_ui(layout, settings)
        elif settings.tool_mode == 'TOOLS':
            self.draw_tools_ui(layout, settings)
    
    def draw_frame_import_ui(self, layout, settings):
        """从帧分析提取对象界面"""
        box = layout.box()
        box.label(text="帧分析提取设置", icon='IMPORT')
        
        box.prop(settings, "import_source_dir")
        box.prop(settings, "import_output_dir")
        box.prop(settings, "import_output_name")
        box.prop(settings, "import_vb_hashes")
        
        row = box.row()
        row.prop(settings, "import_skip_small_textures")
        if settings.import_skip_small_textures:
            row.prop(settings, "import_min_texture_size", text="")
        
        box.prop(settings, "import_skip_jpg")
        box.prop(settings, "import_skip_cube_map")
        box.prop(settings, "import_skip_same_slot")
        box.prop(settings, "import_skip_empty_vg")
        box.prop(settings, "import_mirror_mesh")
        box.prop(settings, "import_vertex_color")
        box.prop(settings, "import_skeleton_type")
        
        layout.operator("gimi.import_objects", icon='IMPORT')

    def draw_import_ui(self, layout, settings):
        """导入对象界面"""
        # 快速导入区域
        box_quick = layout.box()
        box_quick.label(text="快速导入", icon='IMPORT')
        box_quick.prop(settings, "import_frame_dump_dir")
        box_quick.operator("gimi.import_frame_dump_from_folder", icon='FILE_FOLDER')
        
        layout.separator()
        
        # 原版导入功能
        box_import = layout.box()
        col = box_import.column(align=True)
        col.label(text="导入 Import", icon='IMPORT')
        col.separator()
        col.operator("import_mesh.migoto_frame_analysis",
                     text="帧分析转储 (vb.txt + ib.txt)", icon='FILE_FOLDER')
        col.operator("import_mesh.migoto_raw_buffers",
                     text="原始缓冲 (.vb + .ib)", icon='FILE_BLANK')
        col.operator("import_mesh.migoto_input_format",
                     text="参考输入格式 (.txt)", icon='TEXT')
        col.operator("armature.migoto_pose",
                     text="姿势 (.txt)", icon='ARMATURE_DATA')
    
    def draw_export_ui(self, layout, settings):
        """导出界面"""
        box = layout.box()
        box.label(text="导出设置", icon='EXPORT')
        
        box.prop(settings, "export_component_set")
        box.prop(settings, "export_source_dir")
        box.prop(settings, "export_output_dir")
        box.prop(settings, "export_skeleton_type")
        
        box.separator()
        
        col = box.column()
        col.prop(settings, "export_mirror_mesh")
        col.prop(settings, "export_apply_modifiers")
        col.prop(settings, "export_copy_textures")
        col.prop(settings, "export_update_textures")
        col.prop(settings, "export_generate_ini")
        col.prop(settings, "export_ini_comments")
        col.prop(settings, "export_ignore_embedded")
        col.prop(settings, "export_ignore_hidden")
        col.prop(settings, "export_ignore_disabled_shapekeys")
        col.prop(settings, "export_skip_cube_map")
        col.prop(settings, "export_fix_missing_vg")
        col.prop(settings, "export_unlimited_shapekeys")
        col.prop(settings, "export_scale")
        col.prop(settings, "export_partial_export")
        
        box.separator()
        
        # Mod 信息
        box_mod = layout.box()
        box_mod.label(text="Mod 信息", icon='INFO')
        box_mod.prop(settings, "mod_name")
        box_mod.prop(settings, "mod_author")
        box_mod.prop(settings, "mod_description")
        box_mod.prop(settings, "mod_link")
        box_mod.prop(settings, "mod_logo")
        
        layout.operator("gimi.export_mod", icon='EXPORT')
        
        # 原版 3DMigoto 导出功能
        box_export = layout.box()
        col = box_export.column(align=True)
        col.label(text="导出 Export", icon='EXPORT')
        col.separator()
        col.operator("export_mesh.migoto",
                     text="原始缓冲 (.vb + .ib)", icon='FILE_BLANK')
        col.operator("export_mesh_genshin.migoto",
                     text="导出原神 Mod 文件夹", icon='FILE_FOLDER')
    
    def draw_merge_ui(self, layout, settings):
        """合并模组界面"""
        box = layout.box()
        box.label(text="合并模组设置", icon='COPYRIGHT')
        
        box.prop(settings, "merge_key")
        box.prop(settings, "merge_compress")
        box.prop(settings, "merge_reflection_fix")
        
        layout.operator("gimi.merge_mods", icon='COPYRIGHT')
    
    def draw_auto_damage_ui(self, layout, settings):
        """自动伤害界面"""
        box = layout.box()
        box.label(text="自动伤害设置", icon='FORCE_VORTEX')
        
        box.prop(settings, "auto_damage_accumulate")
        box.prop(settings, "auto_damage_hit")
        box.prop(settings, "merge_key")
        box.prop(settings, "merge_compress")
        
        layout.operator("gimi.create_auto_damage", icon='FORCE_VORTEX')
    
    def draw_tools_ui(self, layout, settings):
        """工具箱界面"""
        # 轮廓工具
        box = layout.box()
        box.label(text="轮廓工具", icon='MOD_WIREFRAME')
        box.prop(settings, "tool_outline_thickness")
        box.operator("gimi.set_outline", icon='MOD_WIREFRAME')
        
        # 颜色工具
        box = layout.box()
        box.label(text="颜色工具", icon='COLOR')
        row = box.row()
        row.prop(settings, "tool_color_r", text="R")
        row.prop(settings, "tool_color_g", text="G")
        row.prop(settings, "tool_color_b", text="B")
        row.prop(settings, "tool_color_a", text="A")
        box.operator("gimi.set_color", icon='COLOR')
        
        # 透明度工具
        box = layout.box()
        box.label(text="透明度工具", icon='MATERIAL')
        col = box.column()
        col.prop(settings, "tool_transparency_body")
        col.prop(settings, "tool_transparency_head")
        col.prop(settings, "tool_transparency_dress")
        col.prop(settings, "tool_transparency_extra")
        row = box.row()
        row.prop(settings, "tool_transparency_r", text="R")
        row.prop(settings, "tool_transparency_g", text="G")
        row.prop(settings, "tool_transparency_b", text="B")
        box.operator("gimi.set_transparency", icon='MATERIAL')
        
        # 动画创建工具
        box = layout.box()
        box.label(text="动画创建", icon='ANIM')
        box.prop(settings, "animation_vg_count")
        box.prop(settings, "animation_key")
        box.prop(settings, "animation_active_only")
        box.operator("gimi.create_animation", icon='ANIM')
        
        # 原版 3DMigoto 工具功能
        box_tools = layout.box()
        col = box_tools.column(align=True)
        col.label(text="工具 Tools", icon='TOOL_SETTINGS')
        col.separator()
        col.operator("mesh.migoto_vertex_group_map",
                     text="应用顶点组映射 (.vgmap)", icon='GROUP_VERTEX')
        col.operator("mesh.update_migoto_vertex_group_map",
                     text="更新顶点组映射", icon='GROUP_VERTEX')
        col.operator("armature.merge_pose",
                     text="合并姿势", icon='POSE_HLT')
        col.operator("vertex_groups.delete_non_numeric",
                     text="删除非数字顶点组", icon='TRASH')


# 注册
classes = [
    GIMI_PT_MainPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
