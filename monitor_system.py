import psutil
import argparse
import json
import csv
import time

CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 75
DISK_THRESHOLD = 90

def get_cpu_usage():
    return psutil.cpu_percent(interval=0)  # Immediate CPU usage

def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        "Total": memory.total,
        "Used": memory.used,
        "Free": memory.available,
        "Percent": memory.percent
    }
def get_disk_usage():
    disk_usage = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage[partition.mountpoint] = {
                "Total": usage.total,
                "Used": usage.used,
                "Free": usage.free,
                "Percent": usage.percent
            }
        except PermissionError:
            continue
    return disk_usage
def get_top_cpu_processes(n=5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:n]
    return processes

def check_thresholds(cpu_usage, memory_usage, disk_usage):
    warnings = []
    if cpu_usage > CPU_THRESHOLD:
        warnings.append(f"WARNING: CPU usage is high! ({cpu_usage}%)")
    if memory_usage["Percent"] > MEMORY_THRESHOLD:
        warnings.append(f"WARNING: Memory usage is high! ({memory_usage['Percent']}%)")
    for mountpoint, usage in disk_usage.items():
        if usage["Percent"] > DISK_THRESHOLD:
            warnings.append(f"WARNING: Disk usage is high on {mountpoint}! ({usage['Percent']}%)")
    return warnings

def monitor_system(interval, output_format, output_file):
    while True:
        cpu_usage = get_cpu_usage()
        memory_usage = get_memory_usage()
        disk_usage = get_disk_usage()
        top_processes = get_top_cpu_processes()
        warnings = check_thresholds(cpu_usage, memory_usage, disk_usage)
        data = {
            "CPU Usage": cpu_usage,
            "Memory Usage": memory_usage,
            "Disk Usage": disk_usage,
            "Top Processes": top_processes,
            "Warnings": warnings
        }
        if output_format == "json":
            formatted_output = json.dumps(data, indent=4)
        elif output_format == "csv":
            csv_data = [
                ["Category", "Details"],
                ["CPU Usage", f"{cpu_usage}%"],
                ["Memory Usage", f"Total: {memory_usage['Total']} Bytes, Used: {memory_usage['Used']} Bytes, Free: {memory_usage['Free']} Bytes, Percent: {memory_usage['Percent']}%"]
            ]
            for mountpoint, usage in disk_usage.items():
                csv_data.append(["Disk Usage", f"{mountpoint}: Total: {usage['Total']} Bytes, Used: {usage['Used']} Bytes, Free: {usage['Free']} Bytes, Percent: {usage['Percent']}%"])
            for proc in top_processes:
                csv_data.append(["Top Processes", f"PID: {proc['pid']}, Name: {proc['name']}, CPU Usage: {proc['cpu_percent']}%"])
            csv_data.append(["Warnings", "; ".join(warnings)])
            formatted_output = csv_data
        else:
            formatted_output = []
            formatted_output.append(f"CPU Usage: {cpu_usage}%")
            formatted_output.append("Memory Usage:")
            formatted_output.append(f"  Total: {memory_usage['Total']} Bytes")
            formatted_output.append(f"  Used: {memory_usage['Used']} Bytes")
            formatted_output.append(f"  Free: {memory_usage['Free']} Bytes")
            formatted_output.append(f"  Usage: {memory_usage['Percent']}%")
            formatted_output.append("Disk Usage:")
            for mountpoint, usage in disk_usage.items():
                formatted_output.append(f"  Mountpoint: {mountpoint}")
                formatted_output.append(f"    Total: {usage['Total']} Bytes")
                formatted_output.append(f"    Used: {usage['Used']} Bytes")
                formatted_output.append(f"    Free: {usage['Free']} Bytes")
                formatted_output.append(f"    Usage: {usage['Percent']}%")
            formatted_output.append("Top 5 CPU-Consuming Processes:")
            for proc in top_processes:
                formatted_output.append(f"  PID: {proc['pid']}, Name: {proc['name']}, CPU Usage: {proc['cpu_percent']}%")
            formatted_output.append("Warnings:")
            formatted_output.extend(warnings)
            formatted_output = "\n".join(formatted_output)
        if output_format == "csv":
            print("Output saved to CSV file")
        else:
            print(formatted_output)
        if output_file:
            if output_format == "csv":
                with open(output_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(formatted_output)
            else:
                with open(output_file, "w") as f:
                    f.write(formatted_output)
        if warnings:
            for warning in warnings:
                print(warning)
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="System Monitoring Script")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in seconds")
    parser.add_argument("--format", type=str, choices=["text", "json", "csv"], default="text", help="Output format")
    parser.add_argument("--output", type=str, help="File to save the output")
    args = parser.parse_args()
    monitor_system(args.interval, args.format, args.output)
