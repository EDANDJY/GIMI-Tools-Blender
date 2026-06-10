import bpy
import os
import sys
import subprocess
import re
from pathlib import Path
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

# 获取当前文件所在目录 - 插件内部的 scripts 文件夹
script_dir = Path(__file__).parent.parent
gimi_tools_dir = script_dir / "scripts"

# 添加 scripts 到路径
if str(gimi_tools_dir) not in sys.path:
    sys.path.insert(0, str(gimi_tools_dir))


class GIMI_OT_OverwriteConfirm(bpy.types.Operator):
    """自定义覆盖确认对话框"""
    bl_idname = "gimi.overwrite_confirm"
    bl_label = "确认覆盖"
    bl_description = "确认是否覆盖已存在的文件夹"
    bl_options = {'REGISTER', 'UNDO'}

    folder_name: StringProperty(name="文件夹名称")

    def execute(self, context):
        # 用户点击确定，继续执行导入
        bpy.ops.gimi.import_objects('EXEC_DEFAULT')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"该输出目录下已有 {self.folder_name}")
        layout.label(text="是否确认覆盖？")


class GIMI_OT_ImportObjects(bpy.types.Operator):
    """从帧分析数据导入对象"""
    bl_idname = "gimi.import_objects"
    bl_label = "从帧分析提取对象"
    bl_description = "从 3DMigoto 帧分析数据中提取并导入模型对象"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        settings = context.scene.gimi_tools_settings
        
        # 验证路径
        if not settings.import_source_dir:
            self.report({'ERROR'}, "请指定帧分析目录")
            return {'CANCELLED'}
        
        if not os.path.exists(settings.import_source_dir):
            self.report({'ERROR'}, f"目录不存在：{settings.import_source_dir}")
            return {'CANCELLED'}
        
        # 验证输出目录
        if not settings.import_output_dir:
            self.report({'ERROR'}, "请指定提取输出目录")
            return {'CANCELLED'}
        
        # 验证输出名称
        output_name = settings.import_output_name.strip()
        if not output_name:
            self.report({'ERROR'}, "请指定提取输出名称")
            return {'CANCELLED'}
        
        # 检查输出文件夹是否已存在
        output_folder = os.path.join(settings.import_output_dir, output_name)
        if os.path.exists(output_folder) and os.listdir(output_folder):
            # 显示自定义确认对话框
            bpy.ops.gimi.overwrite_confirm('INVOKE_DEFAULT', folder_name=output_name)
            return {'FINISHED'}
        else:
            # 文件夹不存在或为空，直接执行
            return self.execute(context)

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 获取输出名称
        output_name = settings.import_output_name.strip()
        if not output_name:
            output_name = "Character"
        
        # 创建输出目录（如果不存在）
        os.makedirs(settings.import_output_dir, exist_ok=True)
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_3dmigoto_collect.py"),
            "-vb", settings.import_vb_hashes or "",
            "-n", output_name,
            "-f", settings.import_source_dir,
            "--remove_sanity",
            "--force_overwrite",
        ]
        
        if settings.import_skip_small_textures:
            # 这里可以添加小贴图过滤逻辑
            pass
        
        try:
            # 运行收集脚本，工作目录设置为输出目录
            result = subprocess.run(
                args, 
                capture_output=True, 
                text=True, 
                cwd=settings.import_output_dir,
                timeout=60  # 设置超时，防止无限等待
            )
            
            if result.returncode != 0:
                error_msg = f"收集失败：{result.stderr}" if result.stderr else f"收集失败，返回码：{result.returncode}"
                self.report({'ERROR'}, error_msg)
                return {'CANCELLED'}
            
            # 检查输出文件夹是否创建成功
            output_folder = os.path.join(settings.import_output_dir, output_name)
            if os.path.exists(output_folder) and os.listdir(output_folder):
                self.report({'INFO'}, f"对象提取完成！文件已保存到：{output_folder}")
            else:
                self.report({'WARNING'}, f"提取完成，但输出文件夹为空：{output_folder}")
            
            return {'FINISHED'}
            
        except subprocess.TimeoutExpired:
            self.report({'ERROR'}, "提取超时，请检查帧分析数据是否正确")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_ImportFrameDumpFromFolder(bpy.types.Operator):
    """从文件夹导入帧分析转储文件"""
    bl_idname = "gimi.import_frame_dump_from_folder"
    bl_label = "从文件夹导入帧转储"
    bl_description = "扫描文件夹并自动导入所有帧分析转储文件"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 验证路径
        if not settings.import_frame_dump_dir:
            self.report({'ERROR'}, "请指定帧转储文件夹")
            return {'CANCELLED'}
        
        if not os.path.exists(settings.import_frame_dump_dir):
            self.report({'ERROR'}, f"文件夹不存在：{settings.import_frame_dump_dir}")
            return {'CANCELLED'}
        
        # 添加脚本目录到 sys.path
        scripts_dir = str(gimi_tools_dir)
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
        
        try:
            # 清除已有缓存，强制重新加载最新版本
            if 'blender_3dmigoto_gimi' in sys.modules:
                del sys.modules['blender_3dmigoto_gimi']
            
            # Blender 4.0+ 兼容性修复：mesh.calc_normals() 已被移除
            if not hasattr(bpy.types.Mesh, 'calc_normals'):
                def dummy_calc_normals(self):
                    pass
                bpy.types.Mesh.calc_normals = dummy_calc_normals
            
            # 直接导入并调用 Blender 脚本中的函数
            import blender_3dmigoto_gimi as migoto_import
            
            # 扫描文件夹中的所有 .txt 文件
            import glob
            txt_files = glob.glob(os.path.join(settings.import_frame_dump_dir, '*.txt'))
            
            if not txt_files:
                self.report({'ERROR'}, "未找到 .txt 文件")
                return {'CANCELLED'}
            
            # 过滤出包含 vb 或 ib 的文件
            buffer_pattern = re.compile(r'''-(?:ib|vb[0-9]+)(?P<hash>=[0-9a-f]+)?(?=[^0-9a-f=])''')
            frame_dump_files = [f for f in txt_files if buffer_pattern.search(os.path.basename(f))]
            
            if not frame_dump_files:
                self.report({'WARNING'}, "未找到帧分析转储文件（包含 -ib 或 -vb 的文件），尝试导入所有 .txt 文件")
                frame_dump_files = txt_files
            
            # 直接调用导入函数（绕过操作符实例化问题）
            keywords = {
                'flip_texcoord_v': True,
                'axis_forward': '-Z',
                'axis_up': 'Y',
                'pose_cb_off': [0, 0],
                'pose_cb_step': 1,
            }
            
            # 获取 vb/ib 路径对
            buffer_pattern = re.compile(r'''-(?:ib|vb[0-9]+)(?P<hash>=[0-9a-f]+)?(?=[^0-9a-f=])''')
            dirname = settings.import_frame_dump_dir
            
            paths = set()
            for f in frame_dump_files:
                filename = os.path.basename(f)
                match = buffer_pattern.search(filename)
                if match:
                    ib_pattern = filename[:match.start()] + '-ib*' + filename[match.end():]
                    vb_pattern = filename[:match.start()] + '-vb*' + filename[match.end():]
                    ib_paths = glob.glob(os.path.join(dirname, ib_pattern))
                    vb_paths = glob.glob(os.path.join(dirname, vb_pattern))
                    
                    if len(ib_paths) == 1 and len(vb_paths) == 1:
                        paths.add((vb_paths[0], ib_paths[0], False, None))
            
            if not paths:
                self.report({'ERROR'}, "未找到有效的 vb/ib 文件对")
                return {'CANCELLED'}
            
            # 调用核心导入函数
            migoto_import.import_3dmigoto(self, context, paths, merge_meshes=False, **keywords)
            result = {'FINISHED'}
            
            # 视图聚焦到导入的对象
            imported_obj = context.view_layer.objects.active
            if imported_obj:
                # 选中对象
                imported_obj.select_set(True)
                bpy.context.view_layer.objects.active = imported_obj
                # 缩放视图以显示所有选中对象
                bpy.ops.view3d.view_selected()
            
            self.report({'INFO'}, f"成功导入 {len(frame_dump_files)} 个文件")
            return {'FINISHED'}
            
        except ImportError as e:
            self.report({'ERROR'}, f"导入模块失败：{str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            import traceback
            self.report({'ERROR'}, f"发生错误：{str(e)}\n{traceback.format_exc()}")
            return {'CANCELLED'}


class GIMI_OT_ExportMod(bpy.types.Operator):
    """导出 Mod"""
    bl_idname = "gimi.export_mod"
    bl_label = "导出 Mod"
    bl_description = "将当前场景导出为 Genshin Impact Mod"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 验证路径
        if not settings.export_output_dir:
            self.report({'ERROR'}, "请指定 Mod 导出目录")
            return {'CANCELLED'}
        
        # 创建输出目录
        os.makedirs(settings.export_output_dir, exist_ok=True)
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_3dmigoto_generate.py"),
            "-n", settings.mod_name or "Character",
        ]
        
        if settings.export_original_tangents:
            args.append("--original_tangents")
        
        try:
            # 运行生成脚本
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"导出失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"Mod 已导出到：{settings.export_output_dir}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_CreateAnimation(bpy.types.Operator):
    """创建动画模组"""
    bl_idname = "gimi.create_animation"
    bl_label = "创建动画模组"
    bl_description = "从动画数据创建可切换的动画模组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_animation_creator.py"),
            "-n", settings.animation_vg_count,
            "-k", settings.animation_key or "",
        ]
        
        if settings.animation_active_only:
            args.append("-a")
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"创建动画失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "动画模组创建完成")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_MergeMods(bpy.types.Operator):
    """合并模组"""
    bl_idname = "gimi.merge_mods"
    bl_label = "合并模组"
    bl_description = "将多个模组合并为一个可切换的模组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_merge_mods.py"),
            "-k", settings.merge_key or "",
        ]
        
        if settings.merge_compress:
            args.append("-c")
        
        if settings.merge_reflection_fix:
            args.append("-ref")
        
        if settings.animation_active_only:
            args.append("-a")
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"合并模组失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "模组合并完成")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_CreateAutoDamage(bpy.types.Operator):
    """创建自动伤害切换模组"""
    bl_idname = "gimi.create_auto_damage"
    bl_label = "创建自动伤害模组"
    bl_description = "根据伤害值自动切换的模组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_auto_damage_merge.py"),
            "-k", settings.merge_key or "",
        ]
        
        if settings.merge_compress:
            args.append("-c")
        
        if settings.auto_damage_accumulate:
            args.append("-acc")
        
        if settings.auto_damage_hit:
            args.append("-hit")
        
        if settings.animation_active_only:
            args.append("-a")
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"创建自动伤害模组失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "自动伤害模组创建完成")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_SetOutline(bpy.types.Operator):
    """设置轮廓厚度"""
    bl_idname = "gimi.set_outline"
    bl_label = "设置轮廓厚度"
    bl_description = "设置模型的轮廓厚度（0-255）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_set_outlines.py"),
            "--thickness", str(settings.tool_outline_thickness),
        ]
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"设置轮廓失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"轮廓厚度已设置为：{settings.tool_outline_thickness}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_SetColor(bpy.types.Operator):
    """设置颜色"""
    bl_idname = "gimi.set_color"
    bl_label = "设置颜色"
    bl_description = "设置顶点颜色（用于移除或修改轮廓）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_set_color.py"),
            "--stride", "20",  # 默认 stride，可能需要用户自定义
        ]
        
        if settings.tool_color_r is not None:
            args.extend(["-r", str(settings.tool_color_r)])
        if settings.tool_color_g is not None:
            args.extend(["-g", str(settings.tool_color_g)])
        if settings.tool_color_b is not None:
            args.extend(["-b", str(settings.tool_color_b)])
        if settings.tool_color_a is not None:
            args.extend(["-a", str(settings.tool_color_a)])
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"设置颜色失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "颜色设置完成")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


