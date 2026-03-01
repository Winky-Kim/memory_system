"""
垃圾回收器
实现标记-清除算法和引用计数
"""
from typing import Dict, Set, List, Optional
from datetime import datetime
from src.utils import print_success, print_error, print_info, print_warning, format_size


class GCObject:
    """垃圾回收对象"""
    
    def __init__(self, obj_id: int, size: int, generation: int = 0):
        self.obj_id = obj_id
        self.size = size
        self.generation = generation  # 分代回收：0-新生代，1-老年代，2-永久代
        self.ref_count = 0
        self.marked = False
        self.references: Set[int] = set()  # 该对象引用的其他对象ID
        self.creation_time = datetime.now()
        self.last_access_time = datetime.now()
    
    def __repr__(self):
        return f"Object({self.obj_id}, {format_size(self.size)}, refs={self.ref_count}, gen={self.generation})"


class GarbageCollector:
    """垃圾回收器"""
    
    def __init__(self, mode: str = 'mark_sweep'):
        """
        初始化垃圾回收器
        
        Args:
            mode: 回收模式 ('mark_sweep', 'ref_count', 'generational')
        """
        self.mode = mode
        self.objects: Dict[int, GCObject] = {}
        self.root_set: Set[int] = set()  # 根对象集合
        self.next_id = 1
        
        # 统计信息
        self.stats = {
            'total_objects_created': 0,
            'total_collections': 0,
            'total_objects_collected': 0,
            'total_bytes_collected': 0,
            'current_objects': 0,
            'current_bytes': 0,
            'collection_time_ms': 0
        }
    
    def create_object(self, size: int, is_root: bool = False) -> int:
        """
        创建对象
        
        Args:
            size: 对象大小
            is_root: 是否为根对象
        
        Returns:
            对象ID
        """
        obj_id = self.next_id
        self.next_id += 1
        
        obj = GCObject(obj_id, size)
        self.objects[obj_id] = obj
        
        if is_root:
            self.root_set.add(obj_id)
        
        # 更新统计
        self.stats['total_objects_created'] += 1
        self.stats['current_objects'] += 1
        self.stats['current_bytes'] += size
        
        print_success(f"创建对象 {obj_id} (大小: {format_size(size)}, 根: {is_root})")
        return obj_id
    
    def add_reference(self, from_obj_id: int, to_obj_id: int):
        """
        添加对象间的引用关系
        
        Args:
            from_obj_id: 源对象ID
            to_obj_id: 目标对象ID
        """
        if from_obj_id not in self.objects:
            print_error(f"对象 {from_obj_id} 不存在")
            return
        
        if to_obj_id not in self.objects:
            print_error(f"对象 {to_obj_id} 不存在")
            return
        
        from_obj = self.objects[from_obj_id]
        to_obj = self.objects[to_obj_id]
        
        # 添加引用
        if to_obj_id not in from_obj.references:
            from_obj.references.add(to_obj_id)
            to_obj.ref_count += 1
            print_info(f"添加引用: {from_obj_id} -> {to_obj_id}")
    
    def remove_reference(self, from_obj_id: int, to_obj_id: int):
        """
        移除对象间的引用关系
        
        Args:
            from_obj_id: 源对象ID
            to_obj_id: 目标对象ID
        """
        if from_obj_id not in self.objects or to_obj_id not in self.objects:
            return
        
        from_obj = self.objects[from_obj_id]
        to_obj = self.objects[to_obj_id]
        
        if to_obj_id in from_obj.references:
            from_obj.references.remove(to_obj_id)
            to_obj.ref_count -= 1
            print_info(f"移除引用: {from_obj_id} -> {to_obj_id}")
            
            # 引用计数模式下，立即检查是否需要回收
            if self.mode == 'ref_count' and to_obj.ref_count == 0 and to_obj_id not in self.root_set:
                self._collect_object(to_obj_id)
    
    def add_root(self, obj_id: int):
        """添加根对象"""
        if obj_id in self.objects:
            self.root_set.add(obj_id)
            print_info(f"对象 {obj_id} 添加到根集合")
    
    def remove_root(self, obj_id: int):
        """移除根对象"""
        if obj_id in self.root_set:
            self.root_set.remove(obj_id)
            print_info(f"对象 {obj_id} 从根集合移除")
    
    def collect(self, generation: Optional[int] = None) -> Dict:
        """
        执行垃圾回收
        
        Args:
            generation: 要回收的代（用于分代回收）
        
        Returns:
            回收结果字典
        """
        start_time = datetime.now()
        
        print_info("=" * 60)
        print_info(f"开始垃圾回收 (模式: {self.mode})")
        print_info("=" * 60)
        
        if self.mode == 'mark_sweep':
            result = self._mark_sweep_collect()
        elif self.mode == 'ref_count':
            result = self._ref_count_collect()
        elif self.mode == 'generational':
            result = self._generational_collect(generation)
        else:
            print_error(f"未知的回收模式: {self.mode}")
            return {}
        
        # 计算耗时
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        result['collection_time_ms'] = elapsed
        
        # 更新统计
        self.stats['total_collections'] += 1
        self.stats['total_objects_collected'] += result['objects_collected']
        self.stats['total_bytes_collected'] += result['bytes_collected']
        self.stats['collection_time_ms'] += elapsed
        
        print_success(f"垃圾回收完成: 回收 {result['objects_collected']} 个对象, "
                     f"{format_size(result['bytes_collected'])}, 耗时 {elapsed:.2f}ms")
        
        return result
    
    def _mark_sweep_collect(self) -> Dict:
        """标记-清除算法"""
        # 1. 标记阶段：从根对象开始标记所有可达对象
        self._mark_phase()
        
        # 2. 清除阶段：回收未标记的对象
        collected_objects = []
        collected_bytes = 0
        
        for obj_id in list(self.objects.keys()):
            obj = self.objects[obj_id]
            if not obj.marked:
                collected_objects.append(obj_id)
                collected_bytes += obj.size
                self._collect_object(obj_id)
        
        # 3. 清除标记
        for obj in self.objects.values():
            obj.marked = False
        
        return {
            'objects_collected': len(collected_objects),
            'bytes_collected': collected_bytes,
            'collected_ids': collected_objects
        }
    
    def _mark_phase(self):
        """标记阶段：DFS遍历"""
        visited = set()
        
        def mark(obj_id):
            if obj_id in visited or obj_id not in self.objects:
                return
            
            visited.add(obj_id)
            obj = self.objects[obj_id]
            obj.marked = True
            
            # 递归标记引用的对象
            for ref_id in obj.references:
                mark(ref_id)
        
        # 从根集合开始标记
        for root_id in self.root_set:
            mark(root_id)
    
    def _ref_count_collect(self) -> Dict:
        """引用计数回收"""
        collected_objects = []
        collected_bytes = 0
        
        # 回收引用计数为0且不是根对象的对象
        for obj_id in list(self.objects.keys()):
            obj = self.objects[obj_id]
            if obj.ref_count == 0 and obj_id not in self.root_set:
                collected_objects.append(obj_id)
                collected_bytes += obj.size
                self._collect_object(obj_id)
        
        return {
            'objects_collected': len(collected_objects),
            'bytes_collected': collected_bytes,
            'collected_ids': collected_objects
        }
    
    def _generational_collect(self, generation: Optional[int] = None) -> Dict:
        """分代回收"""
        # 提升对象到更老的代
        self._promote_objects()
        
        # 如果指定了代，只回收该代；否则回收年轻代（0代）
        target_gen = generation if generation is not None else 0
        
        print_info(f"回收第 {target_gen} 代")
        
        # 使用标记-清除算法回收指定代
        self._mark_phase()
        
        collected_objects = []
        collected_bytes = 0
        
        for obj_id in list(self.objects.keys()):
            obj = self.objects[obj_id]
            if obj.generation == target_gen and not obj.marked:
                collected_objects.append(obj_id)
                collected_bytes += obj.size
                self._collect_object(obj_id)
        
        # 清除标记
        for obj in self.objects.values():
            obj.marked = False
        
        return {
            'objects_collected': len(collected_objects),
            'bytes_collected': collected_bytes,
            'collected_ids': collected_objects,
            'generation': target_gen
        }
    
    def _promote_objects(self):
        """提升存活时间长的对象到更老的代"""
        current_time = datetime.now()
        
        for obj in self.objects.values():
            age = (current_time - obj.creation_time).total_seconds()
            
            # 根据存活时间提升代数
            if age > 60 and obj.generation == 0:  # 存活超过60秒
                obj.generation = 1
                print_info(f"对象 {obj.obj_id} 提升到老年代")
            elif age > 300 and obj.generation == 1:  # 存活超过5分钟
                obj.generation = 2
                print_info(f"对象 {obj.obj_id} 提升到永久代")
    
    def _collect_object(self, obj_id: int):
        """回收单个对象"""
        if obj_id not in self.objects:
            return
        
        obj = self.objects[obj_id]
        
        # 移除该对象对其他对象的引用
        for ref_id in list(obj.references):
            if ref_id in self.objects:
                self.objects[ref_id].ref_count -= 1
        
        # 删除对象
        del self.objects[obj_id]
        
        # 从根集合移除
        self.root_set.discard(obj_id)
        
        # 更新统计
        self.stats['current_objects'] -= 1
        self.stats['current_bytes'] -= obj.size
        
        print_info(f"回收对象 {obj_id} ({format_size(obj.size)})")
    
    def display_stats(self):
        """显示垃圾回收器统计信息"""
        print_info("=" * 60)
        print_info(f"垃圾回收器状态 (模式: {self.mode})")
        print_info("=" * 60)
        
        print(f"\n当前状态:")
        print(f"  活动对象: {self.stats['current_objects']}")
        print(f"  占用内存: {format_size(self.stats['current_bytes'])}")
        print(f"  根对象数: {len(self.root_set)}")
        
        print(f"\n统计信息:")
        print(f"  总创建对象: {self.stats['total_objects_created']}")
        print(f"  总回收次数: {self.stats['total_collections']}")
        print(f"  总回收对象: {self.stats['total_objects_collected']}")
        print(f"  总回收内存: {format_size(self.stats['total_bytes_collected'])}")
        if self.stats['total_collections'] > 0:
            avg_time = self.stats['collection_time_ms'] / self.stats['total_collections']
            print(f"  平均回收时间: {avg_time:.2f}ms")
        
        # 按代统计（分代模式）
        if self.mode == 'generational':
            gen_stats = {0: 0, 1: 0, 2: 0}
            for obj in self.objects.values():
                gen_stats[obj.generation] += 1
            
            print(f"\n分代统计:")
            print(f"  新生代 (0): {gen_stats[0]} 个对象")
            print(f"  老年代 (1): {gen_stats[1]} 个对象")
            print(f"  永久代 (2): {gen_stats[2]} 个对象")
    
    def reset(self):
        """重置垃圾回收器"""
        self.objects.clear()
        self.root_set.clear()
        self.next_id = 1
        
        self.stats = {
            'total_objects_created': 0,
            'total_collections': 0,
            'total_objects_collected': 0,
            'total_bytes_collected': 0,
            'current_objects': 0,
            'current_bytes': 0,
            'collection_time_ms': 0
        }
        print_success("垃圾回收器已重置")
