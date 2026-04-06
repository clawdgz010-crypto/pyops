#!/usr/bin/env python3
"""
系统监控工具单元测试
"""
import sys
import os
import unittest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_monitor import (
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_network_info,
    get_system_info,
)


class TestSystemMonitor(unittest.TestCase):
    """系统监控测试类"""

    def test_get_cpu_info(self):
        """测试 CPU 信息获取"""
        info = get_cpu_info()
        self.assertIn("cores", info)
        self.assertIn("percent", info)
        self.assertGreater(info["cores"], 0)
        self.assertGreaterEqual(info["percent"], 0)
        self.assertLessEqual(info["percent"], 100)

    def test_get_memory_info(self):
        """测试内存信息获取"""
        info = get_memory_info()
        self.assertIn("total_gb", info)
        self.assertIn("used_gb", info)
        self.assertIn("available_gb", info)
        self.assertIn("percent", info)
        self.assertGreater(info["total_gb"], 0)
        self.assertGreaterEqual(info["percent"], 0)
        self.assertLessEqual(info["percent"], 100)

    def test_get_disk_info(self):
        """测试磁盘信息获取"""
        info = get_disk_info()
        self.assertIsInstance(info, list)
        if len(info) > 0:
            disk = info[0]
            self.assertIn("mountpoint", disk)
            self.assertIn("total_gb", disk)
            self.assertIn("percent", disk)

    def test_get_network_info(self):
        """测试网络信息获取"""
        info = get_network_info()
        self.assertIn("sent_mb", info)
        self.assertIn("recv_mb", info)
        self.assertGreaterEqual(info["sent_mb"], 0)
        self.assertGreaterEqual(info["recv_mb"], 0)

    def test_get_system_info(self):
        """测试系统信息整合"""
        info = get_system_info()
        self.assertIn("timestamp", info)
        self.assertIn("cpu", info)
        self.assertIn("memory", info)
        self.assertIn("disk", info)
        self.assertIn("network", info)


if __name__ == "__main__":
    unittest.main()
