# pyops

Python 运维工具箱 - 系统监控、日志分析、进程管理、端口扫描等实用工具集

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

### 4. 进程管理工具 (process_manager.py)

查看和管理系统进程，支持搜索、查看详情和终止进程。

```bash
# 列出进程（按CPU使用率排序）
python process_manager.py list

# 按内存排序，显示前20个
python process_manager.py list -s memory -n 20

# 搜索进程
python process_manager.py find nginx

# 查看进程详情
python process_manager.py info 1234

# 终止进程
python process_manager.py kill 1234
python process_manager.py kill 1234 --force  # 强制终止
```

**功能特性:**
- 按CPU、内存、PID排序显示进程
- 关键词搜索进程
- 查看进程详细信息（内存、连接、文件）
- 安全终止进程（SIGTERM/SIGKILL）

---

### 5. 端口扫描工具 (port_scanner.py)

检查端口占用情况，扫描开放端口。

```bash
# 列出所有监听端口
python port_scanner.py listen

# 扫描本地端口范围
python port_scanner.py scan localhost -p 1-1024

# 扫描指定端口
python port_scanner.py scan localhost -p 80,443,8080,3306

# 检查端口占用
python port_scanner.py check 8080
```

**功能特性:**
- 列出系统所有监听端口
- 多线程端口扫描
- 识别常见服务端口
- 查看端口占用进程

---

### 6. 备份工具 (backup_tool.py)

文件和目录的备份、恢复、管理。

```bash
# 创建备份
python backup_tool.py create /path/to/file
python backup_tool.py create /path/to/dir -n mybackup

# 列出备份
python backup_tool.py list

# 恢复备份
python backup_tool.py restore 1
python backup_tool.py restore 1 -d /target/directory

# 删除备份
python backup_tool.py delete 1

# 清理30天前的备份
python backup_tool.py cleanup -d 30
```

**功能特性:**
- 支持文件和目录备份
- tar.gz 压缩备份
- 备份索引管理
- 自动清理旧备份

---

### 7. SSH 配置管理工具 (ssh_manager.py)

管理 SSH 密钥和主机配置。

```bash
# 列出 SSH 密钥
python ssh_manager.py keys

# 生成新密钥
python ssh_manager.py gen-key -n mykey -t ed25519 -e user@example.com

# 列出 SSH 主机配置
python ssh_manager.py hosts

# 添加主机配置
python ssh_manager.py add-host -n myserver -H 192.168.1.100 -u root -p 22

# 测试连接
python ssh_manager.py test myserver

# 复制公钥
python ssh_manager.py copy-id myserver
```

**功能特性:**
- 列出和管理 SSH 密钥
- 生成 RSA/ED25519/ECDSA 密钥
- 管理 SSH config 主机配置
- 测试 SSH 连接
- 快速复制公钥到远程主机

---

### 8. 配置文件解析工具 (config_parser.py)

解析和转换多种格式的配置文件。

```bash
# 读取配置文件
python config_parser.py read config.json
python config_parser.py read config.yaml
python config_parser.py read config.ini

# 搜索配置项
python config_parser.py search config.json database.host
python config_parser.py search config.yaml server.port

# 转换格式
python config_parser.py convert config.json -f yaml
python config_parser.py convert config.yaml -f json -o output.json
```

**功能特性:**
- 支持 JSON、YAML、INI、.env 格式
- 自动检测文件格式
- 美观显示配置内容
- 格式互转

---

## 安装依赖

```bash
pip install -r requirements.txt
```

## 许可证

MIT License
