"""
内存泄漏检测器
跟踪内存分配和释放，检测未释放的内存块
"""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from src.utils import print_success, print_error, print_warning, print_info, format_size
import traceback


@dataclass
class AllocationInfo:
    """内存分配信息"""
    ptr: int
    size: int
    timestamp: datetime
    process_id: Optional[str]
    stack_trace: List[str]  # 调用堆栈
    is_freed: bool = False
    freed_timestamp: Optional[datetime] = None


class MemoryLeakDetector:
    """内存泄漏检测器"""
    
    def __init__(self, enable_stack_trace: bool = True):
        """
        初始化内存泄漏检测器
        
        Args:
            enable_stack_trace: 是否启用调用堆栈跟踪
        """
        self.enable_stack_trace = enable_stack_trace
        self.allocations: Dict[int, AllocationInfo] = {}
        self.next_ptr = 0x1000  # 起始地址
        
        # 统计信息
        self.stats = {
            'total_allocations': 0,
            'total_frees': 0,
            'current_allocations': 0,
            'total_allocated_bytes': 0,
            'total_freed_bytes': 0,
            'current_allocated_bytes': 0,
            'peak_allocated_bytes': 0,
            'leaked_blocks': 0,
            'leaked_bytes': 0
        }
    
    def allocate(self, size: int, process_id: Optional[str] = None) -> int:
        """
        分配内存
        
        Args:
            size: 要分配的内存大小
            process_id: 进程ID
        
        Returns:
            内存指针
        """
        if size <= 0:
            print_error(f"无效的分配大小: {size}")
            return 0
        
        # 生成指针
        ptr = self.next_ptr
        self.next_ptr += size
        
        # 获取调用堆栈
        stack_trace = []
        if self.enable_stack_trace:
            stack = traceback.extract_stack()[:-1]  # 排除当前函数
            stack_trace = [f"{frame.filename}:{frame.lineno} in {frame.name}" 
                          for frame in stack[-5:]]  # 只保留最近5层
        
        # 记录分配信息
        alloc_info = AllocationInfo(
            ptr=ptr,
            size=size,
            timestamp=datetime.now(),
            process_id=process_id,
            stack_trace=stack_trace
        )
        self.allocations[ptr] = alloc_info
        
        # 更新统计
        self.stats['total_allocations'] += 1
        self.stats['current_allocations'] += 1
        self.stats['total_allocated_bytes'] += size
        self.stats['current_allocated_bytes'] += size
        
        if self.stats['current_allocated_bytes'] > self.stats['peak_allocated_bytes']:
            self.stats['peak_allocated_bytes'] = self.stats['current_allocated_bytes']
        
        print_success(f"分配: {format_size(size)} at 0x{ptr:08x} (进程: {process_id or 'N/A'})")
        return ptr
    
    def free(self, ptr: int) -> bool:
        """
        释放内存
        
        Args:
            ptr: 内存指针
        
        Returns:
            释放成功返回True，失败返回False
        """
        if ptr not in self.allocations:
            print_error(f"无效的指针: 0x{ptr:08x} (可能是重复释放或野指针)")
            return False
        
        alloc_info = self.allocations[ptr]
        
        if alloc_info.is_freed:
            print_error(f"重复释放: 0x{ptr:08x}")
            return False
        
        # 标记为已释放
        alloc_info.is_freed = True
        alloc_info.freed_timestamp = datetime.now()
        
        # 更新统计
        self.stats['total_frees'] += 1
        self.stats['current_allocations'] -= 1
        self.stats['total_freed_bytes'] += alloc_info.size
        self.stats['current_allocated_bytes'] -= alloc_info.size
        
        print_success(f"释放: {format_size(alloc_info.size)} at 0x{ptr:08x}")
        return True
    
    def check_leaks(self) -> Dict:
        """
        检查内存泄漏
        
        Returns:
            包含泄漏信息的字典
        """
        leaked_blocks = []
        leaked_bytes = 0
        
        for ptr, alloc_info in self.allocations.items():
            if not alloc_info.is_freed:
                leaked_blocks.append(alloc_info)
                leaked_bytes += alloc_info.size
        
        # 更新统计
        self.stats['leaked_blocks'] = len(leaked_blocks)
        self.stats['leaked_bytes'] = leaked_bytes
        
        # 生成报告
        report = {
            'has_leaks': len(leaked_blocks) > 0,
            'leaked_blocks': leaked_blocks,
            'leaked_bytes': leaked_bytes,
            'leak_count': len(leaked_blocks)
        }
        
        return report
    
    def print_leak_report(self):
        """打印内存泄漏报告"""
        print_info("=" * 60)
        print_info("内存泄漏检测报告")
        print_info("=" * 60)
        
        report = self.check_leaks()
        
        if not report['has_leaks']:
            print_success("✓ 未检测到内存泄漏！")
        else:
            print_error(f"✗ 检测到 {report['leak_count']} 个内存泄漏，"
                       f"共泄漏 {format_size(report['leaked_bytes'])}")
            
            print(f"\n泄漏详情:")
            for i, alloc_info in enumerate(report['leaked_blocks'], 1):
                print(f"\n  泄漏 #{i}:")
                print(f"    地址: 0x{alloc_info.ptr:08x}")
                print(f"    大小: {format_size(alloc_info.size)}")
                print(f"    进程: {alloc_info.process_id or 'N/A'}")
                print(f"    分配时间: {alloc_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if alloc_info.stack_trace:
                    print(f"    调用堆栈:")
                    for frame in alloc_info.stack_trace:
                        print(f"      {frame}")
        
        # 打印统计信息
        print(f"\n统计信息:")
        print(f"  总分配次数: {self.stats['total_allocations']}")
        print(f"  总释放次数: {self.stats['total_frees']}")
        print(f"  当前活动分配: {self.stats['current_allocations']}")
        print(f"  总分配字节: {format_size(self.stats['total_allocated_bytes'])}")
        print(f"  总释放字节: {format_size(self.stats['total_freed_bytes'])}")
        print(f"  当前占用: {format_size(self.stats['current_allocated_bytes'])}")
        print(f"  峰值占用: {format_size(self.stats['peak_allocated_bytes'])}")
        
        if self.stats['total_allocations'] > 0:
            free_rate = self.stats['total_frees'] / self.stats['total_allocations'] * 100
            print(f"  释放率: {free_rate:.2f}%")
    
    def get_allocation_info(self, ptr: int) -> Optional[AllocationInfo]:
        """获取指定指针的分配信息"""
        return self.allocations.get(ptr)
    
    def get_all_allocations(self) -> List[AllocationInfo]:
        """获取所有分配信息"""
        return list(self.allocations.values())
    
    def get_active_allocations(self) -> List[AllocationInfo]:
        """获取所有活动的（未释放的）分配"""
        return [info for info in self.allocations.values() if not info.is_freed]
    
    def display_status(self):
        """显示当前状态"""
        print_info("=" * 60)
        print_info("内存泄漏检测器状态")
        print_info("=" * 60)
        
        active_allocs = self.get_active_allocations()
        
        print(f"\n当前活动分配 (共 {len(active_allocs)} 个):")
        if active_allocs:
            for alloc in sorted(active_allocs, key=lambda x: x.timestamp):
                age = (datetime.now() - alloc.timestamp).total_seconds()
                print(f"  0x{alloc.ptr:08x}: {format_size(alloc.size)} | "
                      f"进程: {alloc.process_id or 'N/A'} | "
                      f"存活时间: {age:.1f}s")
        else:
            print("  (无)")
        
        print(f"\n统计信息:")
        print(f"  总分配: {self.stats['total_allocations']}")
        print(f"  总释放: {self.stats['total_frees']}")
        print(f"  当前活动: {self.stats['current_allocations']}")
        print(f"  当前占用: {format_size(self.stats['current_allocated_bytes'])}")
        print(f"  峰值占用: {format_size(self.stats['peak_allocated_bytes'])}")
    
    def reset(self):
        """重置检测器"""
        self.allocations.clear()
        self.next_ptr = 0x1000
        
        self.stats = {
            'total_allocations': 0,
            'total_frees': 0,
            'current_allocations': 0,
            'total_allocated_bytes': 0,
            'total_freed_bytes': 0,
            'current_allocated_bytes': 0,
            'peak_allocated_bytes': 0,
            'leaked_blocks': 0,
            'leaked_bytes': 0
        }
        print_success("内存泄漏检测器已重置")
    
    def simulate_leak(self, size: int, process_id: Optional[str] = None):
        """模拟内存泄漏（用于测试）"""
        ptr = self.allocate(size, process_id)
        print_warning(f"模拟泄漏: {format_size(size)} at 0x{ptr:08x}")
        return ptr
