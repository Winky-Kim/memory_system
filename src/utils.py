"""
工具函数模块
"""
from typing import List, Tuple
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)


def format_size(size: int) -> str:
    """格式化内存大小显示"""
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    size_float = float(size)
    
    while size_float >= 1024 and unit_index < len(units) - 1:
        size_float /= 1024
        unit_index += 1
    
    return f"{size_float:.2f} {units[unit_index]}"


def print_header(text: str):
    """打印标题"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_warning(text: str):
    """打印警告信息"""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")


def print_info(text: str):
    """打印信息"""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")


class MemoryBlock:
    """内存块类"""
    def __init__(self, start: int, size: int, is_free: bool = True, process_id: str = None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_id = process_id
        self.allocation_time = None
    
    @property
    def end(self) -> int:
        """返回内存块结束位置"""
        return self.start + self.size - 1
    
    def __repr__(self):
        status = "空闲" if self.is_free else f"已用(进程:{self.process_id})"
        return f"[{self.start}-{self.end}] {format_size(self.size)} {status}"


def visualize_memory(blocks: List[MemoryBlock], total_size: int, width: int = 60):
    """可视化内存布局"""
    print(f"\n{Fore.CYAN}内存布局：{Style.RESET_ALL}")
    
    # 绘制内存条
    bar = []
    for block in blocks:
        block_width = max(1, int(block.size / total_size * width))
        if block.is_free:
            bar.append(Fore.GREEN + '░' * block_width)
        else:
            bar.append(Fore.RED + '█' * block_width)
    
    print(''.join(bar) + Style.RESET_ALL)
    
    # 打印图例
    print(f"\n{Fore.GREEN}░{Style.RESET_ALL} 空闲  {Fore.RED}█{Style.RESET_ALL} 已占用")
    
    # 打印详细信息
    print(f"\n{Fore.CYAN}详细信息：{Style.RESET_ALL}")
    for i, block in enumerate(blocks):
        print(f"  块 {i}: {block}")