class GIMI_OT_SetTransparency(bpy.types.Operator):
    """设置透明度"""
    bl_idname = "gimi.set_transparency"
    bl_label = "设置透明度"
    bl_description = "为模型部件设置透明度效果"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.gimi_tools_settings
        
        # 构建参数
        args = [
            sys.executable,
            str(gimi_tools_dir / "genshin_set_transparency.py"),
            "-t", str(settings.tool_transparency_r),
                   str(settings.tool_transparency_g),
                   str(settings.tool_transparency_b),
        ]
        
        if settings.tool_transparency_body:
            args.append("-b")
        if settings.tool_transparency_head:
            args.append("-hd")
        if settings.tool_transparency_dress:
            args.append("-d")
        if settings.tool_transparency_extra:
            args.append("-e")
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(gimi_tools_dir))
            
            if result.returncode != 0:
                self.report({'ERROR'}, f"设置透明度失败：{result.stderr}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "透明度设置完成")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"发生错误：{str(e)}")
            return {'CANCELLED'}


# 注册所有操作符
classes = [
    GIMI_OT_ImportObjects,
    GIMI_OT_ImportFrameDumpFromFolder,
    GIMI_OT_ExportMod,
    GIMI_OT_CreateAnimation,
    GIMI_OT_MergeMods,
    GIMI_OT_CreateAutoDamage,
    GIMI_OT_SetOutline,
    GIMI_OT_SetColor,
    GIMI_OT_SetTransparency,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
