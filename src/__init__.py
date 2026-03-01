"""
内存管理模拟器
"""

__version__ = "1.0.0"
__author__ = "Memory System Simulator"

from src.allocator import MemoryAllocator
from src.virtual_memory import VirtualMemoryManager
from src.leak_detector import MemoryLeakDetector
from src.memory_pool import MemoryPool, MultiSizeMemoryPool
from src.garbage_collector import GarbageCollector

__all__ = [
    'MemoryAllocator',
    'VirtualMemoryManager',
    'MemoryLeakDetector',
    'MemoryPool',
    'MultiSizeMemoryPool',
    'GarbageCollector',
]
