"""
虚拟内存管理器测试
"""
import pytest
from src.virtual_memory import VirtualMemoryManager


class TestVirtualMemoryManager:
    """虚拟内存管理器测试类"""
    
    def test_page_hit(self):
        """测试页面命中"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=10, algorithm='lru')
        
        vm.access_page(1)
        hit = vm.access_page(1)  # 第二次访问应该命中
        
        assert hit is True
        assert vm.stats['page_faults'] == 1
    
    def test_page_fault(self):
        """测试页面缺失"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=3, algorithm='fifo')
        
        vm.access_page(1)
        vm.access_page(2)
        vm.access_page(3)
        vm.access_page(4)  # 应该触发页面置换
        
        assert vm.stats['page_faults'] == 4
        assert vm.stats['page_replacements'] == 1
    
    def test_fifo_algorithm(self):
        """测试FIFO算法"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=3, algorithm='fifo')
        
        # 访问序列: 1, 2, 3, 4
        for page in [1, 2, 3, 4]:
            vm.access_page(page)
        
        # 页面1应该被置换
        assert 1 not in [vm.frames[i] for i in range(vm.num_frames) if vm.frames[i] is not None]
    
    def test_lru_algorithm(self):
        """测试LRU算法"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=3, algorithm='lru')
        
        # 访问序列: 1, 2, 3, 1, 4
        for page in [1, 2, 3, 1, 4]:
            vm.access_page(page)
        
        # 页面2应该被置换（最久未使用）
        assert 2 not in [vm.frames[i] for i in range(vm.num_frames) if vm.frames[i] is not None]
    
    def test_address_translation(self):
        """测试地址转换"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=10, algorithm='lru')
        
        virtual_addr = 0x1234
        physical_addr = vm.translate_address(virtual_addr)
        
        assert physical_addr is not None
    
    def test_hit_rate(self):
        """测试命中率计算"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=10, algorithm='lru')
        
        # 访问一些页面
        for page in [1, 2, 3, 1, 2, 3]:
            vm.access_page(page)
        
        hit_rate = vm.get_hit_rate()
        assert hit_rate > 0
        assert hit_rate <= 100
    
    def test_reset(self):
        """测试重置"""
        vm = VirtualMemoryManager(page_size=4096, num_frames=10, algorithm='lru')
        
        vm.access_page(1)
        vm.access_page(2)
        
        vm.reset()
        
        assert vm.stats['page_accesses'] == 0
        assert len(vm.page_table) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
