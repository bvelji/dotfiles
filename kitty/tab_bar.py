import datetime
import subprocess
import re
from kitty.fast_data_types import ( 
    Screen, add_timer, get_options
)
from kitty.tab_bar import (
    DrawData, ExtraData, TabBarData, 
    as_rgb, draw_title
)

def get_stats():
    try:
        # 1. Get Load Average (CPU)
        # Returns something like "{ 1.25 1.10 1.05 }"
        load_out = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode("utf-8")
        cpu_load = load_out.split()[1] # Grab the 1-minute average
        
        # 2. Get Memory Pressure
        # 'memory_pressure' is more accurate for macOS than raw RAM usage
        mem_out = subprocess.check_output(["memory_pressure"]).decode("utf-8")
        # Extract percentage from output like "System-wide memory free percentage: 25%"
        match = re.search(r"(\d+)%", mem_out)
        mem_pressure = 100 - int(match.group(1)) if match else "--"
        
        return f"CPU: {cpu_load} | RAM: {mem_pressure}%"
    except Exception:
        return "Stats: N/A"

def draw_tab(
    draw_data: DrawData, screen: Screen, tab: TabBarData,
    before: int, max_title_length: int, index: int, is_last: bool,
    extra_data: ExtraData
) -> int:
    end = draw_title(draw_data, screen, tab, index)
    
    if is_last:
        stats = get_stats()
        time_str = datetime.datetime.now().strftime("%H:%M")
        right_text = f" {stats} | {time_str} "
        
        draw_spaces = screen.columns - screen.cursor.x - len(right_text)
        if draw_spaces > 0:
            screen.draw(" " * draw_spaces)
            
        screen.cursor.fg = as_rgb(0x888888) 
        screen.draw(right_text)
        
    return end

def refresh_callback(timer_id):
    from kitty.fast_data_types import redraw_tab_bar
    redraw_tab_bar()  # Trigger a redraw of the tab bar

add_timer(refresh_callback, 2.0, True)  # Refresh tab bar every 2 seconds
