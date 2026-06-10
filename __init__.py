#!/usr/bin/env python3
import sys
import bpy
from pathlib import Path

# 添加 libs 到路径
sys.path.insert(0, str(Path(__file__).parent / 'libs'))

bl_info = {
    "name": "GIMI Tools",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "author": "Based on SilentNightSound's GIMI-Tools, Adapted by AI",
    "location": "View3D > Sidebar > Tool Tab",
    "description": "原神 (Genshin Impact) 模组开发工具箱",
    "category": "Import-Export",
    "tracker_url": "https://github.com/SilentNightSound/GI-Model-Importer",
}

# 添加 scripts 目录到 sys.path
scripts_dir = str(Path(__file__).parent / 'scripts')
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# 导入模块
from .addon.settings import GIMI_Settings
from .addon.ui import GIMI_PT_MainPanel
from .addon.operators import (
    GIMI_OT_OverwriteConfirm,
    GIMI_OT_ImportObjects,
    GIMI_OT_ImportFrameDumpFromFolder,
    GIMI_OT_ExportMod,
    GIMI_OT_CreateAnimation,
    GIMI_OT_MergeMods,
    GIMI_OT_CreateAutoDamage,
    GIMI_OT_SetOutline,
    GIMI_OT_SetColor,
    GIMI_OT_SetTransparency,
)

# 导入原版 3DMigoto 插件的操作符
try:
    import blender_3dmigoto_gimi as migoto
    migoto_classes = (
        migoto.Import3DMigotoFrameAnalysis,
        migoto.Import3DMigotoRaw,
        migoto.Import3DMigotoReferenceInputFormat,
        migoto.Export3DMigoto,
        migoto.Export3DMigotoGenshin,
        migoto.ApplyVGMap,
        migoto.UpdateVGMap,
        migoto.Import3DMigotoPose,
        migoto.Merge3DMigotoPose,
        migoto.DeleteNonNumericVertexGroups,
    )
except ImportError as e:
    print(f"无法导入 blender_3dmigoto_gimi: {e}")
    migoto_classes = ()

# 所有需要注册的类
classes = [
    GIMI_Settings,
    GIMI_PT_MainPanel,
    GIMI_OT_OverwriteConfirm,
    GIMI_OT_ImportObjects,
    GIMI_OT_ImportFrameDumpFromFolder,
    GIMI_OT_ExportMod,
    GIMI_OT_CreateAnimation,
    GIMI_OT_MergeMods,
    GIMI_OT_CreateAutoDamage,
    GIMI_OT_SetOutline,
    GIMI_OT_SetColor,
    GIMI_OT_SetTransparency,
] + list(migoto_classes)


def register():
    print("注册 GIMI Tools 插件...")
    
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print(f"  注册类: {cls.__name__}")
        except Exception as e:
            print(f"  注册失败 {cls.__name__}: {e}")
    
    # 注册场景属性
    bpy.types.Scene.gimi_tools_settings = bpy.props.PointerProperty(type=GIMI_Settings)
    print("  注册场景属性: gimi_tools_settings")
    
    print("GIMI Tools 注册完成!")


def unregister():
    print("注销 GIMI Tools 插件...")
    
    # 注销场景属性
    if hasattr(bpy.types.Scene, 'gimi_tools_settings'):
        del bpy.types.Scene.gimi_tools_settings
        print("  注销场景属性: gimi_tools_settings")
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
            print(f"  注销类: {cls.__name__}")
        except Exception as e:
            print(f"  注销失败 {cls.__name__}: {e}")
    
    print("GIMI Tools 注销完成!")


if __name__ == "__main__":
    register()
