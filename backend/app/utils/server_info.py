import os
import platform
import socket
import sys

from datetime import datetime, timedelta
from datetime import timezone as tz
from typing import List

import psutil

from backend.app.utils.timezone import timezone


class ServerInfo:
    @staticmethod
    def format_bytes(size) -> str:
        """바이트 형식화"""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if abs(size) < factor:
                return f"{size:.2f} {unit}B"
            size /= factor
        return f"{size:.2f} YB"

    @staticmethod
    def fmt_seconds(seconds: int) -> str:
        days, rem = divmod(int(seconds), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        parts = []
        if days:
            parts.append("{}일".format(days))
        if hours:
            parts.append("{}시간".format(hours))
        if minutes:
            parts.append("{}분".format(minutes))
        if seconds:
            parts.append("{}초".format(seconds))
        if len(parts) == 0:
            return "0초"
        else:
            return " ".join(parts)

    @staticmethod
    def fmt_timedelta(td: timedelta) -> str:
        """시간 간격 형식화"""
        total_seconds = round(td.total_seconds())
        return ServerInfo.fmt_seconds(total_seconds)

    @staticmethod
    def get_cpu_info() -> dict:
        """CPU 정보 가져오기"""
        cpu_info = {
            "usage": round(psutil.cpu_percent(interval=1, percpu=False), 2)
        }  # %

        # CPU 주파수 정보, 최대, 최소 및 현재 주파수
        cpu_freq = psutil.cpu_freq()
        cpu_info["max_freq"] = round(cpu_freq.max, 2)  # MHz
        cpu_info["min_freq"] = round(cpu_freq.min, 2)  # MHz
        cpu_info["current_freq"] = round(cpu_freq.current, 2)  # MHz

        # CPU 논리 코어 수, 물리 코어 수
        cpu_info["logical_num"] = psutil.cpu_count(logical=True)
        cpu_info["physical_num"] = psutil.cpu_count(logical=False)
        return cpu_info

    @staticmethod
    def get_mem_info() -> dict:
        """메모리 정보 가져오기"""
        mem = psutil.virtual_memory()
        return {
            "total": round(mem.total / 1024 / 1024 / 1024, 2),  # GB
            "used": round(mem.used / 1024 / 1024 / 1024, 2),  # GB
            "free": round(mem.available / 1024 / 1024 / 1024, 2),  # GB
            "usage": round(mem.percent, 2),  # %
        }

    @staticmethod
    def get_sys_info() -> dict:
        """서버 정보 가져오기"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sk:
                sk.connect(("8.8.8.8", 80))
                ip = sk.getsockname()[0]
        except socket.gaierror:
            ip = "127.0.0.1"
        return {
            "name": socket.gethostname(),
            "ip": ip,
            "os": platform.system(),
            "arch": platform.machine(),
        }

    @staticmethod
    def get_disk_info() -> List[dict]:
        """디스크 정보 가져오기"""
        disk_info = []
        for disk in psutil.disk_partitions():
            usage = psutil.disk_usage(disk.mountpoint)
            disk_info.append(
                {
                    "dir": disk.mountpoint,
                    "type": disk.fstype,
                    "device": disk.device,
                    "total": ServerInfo.format_bytes(usage.total),
                    "free": ServerInfo.format_bytes(usage.free),
                    "used": ServerInfo.format_bytes(usage.used),
                    "usage": f"{round(usage.percent, 2)} %",
                }
            )
        return disk_info

    @staticmethod
    def get_service_info():
        """서비스 정보 가져오기"""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        start_time = timezone.f_datetime(
            datetime.utcfromtimestamp(process.create_time()).replace(tzinfo=tz.utc)
        )
        return {
            "name": "Python3",
            "version": platform.python_version(),
            "home": sys.executable,
            "cpu_usage": f"{round(process.cpu_percent(interval=1), 2)} %",
            "mem_vms": ServerInfo.format_bytes(
                mem_info.vms
            ),  # 가상 메모리, 현재 프로세스에서 요청한 가상 메모리
            "mem_rss": ServerInfo.format_bytes(
                mem_info.rss
            ),  # 상주 메모리, 현재 프로세스가 실제로 사용하는 물리적 메모리
            "mem_free": ServerInfo.format_bytes(
                mem_info.vms - mem_info.rss
            ),  # 빈 메모리
            "startup": start_time,
            "elapsed": f"{ServerInfo.fmt_timedelta(timezone.now() - start_time)}",
        }


server_info = ServerInfo()
