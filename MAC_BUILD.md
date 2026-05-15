# macOS 打包说明

macOS `.app` 必须在 macOS 上构建，不能在 Windows 上交叉打包。

## 生成 `.app`

在 Mac 上进入项目目录后执行：

```bash
chmod +x build_mac.sh
./build_mac.sh
```

成功后会生成：

```text
dist/WordFormulaStudio.app
```

如果已安装 `create-dmg`，脚本还会生成：

```text
dist/WordFormulaStudio-mac.dmg
```

安装 `create-dmg`：

```bash
brew install create-dmg
```

## Microsoft Word 转换组件

本工具需要 `MML2OMML.XSL` 来生成 Word 原生公式。脚本默认查找：

```text
/Applications/Microsoft Word.app/Contents/Resources/MML2OMML.XSL
```

如果你的 Office 路径不同，执行前指定：

```bash
export MML2OMML_XSL="/path/to/MML2OMML.XSL"
./build_mac.sh
```
