"""
内存池管理器
实现高效的内存池分配和管理
"""
from typing import List, Optional, Set
from datetime import datetime
from src.utils import print_success, print_error, print_info, format_size


class MemoryPool:
    """内存池类"""
    
    def __init__(self, block_size: int = 64, num_blocks: int = 100):
        """
        初始化内存池
        
        Args:
            block_size: 每个内存块的大小（字节）
            num_blocks: 内存块的数量
        """
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.total_size = block_size * num_blocks
        
        # 空闲块索引集合
        self.free_blocks: Set[int] = set(range(num_blocks))
        
        # 已分配块的信息：块索引 -> (进程ID, 分配时间)
        self.allocated_blocks = {}
        
        # 统计信息
        self.stats = {
            'total_allocations': 0,
            'total_frees': 0,
            'failed_allocations': 0,
            'current_allocated': 0,
            'peak_allocated': 0
        }
    
    def allocate(self, process_id: Optional[str] = None) -> Optional[int]:
        """
        从内存池分配一个块
        
        Args:
            process_id: 进程ID
        
        Returns:
            块索引，失败返回None
        """
        if not self.free_blocks:
            self.stats['failed_allocations'] += 1
            print_error(f"内存池已满，无法分配")
            return None
        
        # 获取一个空闲块
        block_index = self.free_blocks.pop()
        
        # 记录分配信息
        self.allocated_blocks[block_index] = (process_id, datetime.now())
        
        # 更新统计
        self.stats['total_allocations'] += 1
        self.stats['current_allocated'] += 1
        if self.stats['current_allocated'] > self.stats['peak_allocated']:
            self.stats['peak_allocated'] = self.stats['current_allocated']
        
        print_success(f"从内存池分配块 {block_index} (大小: {format_size(self.block_size)}, 进程: {process_id or 'N/A'})")
        return block_index
    
    def free(self, block_index: int) -> bool:
        """
        释放内存块
        
        Args:
            block_index: 块索引
        
        Returns:
            释放成功返回True，失败返回False
        """
        if block_index < 0 or block_index >= self.num_blocks:
            print_error(f"无效的块索引: {block_index}")
            return False
        
        if block_index in self.free_blocks:
            print_error(f"块 {block_index} 已经是空闲的（可能是重复释放）")
            return False
        
        if block_index not in self.allocated_blocks:
            print_error(f"块 {block_index} 不在已分配列表中")
            return False
        
        # 释放块
        del self.allocated_blocks[block_index]
        self.free_blocks.add(block_index)
        
        # 更新统计
        self.stats['total_frees'] += 1
        self.stats['current_allocated'] -= 1
        
        print_success(f"释放内存池块 {block_index}")
        return True
    
    def display_stats(self):
        """显示内存池统计信息"""
        print_info("=" * 60)
        print_info("内存池状态")
        print_info("=" * 60)
        
        print(f"\n配置:")
        print(f"  块大小: {format_size(self.block_size)}")
        print(f"  块数量: {self.num_blocks}")
        print(f"  总大小: {format_size(self.total_size)}")
        
        print(f"\n当前状态:")
        print(f"  空闲块: {len(self.free_blocks)}")
        print(f"  已分配块: {len(self.allocated_blocks)}")
        print(f"  利用率: {len(self.allocated_blocks) / self.num_blocks * 100:.2f}%")
        
        print(f"\n统计信息:")
        print(f"  总分配次数: {self.stats['total_allocations']}")
        print(f"  总释放次数: {self.stats['total_frees']}")
        print(f"  失败次数: {self.stats['failed_allocations']}")
        print(f"  当前已分配: {self.stats['current_allocated']}")
        print(f"  峰值分配: {self.stats['peak_allocated']}")
    
    def get_utilization(self) -> float:
        """获取内存池利用率"""
        return len(self.allocated_blocks) / self.num_blocks * 100
    
    def reset(self):
        """重置内存池"""
        self.free_blocks = set(range(self.num_blocks))
        self.allocated_blocks.clear()
        
        self.stats = {
            'total_allocations': 0,
            'total_frees': 0,
            'failed_allocations': 0,
            'current_allocated': 0,
            'peak_allocated': 0
        }
        print_success("内存池已重置")


class MultiSizeMemoryPool:
    """多尺寸内存池管理器"""
    
    def __init__(self, pool_configs: List[tuple] = None):
        """
        初始化多尺寸内存池
        
        Args:
            pool_configs: 池配置列表 [(block_size, num_blocks), ...]
        """
        if pool_configs is None:
            # 默认配置：小、中、大三种尺寸
            pool_configs = [
                (64, 100),    # 64B x 100
                (256, 50),    # 256B x 50
                (1024, 20)    # 1KB x 20
            ]
        
        self.pools = {}
        for block_size, num_blocks in pool_configs:
            self.pools[block_size] = MemoryPool(block_size, num_blocks)
        
        self.allocations = {}  # 指针 -> (pool_size, block_index)
        self.next_ptr = 0x10000
    
    def allocate(self, size: int, process_id: Optional[str] = None) -> Optional[int]:
        """
        分配内存（自动选择合适的池）
        
        Args:
            size: 请求的内存大小
            process_id: 进程ID
        
        Returns:
            内存指针，失败返回None
        """
        # 找到最小的能容纳的池
        suitable_pool = None
        pool_size = None
        
        for block_size in sorted(self.pools.keys()):
            if block_size >= size:
                suitable_pool = self.pools[block_size]
                pool_size = block_size
                break
        
        if suitable_pool is None:
            print_error(f"没有合适的内存池可以容纳 {format_size(size)}")
            return None
        
        # 从池中分配
        block_index = suitable_pool.allocate(process_id)
        if block_index is None:
            return None
        
        # 生成指针
        ptr = self.next_ptr
        self.next_ptr += pool_size
        
        # 记录分配
        self.allocations[ptr] = (pool_size, block_index)
        
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
            print_error(f"无效的指针: 0x{ptr:08x}")
            return False
        
        pool_size, block_index = self.allocations[ptr]
        pool = self.pools[pool_size]
        
        if pool.free(block_index):
            del self.allocations[ptr]
            return True
        
        return False
    
    def display_stats(self):
        """显示所有池的统计信息"""
        print_info("=" * 60)
        print_info("多尺寸内存池管理器状态")
        print_info("=" * 60)
        
        for block_size in sorted(self.pools.keys()):
            pool = self.pools[block_size]
            print(f"\n内存池 ({format_size(block_size)} 块):")
            print(f"  块数量: {pool.num_blocks}")
            print(f"  空闲: {len(pool.free_blocks)}")
            print(f"  已分配: {len(pool.allocated_blocks)}")
            print(f"  利用率: {pool.get_utilization():.2f}%")
    
    def reset(self):
        """重置所有池"""
        for pool in self.pools.values():
            pool.reset()
        self.allocations.clear()
        self.next_ptr = 0x10000
        print_success("多尺寸内存池管理器已重置")
