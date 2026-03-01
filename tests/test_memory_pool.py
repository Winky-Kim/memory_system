"""
内存池测试
"""
import pytest
from src.memory_pool import MemoryPool, MultiSizeMemoryPool


class TestMemoryPool:
    """内存池测试类"""
    
    def test_allocate(self):
        """测试分配"""
        pool = MemoryPool(block_size=64, num_blocks=10)
        
        block = pool.allocate("P1")
        assert block is not None
        assert block in range(10)
        assert pool.stats['current_allocated'] == 1
    
    def test_free(self):
        """测试释放"""
        pool = MemoryPool(block_size=64, num_blocks=10)
        
        block = pool.allocate("P1")
        result = pool.free(block)
        
        assert result is True
        assert pool.stats['current_allocated'] == 0
    
    def test_pool_exhaustion(self):
        """测试池耗尽"""
        pool = MemoryPool(block_size=64, num_blocks=3)
        
        b1 = pool.allocate("P1")
        b2 = pool.allocate("P2")
        b3 = pool.allocate("P3")
        b4 = pool.allocate("P4")  # 应该失败
        
        assert b1 is not None
        assert b2 is not None
        assert b3 is not None
        assert b4 is None
        assert pool.stats['failed_allocations'] == 1
    
    def test_double_free(self):
        """测试重复释放"""
        pool = MemoryPool(block_size=64, num_blocks=10)
        
        block = pool.allocate("P1")
        pool.free(block)
        result = pool.free(block)  # 重复释放
        
        assert result is False
    
    def test_invalid_block(self):
        """测试无效块索引"""
        pool = MemoryPool(block_size=64, num_blocks=10)
        
        result = pool.free(999)
        assert result is False
    
    def test_utilization(self):
        """测试利用率计算"""
        pool = MemoryPool(block_size=64, num_blocks=10)
        
        pool.allocate("P1")
        pool.allocate("P2")
        pool.allocate("P3")
        
        util = pool.get_utilization()
        assert util == 30.0  # 3/10 = 30%


class TestMultiSizeMemoryPool:
    """多尺寸内存池测试类"""
    
    def test_allocate_small(self):
        """测试分配小块"""
        pool = MultiSizeMemoryPool()
        
        ptr = pool.allocate(32, "P1")
        assert ptr is not None
    
    def test_allocate_medium(self):
        """测试分配中等块"""
        pool = MultiSizeMemoryPool()
        
        ptr = pool.allocate(150, "P1")
        assert ptr is not None
    
    def test_allocate_large(self):
        """测试分配大块"""
        pool = MultiSizeMemoryPool()
        
        ptr = pool.allocate(800, "P1")
        assert ptr is not None
    
    def test_allocate_too_large(self):
        """测试分配过大的块"""
        pool = MultiSizeMemoryPool()
        
        ptr = pool.allocate(2000, "P1")
        assert ptr is None
    
    def test_free(self):
        """测试释放"""
        pool = MultiSizeMemoryPool()
        
        ptr = pool.allocate(100, "P1")
        result = pool.free(ptr)
        
        assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
