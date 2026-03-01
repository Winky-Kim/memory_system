"""
内存分配器测试
"""
import pytest
from src.allocator import MemoryAllocator


class TestMemoryAllocator:
    """内存分配器测试类"""
    
    def test_first_fit(self):
        """测试首次适应算法"""
        allocator = MemoryAllocator(total_size=1000, algorithm='first_fit')
        
        ptr1 = allocator.allocate(100)
        ptr2 = allocator.allocate(200)
        ptr3 = allocator.allocate(150)
        
        assert ptr1 is not None
        assert ptr2 is not None
        assert ptr3 is not None
        assert allocator.stats['current_allocated'] == 450
    
    def test_best_fit(self):
        """测试最佳适应算法"""
        allocator = MemoryAllocator(total_size=1000, algorithm='best_fit')
        
        ptr1 = allocator.allocate(200)
        ptr2 = allocator.allocate(300)
        allocator.free(ptr1)
        
        # 现在有一个200字节的空洞和一个500字节的空洞
        ptr3 = allocator.allocate(150)
        
        assert ptr3 == ptr1  # 应该分配到200字节的空洞（最佳适应）
    
    def test_worst_fit(self):
        """测试最坏适应算法"""
        allocator = MemoryAllocator(total_size=1000, algorithm='worst_fit')
        
        ptr1 = allocator.allocate(100)
        ptr2 = allocator.allocate(200)
        ptr3 = allocator.allocate(300)
        
        allocator.free(ptr1)
        allocator.free(ptr3)
        
        # 现在有100和300字节的空洞
        ptr4 = allocator.allocate(50)
        
        # 最坏适应应该选择最大的空洞（300字节）
        assert ptr4 == ptr3
    
    def test_allocation_failure(self):
        """测试分配失败"""
        allocator = MemoryAllocator(total_size=100, algorithm='first_fit')
        
        ptr1 = allocator.allocate(60)
        ptr2 = allocator.allocate(50)  # 应该失败
        
        assert ptr1 is not None
        assert ptr2 is None
        assert allocator.stats['failed_allocations'] == 1
    
    def test_free_invalid_pointer(self):
        """测试释放无效指针"""
        allocator = MemoryAllocator(total_size=1000, algorithm='first_fit')
        
        result = allocator.free(12345)
        assert result is False
    
    def test_memory_merge(self):
        """测试内存块合并"""
        allocator = MemoryAllocator(total_size=1000, algorithm='first_fit')
        
        ptr1 = allocator.allocate(100)
        ptr2 = allocator.allocate(200)
        ptr3 = allocator.allocate(150)
        
        # 释放相邻的块
        allocator.free(ptr1)
        allocator.free(ptr2)
        
        # 块应该合并
        assert len([b for b in allocator.blocks if b.is_free]) >= 1
    
    def test_fragmentation(self):
        """测试碎片率计算"""
        allocator = MemoryAllocator(total_size=1000, algorithm='first_fit')
        
        ptr1 = allocator.allocate(100)
        ptr2 = allocator.allocate(100)
        ptr3 = allocator.allocate(100)
        
        allocator.free(ptr1)
        allocator.free(ptr3)
        
        frag = allocator.get_fragmentation()
        assert frag > 0  # 应该有碎片
    
    def test_reset(self):
        """测试重置"""
        allocator = MemoryAllocator(total_size=1000, algorithm='first_fit')
        
        allocator.allocate(100)
        allocator.allocate(200)
        
        allocator.reset()
        
        assert allocator.stats['current_allocated'] == 0
        assert len(allocator.blocks) == 1
        assert allocator.blocks[0].is_free is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
