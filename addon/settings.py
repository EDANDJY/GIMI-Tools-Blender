import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup


class GIMI_Settings(PropertyGroup):
    """GIMI Tools 插件设置"""
    
    # 模式选择
    tool_mode: EnumProperty(
        name="模式",
        description="选择工具模式",
        items=[
            ('FRAME_IMPORT', "从帧分析提取对象", "从 3DMigoto 帧分析数据提取并导入模型"),
            ('IMPORT', "导入对象", "导入 LODO 模型"),
            ('EXPORT', "导出 Mod", "导出为 Mod 文件"),
            ('MERGE', "合并模组", "合并多个模组"),
            ('AUTO_DAMAGE', "自动伤害切换", "根据伤害自动切换模组"),
            ('TOOLS', "工具箱", "各种工具功能"),
        ],
        default='FRAME_IMPORT'
    )
    
    # 导入设置
    import_source_dir: StringProperty(
        name="帧分析目录",
        description="FrameAnalysis 文件夹路径",
        subtype='DIR_PATH'
    )
    import_frame_dump_dir: StringProperty(
        name="帧转储文件夹",
        description="包含帧分析转储文件的文件夹路径",
        subtype='DIR_PATH'
    )
    import_output_dir: StringProperty(
        name="提取输出目录",
        description="提取数据的输出路径",
        subtype='DIR_PATH'
    )
    import_output_name: StringProperty(
        name="提取输出名称",
        description="输出文件夹名称（不含路径）",
        default="Character"
    )
    import_vb_hashes: StringProperty(
        name="指定哈希",
        description="VB 哈希值（空格分隔）"
    )
    import_skip_small_textures: BoolProperty(
        name="跳过小尺寸贴图",
        description="跳过小于指定尺寸的贴图",
        default=True
    )
    import_min_texture_size: IntProperty(
        name="最小尺寸 (KB)",
        description="贴图最小尺寸（KB）",
        default=256,
        min=0
    )
    import_skip_jpg: BoolProperty(
        name="跳过 .jpg",
        description="跳过 JPG 格式贴图",
        default=True
    )
    import_skip_cube_map: BoolProperty(
        name="跳过已知立方体贴图",
        description="跳过已知的立方体贴图",
        default=True
    )
    import_skip_same_slot: BoolProperty(
        name="跳过同槽哈希贴图",
        description="跳过相同纹理槽的哈希贴图",
        default=False
    )

    
    # 导出设置
    export_component_set: EnumProperty(
        name="组件集合",
        description="组件集合类型",
        items=[
            ('SINGLE', "集合", "单个集合"),
            ('MULTIPLE', "多个", "多个组件"),
        ],
        default='SINGLE'
    )
    export_source_dir: StringProperty(
        name="LODO 来源目录",
        description="LODO 模型来源目录",
        subtype='DIR_PATH'
    )
    export_output_dir: StringProperty(
        name="Mod 导出目录",
        description="Mod 输出目录",
        subtype='DIR_PATH'
    )
    export_skeleton_type: EnumProperty(
        name="骨架类型",
        description="骨架类型",
        items=[
            ('MERGED', "合并型", "合并所有骨架"),
            ('COMPONENT', "组件型", "按组件分离骨架"),
        ],
        default='MERGED'
    )
    export_mirror_mesh: BoolProperty(
        name="镜像网格",
        description="镜像导出的网格",
        default=False
    )
    export_apply_modifiers: BoolProperty(
        name="应用全部修改器",
        description="导出前应用所有修改器",
        default=False
    )
    export_copy_textures: BoolProperty(
        name="复制贴图",
        description="复制贴图到 Mod 文件夹",
        default=True
    )
    export_update_textures: BoolProperty(
        name="更新贴图",
        description="更新现有贴图",
        default=True
    )
    export_generate_ini: BoolProperty(
        name="生成 Mod INI",
        description="生成 Mod INI 文件",
        default=True
    )
    export_ini_comments: BoolProperty(
        name="为 INI 添加注释",
        description="在 INI 文件中添加注释",
        default=False
    )
    export_ignore_embedded: BoolProperty(
        name="忽略嵌套集合",
        description="忽略嵌套的集合",
        default=True
    )
    export_ignore_hidden: BoolProperty(
        name="忽略隐藏对象",
        description="忽略隐藏的对象",
        default=False
    )
    export_ignore_disabled_shapekeys: BoolProperty(
        name="忽略已禁用形态键",
        description="忽略已禁用的形态键",
        default=True
    )
    export_skip_cube_map: BoolProperty(
        name="跳过已知立方体贴图",
        description="跳过已知的立方体贴图",
        default=True
    )
    export_fix_missing_vg: BoolProperty(
        name="补全缺失顶点组",
        description="自动补全缺失的顶点组",
        default=True
    )
    export_unlimited_shapekeys: BoolProperty(
        name="不限制自定义形态键",
        description="不限制自定义形态键数量",
        default=False
    )
    export_scale: FloatProperty(
        name="骨架缩放",
        description="骨架缩放比例",
        default=1.0,
        min=0.01,
        max=10.0
    )
    export_partial_export: BoolProperty(
        name="部分导出",
        description="只导出选中的对象",
        default=False
    )
    export_original_tangents: BoolProperty(
        name="使用原始切线",
        description="使用原始切线数据（实验性）",
        default=False
    )
    
    # Mod 信息
    mod_name: StringProperty(
        name="Mod 名称",
        description="Mod 的名称",
        default="Unnamed Mod"
    )
    mod_author: StringProperty(
        name="作者名称",
        description="Mod 作者",
        default="Unknown Author"
    )
    mod_description: StringProperty(
        name="Mod 描述",
        description="Mod 的描述",
        default=""
    )
    mod_link: StringProperty(
        name="Mod 链接",
        description="Mod 的链接",
        default=""
    )
    mod_logo: StringProperty(
        name="Mod Logo",
        description="Mod 的 Logo 文件路径",
        subtype='FILE_PATH'
    )
    
    # 动画设置
    animation_vg_count: IntProperty(
        name="顶点组数量",
        description="顶点组数量",
        default=1,
        min=1
    )
    animation_key: StringProperty(
        name="切换键",
        description="切换动画的按键",
        default=""
    )
    animation_active_only: BoolProperty(
        name="仅活动角色",
        description="只切换活动（屏幕上）的角色",
        default=True
    )
    
    # 合并模组设置
    merge_key: StringProperty(
        name="切换键",
        description="切换模组的按键",
        default=""
    )
    merge_compress: BoolProperty(
        name="压缩输出",
        description="使输出的 Mod 尽可能小（警告：难以还原）",
        default=False
    )
    merge_reflection_fix: BoolProperty(
        name="反射修复",
        description="应用 3.0+ 角色的反射修复",
        default=False
    )
    
    # 自动伤害切换设置
    auto_damage_accumulate: BoolProperty(
        name="伤害累积",
        description="使用伤害累积而不是阈值",
        default=False
    )
    auto_damage_hit: BoolProperty(
        name="单次大伤害",
        description="使用单次大伤害触发服装变化",
        default=False
    )
    
    # 工具设置
    tool_outline_thickness: IntProperty(
        name="轮廓厚度",
        description="轮廓厚度（0-255，0 为无轮廓）",
        default=0,
        min=0,
        max=255
    )
    tool_color_r: IntProperty(
        name="R",
        description="红色值",
        default=0,
        min=0,
        max=255
    )
    tool_color_g: IntProperty(
        name="G",
        description="绿色值",
        default=0,
        min=0,
        max=255
    )
    tool_color_b: IntProperty(
        name="B",
        description="蓝色值",
        default=0,
        min=0,
        max=255
    )
    tool_color_a: IntProperty(
        name="A",
        description="透明度值（控制轮廓厚度）",
        default=0,
        min=0,
        max=255
    )
    tool_transparency_body: BoolProperty(
        name="身体透明",
        description="使身体透明",
        default=False
    )
    tool_transparency_head: BoolProperty(
        name="头部透明",
        description="使头部透明",
        default=False
    )
    tool_transparency_dress: BoolProperty(
        name="衣服透明",
        description="使衣服透明",
        default=False
    )
    tool_transparency_extra: BoolProperty(
        name="额外透明",
        description="使额外部分透明",
        default=False
    )
    tool_transparency_r: FloatProperty(
        name="R 因子",
        description="红色透明度因子",
        default=0.5,
        min=0.0,
        max=1.0
    )
    tool_transparency_g: FloatProperty(
        name="G 因子",
        description="绿色透明度因子",
        default=0.5,
        min=0.0,
        max=1.0
    )
    tool_transparency_b: FloatProperty(
        name="B 因子",
        description="蓝色透明度因子",
        default=0.5,
        min=0.0,
        max=1.0
    )
