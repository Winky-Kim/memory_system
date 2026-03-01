"""
内存管理模拟器主程序
演示所有功能模块
"""
import time
from colorama import Fore, Style
from src.allocator import MemoryAllocator
from src.virtual_memory import VirtualMemoryManager
from src.leak_detector import MemoryLeakDetector
from src.memory_pool import MemoryPool, MultiSizeMemoryPool
from src.garbage_collector import GarbageCollector
from src.utils import print_header, print_info, print_success


def demo_allocator():
    """演示内存分配器"""
    print_header("1. 动态内存分配算法演示")
    
    algorithms = ['first_fit', 'best_fit', 'worst_fit', 'next_fit']
    
    for algorithm in algorithms:
        print(f"\n{Fore.CYAN}{'─' * 60}")
        print(f"算法: {algorithm.upper()}")
        print(f"{'─' * 60}{Style.RESET_ALL}\n")
        
        allocator = MemoryAllocator(total_size=1024, algorithm=algorithm)
        
        # 模拟内存分配
        ptr1 = allocator.allocate(100, "P1")
        ptr2 = allocator.allocate(200, "P2")
        ptr3 = allocator.allocate(150, "P3")
        ptr4 = allocator.allocate(300, "P4")
        
        # 释放一些内存
        allocator.free(ptr2)
        allocator.free(ptr4)
        
        # 再次分配
        ptr5 = allocator.allocate(180, "P5")
        ptr6 = allocator.allocate(50, "P6")
        
        # 显示状态
        allocator.display_memory()
        
        time.sleep(1)
    
    input(f"\n{Fore.YELLOW}按回车继续...{Style.RESET_ALL}")


def demo_virtual_memory():
    """演示虚拟内存管理"""
    print_header("2. 虚拟内存管理和页面置换算法演示")
    
    algorithms = ['fifo', 'lru', 'lfu', 'clock']
    
    for algorithm in algorithms:
        print(f"\n{Fore.CYAN}{'─' * 60}")
        print(f"页面置换算法: {algorithm.upper()}")
        print(f"{'─' * 60}{Style.RESET_ALL}\n")
        
        vm = VirtualMemoryManager(page_size=4096, num_frames=4, algorithm=algorithm)
        
        # 模拟页面访问序列
        page_sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        
        print_info(f"页面访问序列: {page_sequence}\n")
        
        for page_num in page_sequence:
            vm.access_page(page_num)
            time.sleep(0.1)
        
        print()
        vm.display_status()
        
        time.sleep(1)
    
    # 地址转换演示
    print(f"\n{Fore.CYAN}{'─' * 60}")
    print(f"地址转换演示")
    print(f"{'─' * 60}{Style.RESET_ALL}\n")
    
    vm = VirtualMemoryManager(page_size=4096, num_frames=10, algorithm='lru')
    
    virtual_addresses = [0x0000, 0x1000, 0x2500, 0x3ABC]
    for vaddr in virtual_addresses:
        vm.translate_address(vaddr)
    
    input(f"\n{Fore.YELLOW}按回车继续...{Style.RESET_ALL}")


def demo_leak_detector():
    """演示内存泄漏检测"""
    print_header("3. 内存泄漏检测演示")
    
    detector = MemoryLeakDetector(enable_stack_trace=True)
    
    # 正常分配和释放
    print_info("正常分配和释放:")
    ptr1 = detector.allocate(100, "P1")
    ptr2 = detector.allocate(200, "P2")
    detector.free(ptr1)
    detector.free(ptr2)
    
    print()
    
    # 模拟内存泄漏
    print_info("模拟内存泄漏:")
    detector.simulate_leak(256, "P3")
    detector.simulate_leak(512, "P4")
    detector.simulate_leak(128, "P5")
    
    print()
    detector.display_status()
    
    # 检查泄漏
    print()
    detector.print_leak_report()
    
    input(f"\n{Fore.YELLOW}按回车继续...{Style.RESET_ALL}")


def demo_memory_pool():
    """演示内存池管理"""
    print_header("4. 内存池管理演示")
    
    # 单一尺寸内存池
    print(f"\n{Fore.CYAN}{'─' * 60}")
    print(f"单一尺寸内存池")
    print(f"{'─' * 60}{Style.RESET_ALL}\n")
    
    pool = MemoryPool(block_size=64, num_blocks=10)
    
    # 分配一些块
    blocks = []
    for i in range(7):
        block = pool.allocate(f"P{i+1}")
        if block is not None:
            blocks.append(block)
    
    print()
    
    # 释放一些块
    pool.free(blocks[1])
    pool.free(blocks[3])
    pool.free(blocks[5])
    
    print()
    pool.display_stats()
    
    # 多尺寸内存池
    print(f"\n{Fore.CYAN}{'─' * 60}")
    print(f"多尺寸内存池")
    print(f"{'─' * 60}{Style.RESET_ALL}\n")
    
    multi_pool = MultiSizeMemoryPool()
    
    # 分配不同大小的内存
    sizes = [32, 150, 800, 60, 500, 200]
    ptrs = []
    for i, size in enumerate(sizes):
        ptr = multi_pool.allocate(size, f"P{i+1}")
        if ptr:
            ptrs.append(ptr)
    
    print()
    
    # 释放一些内存
    if len(ptrs) >= 3:
        multi_pool.free(ptrs[1])
        multi_pool.free(ptrs[3])
    
    print()
    multi_pool.display_stats()
    
    input(f"\n{Fore.YELLOW}按回车继续...{Style.RESET_ALL}")


