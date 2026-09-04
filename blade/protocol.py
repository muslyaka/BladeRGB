import time

VID = 0x0416
PID = 0xC345
USAGE_PAGE = 0xFF1B
USAGE = 0x91
INTERFACE = 2

REPORT_SIZE = 64
REPORT_COUNT = 8
FRAME_SIZE = 512


def make_manual_mode_packet(brightness: int = 4, speed: int = 3) -> bytearray:
    brightness = max(0, min(4, int(brightness)))
    speed = max(1, min(5, int(speed)))

    packet = bytearray([
        0x01,0x07,0x00,0x00,0x00,0x00,0x0A,0x04,
        0x03,0xFF,0x00,0x00,0xFF,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    ])
    packet[7] = brightness
    packet[8] = speed
    return packet


def build_frame():
    frame = bytearray(FRAME_SIZE)
    for page in range(REPORT_COUNT):
        s = page * REPORT_SIZE
        frame[s+0] = 0x01
        frame[s+1] = 0x0F
        frame[s+2] = 0x00
        frame[s+3] = 0x00
        frame[s+4] = page
        frame[s+5] = 0x12 if page == 7 else 0x36
        frame[s+6] = 0x00
        frame[s+7] = 0x00
    return frame


def write_frame(device, frame, inter_report_delay=0.001):
    if len(frame) != FRAME_SIZE:
        raise ValueError(f"frame={len(frame)}, ожидалось {FRAME_SIZE}")

    total = 0
    for page in range(REPORT_COUNT):
        s = page * REPORT_SIZE
        written = device.write(frame[s:s+REPORT_SIZE])
        total += int(written or 0)
        if inter_report_delay and page < REPORT_COUNT-1:
            time.sleep(inter_report_delay)
    return total
