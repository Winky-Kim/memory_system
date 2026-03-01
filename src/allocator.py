"""
动态内存分配器
实现多种内存分配算法：首次适应、最佳适应、最坏适应、下次适应
"""
from typing import Optional, List, Dict
from datetime import datetime
from src.utils import MemoryBlock, print_success, print_error, print_info, visualize_memory, format_size


class MemoryAllocator:
    """内存分配器类"""
    
    def __init__(self, total_size: int = 1024 * 1024, algorithm: str = 'first_fit'):
        """
        初始化内存分配器
        
        Args:
            total_size: 总内存大小（字节）
            algorithm: 分配算法 ('first_fit', 'best_fit', 'worst_fit', 'next_fit')
        """
        self.total_size = total_size
        self.algorithm = algorithm
        self.blocks: List[MemoryBlock] = [MemoryBlock(0, total_size, True)]
        self.allocations: Dict[int, MemoryBlock] = {}  # 指针 -> 内存块
        self.next_fit_index = 0  # 下次适应算法的起始位置
        
        # 统计信息
        self.stats = {
            'total_allocations': 0,
            'total_frees': 0,
            'failed_allocations': 0,
            'current_allocated': 0,
            'peak_allocated': 0
        }
    
    def allocate(self, size: int, process_id: str = None) -> Optional[int]:
        """
        分配内存
        
        Args:
            size: 请求的内存大小
            process_id: 进程ID
        
        Returns:
            分配成功返回内存指针（起始地址），失败返回None
        """
        if size <= 0:
            print_error(f"无效的分配大小: {size}")
            return None
        
        # 根据算法选择合适的内存块
        if self.algorithm == 'first_fit':
            block_index = self._first_fit(size)
        elif self.algorithm == 'best_fit':
            block_index = self._best_fit(size)
        elif self.algorithm == 'worst_fit':
            block_index = self._worst_fit(size)
        elif self.algorithm == 'next_fit':
            block_index = self._next_fit(size)
        else:
            print_error(f"未知的分配算法: {self.algorithm}")
            return None
        
        if block_index is None:
            self.stats['failed_allocations'] += 1
            print_error(f"分配失败：找不到大小为 {format_size(size)} 的空闲块")
            return None
        
        # 执行分配
        block = self.blocks[block_index]
        ptr = block.start
        
        # 如果块大小正好，直接标记为已用
        if block.size == size:
            block.is_free = False
            block.process_id = process_id
            block.allocation_time = datetime.now()
        else:
            # 分割内存块
            new_block = MemoryBlock(block.start, size, False, process_id)
            new_block.allocation_time = datetime.now()
            
            # 更新原块
            block.start += size
            block.size -= size
            
            # 插入新块
            self.blocks.insert(block_index, new_block)
        
        # 记录分配
        self.allocations[ptr] = self.blocks[block_index] if block.size == size else self.blocks[block_index]
        
        # 更新统计
        self.stats['total_allocations'] += 1
        self.stats['current_allocated'] += size
        if self.stats['current_allocated'] > self.stats['peak_allocated']:
            self.stats['peak_allocated'] = self.stats['current_allocated']
        
        print_success(f"分配成功: {format_size(size)} at 0x{ptr:08x} (进程: {process_id or 'N/A'})")
        return ptr
    
    def free(self, ptr: int) -> bool:
        """
        释放内存
        
        Args:
            ptr: 内存指针（起始地址）
        
        Returns:
            释放成功返回True，失败返回False
        """
        if ptr not in self.allocations:
            print_error(f"无效的指针: 0x{ptr:08x}")
            return False
        
        # 找到对应的内存块
        block_to_free = None
        block_index = -1
        for i, block in enumerate(self.blocks):
            if block.start == ptr and not block.is_free:
                block_to_free = block
                block_index = i
                break
        
        if block_to_free is None:
            print_error(f"未找到指针 0x{ptr:08x} 对应的内存块")
            return False
        
        # 标记为空闲
        size = block_to_free.size
        block_to_free.is_free = True
        block_to_free.process_id = None
        block_to_free.allocation_time = None
        
        # 删除分配记录
        del self.allocations[ptr]
        
        # 合并相邻的空闲块
        self._merge_free_blocks(block_index)
        
        # 更新统计
        self.stats['total_frees'] += 1
        self.stats['current_allocated'] -= size
        
        print_success(f"释放成功: {format_size(size)} at 0x{ptr:08x}")
        return True
    
    def _first_fit(self, size: int) -> Optional[int]:
        """首次适应算法：返回第一个足够大的空闲块的索引"""
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                return i
        return None
    
    def _best_fit(self, size: int) -> Optional[int]:
        """最佳适应算法：返回最小的足够大的空闲块的索引"""
        best_index = None
        best_size = float('inf')
        
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size < best_size:
                    best_size = block.size
                    best_index = i
        
        return best_index
    
    def _worst_fit(self, size: int) -> Optional[int]:
        """最坏适应算法：返回最大的空闲块的索引"""
        worst_index = None
        worst_size = 0
        
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size > worst_size:
                    worst_size = block.size
                    worst_index = i
        
        return worst_index
    
    def _next_fit(self, size: int) -> Optional[int]:
        """下次适应算法：从上次分配的位置开始查找"""
        n = len(self.blocks)
        
        # 从上次位置开始查找
        for i in range(n):
            index = (self.next_fit_index + i) % n
            block = self.blocks[index]
            if block.is_free and block.size >= size:
                self.next_fit_index = index
                return index
        
        return None
    
    def _merge_free_blocks(self, start_index: int):
        """合并相邻的空闲块"""
        i = start_index
        while i < len(self.blocks) - 1:
            current = self.blocks[i]
            next_block = self.blocks[i + 1]
            
            # 如果当前块和下一块都是空闲的，合并它们
            if current.is_free and next_block.is_free:
                current.size += next_block.size
                self.blocks.pop(i + 1)
            else:
                i += 1
        
        # 向前合并
        i = start_index
        while i > 0:
            current = self.blocks[i]
            prev_block = self.blocks[i - 1]
            
            if current.is_free and prev_block.is_free:
                prev_block.size += current.size
                self.blocks.pop(i)
                i -= 1
            else:
                break
    
    def display_memory(self):
        """显示内存状态"""
        print_info("=" * 60)
        print_info(f"内存分配器状态 (算法: {self.algorithm})")
        print_info("=" * 60)
        
        visualize_memory(self.blocks, self.total_size)
        
        # 显示统计信息
        print(f"\n统计信息:")
        print(f"  总分配次数: {self.stats['total_allocations']}")
        print(f"  总释放次数: {self.stats['total_frees']}")
        print(f"  失败次数: {self.stats['failed_allocations']}")
        print(f"  当前已分配: {format_size(self.stats['current_allocated'])}")
        print(f"  峰值分配: {format_size(self.stats['peak_allocated'])}")
        print(f"  内存利用率: {self.stats['current_allocated'] / self.total_size * 100:.2f}%")
        
        # 计算碎片率
        free_blocks = [b for b in self.blocks if b.is_free]
        if free_blocks:
            total_free = sum(b.size for b in free_blocks)
            largest_free = max(b.size for b in free_blocks)
            fragmentation = (1 - largest_free / total_free) * 100 if total_free > 0 else 0
            print(f"  碎片率: {fragmentation:.2f}%")
            print(f"  空闲块数量: {len(free_blocks)}")
    
    def get_fragmentation(self) -> float:
        """计算内存碎片率"""
        free_blocks = [b for b in self.blocks if b.is_free]
        if not free_blocks:
            return 0.0
        
        total_free = sum(b.size for b in free_blocks)
        if total_free == 0:
            return 0.0
        
        largest_free = max(b.size for b in free_blocks)
        return (1 - largest_free / total_free) * 100
    
    def reset(self):
        """重置内存分配器"""
        self.blocks = [MemoryBlock(0, self.total_size, True)]
        self.allocations.clear()
        self.next_fit_index = 0
        
        self.stats = {
            'total_allocations': 0,
            'total_frees': 0,
            'failed_allocations': 0,
            'current_allocated': 0,
            'peak_allocated': 0
        }
        print_success("内存分配器已重置")