def demo_garbage_collector():
    """演示垃圾回收"""
    print_header("5. 垃圾回收机制演示")
    
    modes = ['mark_sweep', 'ref_count', 'generational']
    
    for mode in modes:
        print(f"\n{Fore.CYAN}{'─' * 60}")
        print(f"回收模式: {mode.upper()}")
        print(f"{'─' * 60}{Style.RESET_ALL}\n")
        
        gc = GarbageCollector(mode=mode)
        
        # 创建对象图
        obj1 = gc.create_object(100, is_root=True)
        obj2 = gc.create_object(200, is_root=True)
        obj3 = gc.create_object(150)
        obj4 = gc.create_object(300)
        obj5 = gc.create_object(250)
        
        # 建立引用关系
        gc.add_reference(obj1, obj3)
        gc.add_reference(obj2, obj4)
        gc.add_reference(obj3, obj5)
        
        print()
        print_info("对象图:")
        print(f"  obj1 (根) -> obj3 -> obj5")
        print(f"  obj2 (根) -> obj4")
        
        print()
        gc.display_stats()
        
        # 移除一些引用，创造垃圾
        print()
        print_info("移除 obj2 -> obj4 引用，obj4 变成垃圾")
        gc.remove_reference(obj2, obj4)
        
        # 执行垃圾回收
        print()
        gc.collect()
        
        print()
        gc.display_stats()
        
        time.sleep(1)
    
    input(f"\n{Fore.YELLOW}按回车继续...{Style.RESET_ALL}")


def demo_comprehensive():
    """综合演示"""
    print_header("6. 综合场景演示")
    
    print_info("模拟一个复杂的内存管理场景...\n")
    
    # 创建各个组件
    allocator = MemoryAllocator(total_size=4096, algorithm='best_fit')
    vm = VirtualMemoryManager(page_size=1024, num_frames=8, algorithm='lru')
    detector = MemoryLeakDetector()
    pool = MultiSizeMemoryPool()
    gc = GarbageCollector(mode='generational')
    
    # 场景1：动态分配
    print(f"\n{Fore.CYAN}场景1: 动态内存分配{Style.RESET_ALL}")
    ptrs = []
    for i in range(5):
        size = (i + 1) * 100
        ptr = allocator.allocate(size, f"Process-{i}")
        ptrs.append(ptr)
    
    # 场景2：虚拟内存访问
    print(f"\n{Fore.CYAN}场景2: 虚拟内存访问{Style.RESET_ALL}")
    for page in [0, 1, 2, 3, 0, 4, 1, 5, 2]:
        vm.access_page(page)
    
    # 场景3：内存池使用
    print(f"\n{Fore.CYAN}场景3: 内存池分配{Style.RESET_ALL}")
    pool_ptrs = []
    for i in range(3):
        ptr = pool.allocate(128, f"Pool-Process-{i}")
        if ptr:
            pool_ptrs.append(ptr)
    
    # 场景4：创建对象和垃圾回收
    print(f"\n{Fore.CYAN}场景4: 对象创建和垃圾回收{Style.RESET_ALL}")
    obj1 = gc.create_object(200, is_root=True)
    obj2 = gc.create_object(300)
    obj3 = gc.create_object(150)
    gc.add_reference(obj1, obj2)
    gc.add_reference(obj1, obj3)
    
    # 显示所有组件状态
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}最终状态汇总:{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}内存分配器:{Style.RESET_ALL}")
    print(f"  利用率: {allocator.stats['current_allocated'] / allocator.total_size * 100:.1f}%")
    print(f"  碎片率: {allocator.get_fragmentation():.1f}%")
    
    print(f"\n{Fore.GREEN}虚拟内存:{Style.RESET_ALL}")
    print(f"  命中率: {vm.get_hit_rate():.1f}%")
    print(f"  页面置换: {vm.stats['page_replacements']} 次")
    
    print(f"\n{Fore.GREEN}垃圾回收:{Style.RESET_ALL}")
    print(f"  活动对象: {gc.stats['current_objects']}")
    print(f"  占用内存: {gc.stats['current_bytes']} 字节")
    
    print_success("\n综合演示完成！")


def main():
    """主函数"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{'内存管理模拟器':^60}")
    print(f"{'=' * 60}{Style.RESET_ALL}\n")
    
    print("本模拟器演示以下功能：")
    print("  1. 动态内存分配算法（首次适应、最佳适应、最坏适应、下次适应）")
    print("  2. 虚拟内存管理和页面置换算法（FIFO、LRU、LFU、Clock）")
    print("  3. 内存泄漏检测")
    print("  4. 内存池管理")
    print("  5. 垃圾回收机制（标记-清除、引用计数、分代回收）")
    print("  6. 综合场景演示")
    
    while True:
        print(f"\n{Fore.YELLOW}{'─' * 60}{Style.RESET_ALL}")
        print("\n请选择演示模块：")
        print("  [1] 动态内存分配算法")
        print("  [2] 虚拟内存管理和页面置换")
        print("  [3] 内存泄漏检测")
        print("  [4] 内存池管理")
        print("  [5] 垃圾回收机制")
        print("  [6] 综合场景演示")
        print("  [7] 全部演示")
        print("  [0] 退出")
        
        choice = input(f"\n{Fore.CYAN}请输入选项 [0-7]: {Style.RESET_ALL}").strip()
        
        if choice == '0':
            print_success("\n感谢使用内存管理模拟器！")
            break
        elif choice == '1':
            demo_allocator()
        elif choice == '2':
            demo_virtual_memory()
        elif choice == '3':
            demo_leak_detector()
        elif choice == '4':
            demo_memory_pool()
        elif choice == '5':
            demo_garbage_collector()
        elif choice == '6':
            demo_comprehensive()
        elif choice == '7':
            demo_allocator()
            demo_virtual_memory()
            demo_leak_detector()
            demo_memory_pool()
            demo_garbage_collector()
            demo_comprehensive()
        else:
            print(f"{Fore.RED}无效的选项，请重新输入{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
