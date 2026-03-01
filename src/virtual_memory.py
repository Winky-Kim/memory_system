"""
虚拟内存管理器
实现页面管理和多种页面置换算法：FIFO、LRU、LFU、Clock
"""
from typing import Optional, List, Dict
from collections import deque, OrderedDict
from datetime import datetime
from src.utils import print_success, print_error, print_info, print_warning


class Page:
    """页面类"""
    def __init__(self, page_number: int):
        self.page_number = page_number
        self.frame_number: Optional[int] = None
        self.reference_count = 0
        self.last_access_time = datetime.now()
        self.load_time = None
        self.reference_bit = False  # 用于Clock算法
    
    def __repr__(self):
        return f"Page({self.page_number}, Frame={self.frame_number})"


class VirtualMemoryManager:
    """虚拟内存管理器"""
    
    def __init__(self, page_size: int = 4096, num_frames: int = 10, algorithm: str = 'lru'):
        """
        初始化虚拟内存管理器
        
        Args:
            page_size: 页面大小（字节）
            num_frames: 物理内存帧数
            algorithm: 页面置换算法 ('fifo', 'lru', 'lfu', 'clock')
        """
        self.page_size = page_size
        self.num_frames = num_frames
        self.algorithm = algorithm
        
        # 页表：页号 -> Page对象
        self.page_table: Dict[int, Page] = {}
        
        # 物理内存帧：帧号 -> 页号
        self.frames: List[Optional[int]] = [None] * num_frames
        
        # 算法特定的数据结构
        self.fifo_queue = deque()  # FIFO队列
        self.lru_access = OrderedDict()  # LRU访问顺序
        self.clock_hand = 0  # Clock算法的指针
        
        # 统计信息
        self.stats = {
            'page_accesses': 0,
            'page_faults': 0,
            'page_replacements': 0,
            'total_pages_loaded': 0
        }
    
    def access_page(self, page_number: int) -> bool:
        """
        访问页面
        
        Args:
            page_number: 要访问的页号
        
        Returns:
            True表示页面命中，False表示页面缺失
        """
        self.stats['page_accesses'] += 1
        
        # 检查页面是否在内存中
        if page_number in self.page_table and self.page_table[page_number].frame_number is not None:
            # 页面命中
            page = self.page_table[page_number]
            page.reference_count += 1
            page.last_access_time = datetime.now()
            page.reference_bit = True
            
            # 更新LRU访问顺序
            if self.algorithm == 'lru':
                self.lru_access.move_to_end(page_number)
            
            print_success(f"页面 {page_number} 命中 (帧 {page.frame_number})")
            return True
        else:
            # 页面缺失
            self.stats['page_faults'] += 1
            print_warning(f"页面 {page_number} 缺失")
            self._handle_page_fault(page_number)
            return False
    
    def _handle_page_fault(self, page_number: int):
        """处理页面缺失"""
        # 查找空闲帧
        free_frame = self._find_free_frame()
        
        if free_frame is not None:
            # 有空闲帧，直接加载
            self._load_page(page_number, free_frame)
        else:
            # 没有空闲帧，需要置换
            self.stats['page_replacements'] += 1
            victim_frame = self._select_victim()
            self._replace_page(page_number, victim_frame)
    
    def _find_free_frame(self) -> Optional[int]:
        """查找空闲帧"""
        for i, frame in enumerate(self.frames):
            if frame is None:
                return i
        return None
    
    def _load_page(self, page_number: int, frame_number: int):
        """加载页面到指定帧"""
        # 创建或更新页面
        if page_number not in self.page_table:
            page = Page(page_number)
            self.page_table[page_number] = page
        else:
            page = self.page_table[page_number]
        
        page.frame_number = frame_number
        page.load_time = datetime.now()
        page.last_access_time = datetime.now()
        page.reference_count = 1
        page.reference_bit = True
        
        # 更新帧表
        self.frames[frame_number] = page_number
        
        # 更新算法特定的数据结构
        if self.algorithm == 'fifo':
            self.fifo_queue.append(page_number)
        elif self.algorithm == 'lru':
            self.lru_access[page_number] = True
        
        self.stats['total_pages_loaded'] += 1
        print_success(f"页面 {page_number} 加载到帧 {frame_number}")
    
    def _select_victim(self) -> int:
        """根据算法选择要置换的页面帧"""
        if self.algorithm == 'fifo':
            return self._fifo_victim()
        elif self.algorithm == 'lru':
            return self._lru_victim()
        elif self.algorithm == 'lfu':
            return self._lfu_victim()
        elif self.algorithm == 'clock':
            return self._clock_victim()
        else:
            return 0
    
    def _fifo_victim(self) -> int:
        """FIFO算法：选择最先进入的页面"""
        victim_page = self.fifo_queue.popleft()
        page = self.page_table[victim_page]
        return page.frame_number
    
    def _lru_victim(self) -> int:
        """LRU算法：选择最久未使用的页面"""
        victim_page = next(iter(self.lru_access))
        del self.lru_access[victim_page]
        page = self.page_table[victim_page]
        return page.frame_number
    
    def _lfu_victim(self) -> int:
        """LFU算法：选择使用频率最低的页面"""
        min_count = float('inf')
        victim_frame = 0
        
        for frame_num, page_num in enumerate(self.frames):
            if page_num is not None:
                page = self.page_table[page_num]
                if page.reference_count < min_count:
                    min_count = page.reference_count
                    victim_frame = frame_num
        
        return victim_frame
    
    def _clock_victim(self) -> int:
        """Clock算法（二次机会算法）"""
        while True:
            page_num = self.frames[self.clock_hand]
            page = self.page_table[page_num]
            
            if not page.reference_bit:
                # 找到victim
                victim_frame = self.clock_hand
                self.clock_hand = (self.clock_hand + 1) % self.num_frames
                return victim_frame
            else:
                # 给予第二次机会
                page.reference_bit = False
                self.clock_hand = (self.clock_hand + 1) % self.num_frames
    
    def _replace_page(self, new_page_number: int, victim_frame: int):
        """置换页面"""
        # 获取被置换的页面
        old_page_number = self.frames[victim_frame]
        old_page = self.page_table[old_page_number]
        
        print_info(f"置换: 页面 {old_page_number} (帧 {victim_frame}) -> 页面 {new_page_number}")
        
        # 从帧中移除旧页面
        old_page.frame_number = None
        
        # 加载新页面
        self._load_page(new_page_number, victim_frame)
    
    def translate_address(self, virtual_address: int) -> Optional[int]:
        """
        将虚拟地址转换为物理地址
        
        Args:
            virtual_address: 虚拟地址
        
        Returns:
            物理地址，如果页面不在内存中返回None
        """
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        # 访问页面（可能触发页面置换）
        self.access_page(page_number)
        
        # 获取物理地址
        if page_number in self.page_table:
            page = self.page_table[page_number]
            if page.frame_number is not None:
                physical_address = page.frame_number * self.page_size + offset
                print_info(f"地址转换: 虚拟地址 0x{virtual_address:08x} -> "
                          f"物理地址 0x{physical_address:08x} "
                          f"(页 {page_number}, 帧 {page.frame_number}, 偏移 {offset})")
                return physical_address
        
        return None
    
    def display_status(self):
        """显示虚拟内存状态"""
        print_info("=" * 60)
        print_info(f"虚拟内存管理器状态 (算法: {self.algorithm})")
        print_info("=" * 60)
        
        # 显示页表
        print(f"\n页表 (共 {len(self.page_table)} 个页面):")
        for page_num in sorted(self.page_table.keys()):
            page = self.page_table[page_num]
            if page.frame_number is not None:
                print(f"  页 {page_num:3d} -> 帧 {page.frame_number:2d} | "
                      f"引用次数: {page.reference_count:3d} | "
                      f"引用位: {int(page.reference_bit)}")
        
        # 显示物理内存帧
        print(f"\n物理内存帧 (共 {self.num_frames} 个帧):")
        for i, page_num in enumerate(self.frames):
            if page_num is not None:
                print(f"  帧 {i:2d} <- 页 {page_num:3d}")
            else:
                print(f"  帧 {i:2d} <- [空闲]")
        
        # 显示统计信息
        print(f"\n统计信息:")
        print(f"  页面访问次数: {self.stats['page_accesses']}")
        print(f"  页面缺失次数: {self.stats['page_faults']}")
        print(f"  页面置换次数: {self.stats['page_replacements']}")
        print(f"  已加载页面数: {self.stats['total_pages_loaded']}")
        
        if self.stats['page_accesses'] > 0:
            hit_rate = (self.stats['page_accesses'] - self.stats['page_faults']) / self.stats['page_accesses'] * 100
            miss_rate = self.stats['page_faults'] / self.stats['page_accesses'] * 100
            print(f"  命中率: {hit_rate:.2f}%")
            print(f"  缺失率: {miss_rate:.2f}%")
    
    def get_hit_rate(self) -> float:
        """获取页面命中率"""
        if self.stats['page_accesses'] == 0:
            return 0.0
        return (self.stats['page_accesses'] - self.stats['page_faults']) / self.stats['page_accesses'] * 100
    
    def reset(self):
        """重置虚拟内存管理器"""
        self.page_table.clear()
        self.frames = [None] * self.num_frames
        self.fifo_queue.clear()
        self.lru_access.clear()
        self.clock_hand = 0
        
        self.stats = {
            'page_accesses': 0,
            'page_faults': 0,
            'page_replacements': 0,
            'total_pages_loaded': 0
        }
        print_success("虚拟内存管理器已重置")
