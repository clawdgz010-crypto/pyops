# mycode

个人的代码仓库，包含一些实用的 Python 运维工具。

## 工具列表

### 1. 系统监控工具 (sys_monitor.py)

实时查看系统资源使用情况，包括 CPU、内存、磁盘和网络。

```bash
# 查看一次系统信息
python sys_monitor.py

# 持续监控（每5秒刷新）
python sys_monitor.py --loop

# 自定义监控间隔（每10秒）
python sys_monitor.py --loop --interval 10
```

**功能特性:**
- CPU 使用率和核心数
- 内存使用情况
- 磁盘空间和挂载点
- 网络流量统计

---

### 2. 日志分析工具 (log_analyzer.py)

分析日志文件，统计 ERROR、WARNING、INFO、DEBUG 等级别的日志。

```bash
# 分析日志文件
python log_analyzer.py /var/log/syslog

# 使用自定义模式搜索
python log_analyzer.py app.log -p "Exception"
```

**功能特性:**
- 自动识别日志级别
- 统计各级别日志数量
- 显示关键日志内容
- 支持自定义搜索模式

---

### 3. 文件监控工具 (file_watcher.py)

实时监控文件或目录的变更（新增、修改、删除）。

```bash
# 监控目录
python file_watcher.py /path/to/directory

# 监控单个文件
python file_watcher.py /var/log/app.log

# 自定义检查间隔
python file_watcher.py /path/to/directory --interval 5
```

**功能特性:**
- 实时检测文件变更
- 基于 MD5 哈希的变更检测
- 自动忽略 .git、__pycache__ 等目录
- 显示变更时间戳

---

## 安装依赖

```bash
pip install -r requirements.txt
```

## 许可证

MIT License
