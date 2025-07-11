# MicroPython 开发工具集

这是一个用于 MicroPython 开发的工具集合，提供文件上传、设备监控和热重载功能。

## 快速开始

1. 安装依赖：
```shell script
pip install -r requirements.txt
```

2. 配置环境变量：
```shell script
echo "DEVICE=/dev/ttyUSB0" >> .env
echo "BAUD=115200" >> .env
```

3. 开始开发：
```shell script
# 首次上传所有文件
python upload.py --all
# 开发过程中使用热重载
python reload.py
```

## 工具介绍

### 1. upload.py - 文件上传工具
上传工具，用于将本地 Python 文件同步到 MicroPython 设备。（会自动重启）

**使用方法：**
```
bash
# 上传已修改的文件
python upload.py

# 强制同步所有文件（会先清空再上传）
python upload.py --all
```
### 2. monit.py - 串口监控工具
实时监控 MicroPython 设备的串口输出，便于调试和查看程序运行状态。

**使用方法：**
```
bash
python monit.py
# 使用ctrl + d退出
# 可以在python解释器里直接输入main()来重新运行
```
### 3. reload.py - 热重载工具
组合工具，自动上传变更文件并启动监控.（会自动重启）

**使用方法：**
```
bash
python reload.py
```
## 环境配置

创建 `.env` 文件并配置以下参数：

```env
DEVICE=/dev/ttyUSBx (on Win: COMx)    # 设备路径
BAUD=115200                           # 波特率
```


## 目录结构

```
.
├── src/             # pyboard源代码目录
├── .uploaded/       # 上传文件哈希缓存
├── .env             # 环境变量配置
├── upload.py        # 文件上传工具
├── monit.py         # 串口监控工具
└── reload.py        # 热重载工具
```

