# Web Python Backend Design

## Goal

把现有网页版公式编辑器升级为“浏览器界面 + 本地 Python 后端”的桌面级工具，复用 Python 工程已经验证过的 Word 原生公式生成、字体列表、符号库和品牌配置。

## Architecture

前端仍由 `index.html` 承载，继续使用 MathJax SVG 做实时矢量预览和复制。新增 Flask 本地服务读取 `ui_branding.py`、`formula_symbols.py`、`formula_docx.py`，通过 JSON 接口向页面提供品牌、字体和符号库，并通过 DOCX 下载接口生成包含 Word 原生公式对象的文档。

启动入口新增 `web_formula_studio.py`，负责创建 Flask app、寻找空闲端口、启动本地服务并打开浏览器。打包脚本包含 `index.html` 和图标资源，生成后的 exe 可以直接启动网页版体验。

## UI Requirements

网页顶部使用 `干翻传统公式编辑，全给我用LaTex` 和 `assets/esdkaiyuan.png`。顶部或工具栏提供公式字体下拉框，选项与 `SUPPORTED_FORMULA_FONTS` 一致，必须包含 `Times New Roman`。左侧增加符号库，分组与 Python 桌面端一致，按钮只显示符号，悬停显示说明与 LaTeX 示例，点击把 LaTeX 插入当前光标位置。

页面底部保留极轻量水平水印 `esdkaiyuan.online`，只在底部区域做向下循环运动，不覆盖编辑内容。右上或合适位置提供 `?` 帮助按钮，弹窗第一句为反馈链接说明，并包含基本快捷键和生成 Word 的说明。

## API Requirements

`GET /api/config` 返回应用标题、反馈 URL、水印文本、字体列表、符号分组。`POST /api/docx` 接收标题、说明、公式数组和字体名称，返回 `.docx` 文件。空公式时沿用 `build_docx` 的默认公式行为；非法或转换失败时返回 JSON 错误和非 2xx 状态。

## Testing

新增 unittest 覆盖 Flask app 的配置接口和 DOCX 下载接口。新增网页静态测试检查 `index.html` 包含后端调用、品牌入口、字体控件、符号库容器、帮助入口和 Word 生成按钮。
