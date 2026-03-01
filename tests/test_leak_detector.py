"""
内存泄漏检测器测试
"""
import pytest
from src.leak_detector import MemoryLeakDetector


class TestMemoryLeakDetector:
    """内存泄漏检测器测试类"""
    
    def test_allocate_and_free(self):
        """测试正常的分配和释放"""
        detector = MemoryLeakDetector()
        
        ptr = detector.allocate(100, "P1")
        assert ptr != 0
        assert detector.stats['current_allocations'] == 1
        
        result = detector.free(ptr)
        assert result is True
        assert detector.stats['current_allocations'] == 0
    
    def test_detect_leak(self):
        """测试检测内存泄漏"""
        detector = MemoryLeakDetector()
        
        ptr1 = detector.allocate(100, "P1")
        ptr2 = detector.allocate(200, "P2")
        
        # 只释放一个
        detector.free(ptr1)
        
        report = detector.check_leaks()
        
        assert report['has_leaks'] is True
        assert report['leak_count'] == 1
        assert report['leaked_bytes'] == 200
    
    def test_no_leak(self):
        """测试无泄漏情况"""
        detector = MemoryLeakDetector()
        
        ptr1 = detector.allocate(100, "P1")
        ptr2 = detector.allocate(200, "P2")
        
        detector.free(ptr1)
        detector.free(ptr2)
        
        report = detector.check_leaks()
        
        assert report['has_leaks'] is False
        assert report['leak_count'] == 0
    
    def test_double_free(self):
        """测试重复释放"""
        detector = MemoryLeakDetector()
        
        ptr = detector.allocate(100, "P1")
        detector.free(ptr)
        result = detector.free(ptr)  # 重复释放
        
        assert result is False
    
    def test_invalid_pointer(self):
        """测试无效指针"""
        detector = MemoryLeakDetector()
        
        result = detector.free(99999)
        assert result is False
    
    def test_allocation_info(self):
        """测试分配信息"""
        detector = MemoryLeakDetector(enable_stack_trace=True)
        
        ptr = detector.allocate(100, "P1")
        info = detector.get_allocation_info(ptr)
        
        assert info is not None
        assert info.size == 100
        assert info.process_id == "P1"
        assert info.is_freed is False
    
    def test_active_allocations(self):
        """测试获取活动分配"""
        detector = MemoryLeakDetector()
        
        ptr1 = detector.allocate(100, "P1")
        ptr2 = detector.allocate(200, "P2")
        detector.free(ptr1)
        
        active = detector.get_active_allocations()
        
        assert len(active) == 1
        assert active[0].size == 200
    
    def test_statistics(self):
        """测试统计信息"""
        detector = MemoryLeakDetector()
        
        ptr1 = detector.allocate(100, "P1")
        ptr2 = detector.allocate(200, "P2")
        detector.free(ptr1)
        
        assert detector.stats['total_allocations'] == 2
        assert detector.stats['total_frees'] == 1
        assert detector.stats['current_allocations'] == 1
        assert detector.stats['total_allocated_bytes'] == 300
        assert detector.stats['total_freed_bytes'] == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
