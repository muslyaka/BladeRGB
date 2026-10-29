"""Hardware-free regression checks for HID output and Blackout behavior."""

from blade.layout import KEY_OFFSETS
from blade.protocol import REPORT_COUNT, REPORT_SIZE, build_frame, write_frame
from engine.renderer import Renderer


class FakeHid:
    def __init__(self, result=REPORT_SIZE):
        self.result = result
        self.calls = 0

    def write(self, data):
        assert len(data) == REPORT_SIZE
        self.calls += 1
        return self.result


class FakeKeyboard:
    connected = True

    def __init__(self):
        self.sent_black = False
        self.manual_calls = 0

    def enable_manual_mode(self):
        self.manual_calls += 1

    def blackout(self):
        self.sent_black = True


def test_reports():
    fake = FakeHid()
    assert write_frame(fake, build_frame(), inter_report_delay=0) == REPORT_COUNT * REPORT_SIZE
    assert fake.calls == REPORT_COUNT

    for count in (0, REPORT_SIZE - 1):
        fake = FakeHid(count)
        try:
            write_frame(fake, build_frame(), inter_report_delay=0)
        except OSError as exc:
            assert "HID" in str(exc)
            assert fake.calls == 1
        else:
            raise AssertionError("A partial HID write must raise OSError")


def test_blackout():
    device = FakeKeyboard()
    renderer = Renderer(device)
    renderer.running = True
    renderer.last_colors = {k: (255, 100, 20) for k in KEY_OFFSETS}
    renderer.blackout()
    assert not renderer.running
    assert renderer.actual_fps == 0
    assert device.sent_black
    assert device.manual_calls == 1
    assert all(rgb == (0, 0, 0) for rgb in renderer.snapshot().values())


if __name__ == "__main__":
    test_reports()
    test_blackout()
    print("Runtime regression tests: OK")
