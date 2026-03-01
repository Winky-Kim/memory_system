"""
垃圾回收器测试
"""
import pytest
from src.garbage_collector import GarbageCollector


class TestGarbageCollector:
    """垃圾回收器测试类"""
    
    def test_create_object(self):
        """测试创建对象"""
        gc = GarbageCollector()
        
        obj_id = gc.create_object(100)
        assert obj_id > 0
        assert gc.stats['current_objects'] == 1
        assert gc.stats['current_bytes'] == 100
    
    def test_add_reference(self):
        """测试添加引用"""
        gc = GarbageCollector()
        
        obj1 = gc.create_object(100)
        obj2 = gc.create_object(200)
        
        gc.add_reference(obj1, obj2)
        
        assert gc.objects[obj2].ref_count == 1
    
    def test_remove_reference(self):
        """测试移除引用"""
        gc = GarbageCollector()
        
        obj1 = gc.create_object(100)
        obj2 = gc.create_object(200)
        
        gc.add_reference(obj1, obj2)
        gc.remove_reference(obj1, obj2)
        
        assert gc.objects[obj2].ref_count == 0
    
    def test_mark_sweep(self):
        """测试标记-清除算法"""
        gc = GarbageCollector(mode='mark_sweep')
        
        obj1 = gc.create_object(100, is_root=True)
        obj2 = gc.create_object(200)
        obj3 = gc.create_object(150)
        
        gc.add_reference(obj1, obj2)
        # obj3 没有被引用，是垃圾
        
        result = gc.collect()
        
        assert result['objects_collected'] == 1
        assert obj3 not in gc.objects
        assert obj1 in gc.objects
        assert obj2 in gc.objects
    
    def test_ref_count(self):
        """测试引用计数"""
        gc = GarbageCollector(mode='ref_count')
        
        obj1 = gc.create_object(100, is_root=True)
        obj2 = gc.create_object(200)
        
        gc.add_reference(obj1, obj2)
        
        # 移除引用后，obj2应该被回收（如果不是根对象）
        gc.remove_reference(obj1, obj2)
        
        assert obj2 not in gc.objects
    
    def test_root_set(self):
        """测试根集合"""
        gc = GarbageCollector(mode='mark_sweep')
        
        obj1 = gc.create_object(100, is_root=True)
        obj2 = gc.create_object(200, is_root=True)
        
        assert len(gc.root_set) == 2
        assert obj1 in gc.root_set
        assert obj2 in gc.root_set
    
    def test_add_remove_root(self):
        """测试添加和移除根对象"""
        gc = GarbageCollector()
        
        obj = gc.create_object(100)
        gc.add_root(obj)
        
        assert obj in gc.root_set
        
        gc.remove_root(obj)
        assert obj not in gc.root_set
    
    def test_generational(self):
        """测试分代回收"""
        gc = GarbageCollector(mode='generational')
        
        obj1 = gc.create_object(100, is_root=True)
        obj2 = gc.create_object(200)
        
        # 执行年轻代回收
        result = gc.collect(generation=0)
        
        # obj2应该被回收
        assert obj2 not in gc.objects
    
    def test_circular_reference(self):
        """测试循环引用"""
        gc = GarbageCollector(mode='mark_sweep')
        
        obj1 = gc.create_object(100)
        obj2 = gc.create_object(200)
        
        # 创建循环引用
        gc.add_reference(obj1, obj2)
        gc.add_reference(obj2, obj1)
        
        # 两个对象都不是根对象，应该被回收
        result = gc.collect()
        
        assert result['objects_collected'] == 2
    
    def test_statistics(self):
        """测试统计信息"""
        gc = GarbageCollector()
        
        obj1 = gc.create_object(100)
        obj2 = gc.create_object(200)
        
        assert gc.stats['total_objects_created'] == 2
        assert gc.stats['current_objects'] == 2
        assert gc.stats['current_bytes'] == 300


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
