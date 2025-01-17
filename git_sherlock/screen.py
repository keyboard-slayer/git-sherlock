import sys
import tty
import shutil
import traceback
from typing import Callable, Optional


class Screen:
    def __init__(self):
        tty.setcbreak(sys.stdin.fileno())

        self.size = shutil.get_terminal_size()
        self.pos = (1, 1)
        self.offset = 0
        self.quit = self.default_quit
        self.buffer = []
        self.need_update = True
        self.previous_pos = {}
        self.bindings = {}

        self.clearscr()
        self.reset_bindings()

    def reset_bindings(self):
        self.bindings = {
            "j": lambda: self.move_cursor((self.pos[0], self.pos[1] + 1)),
            "k": lambda: self.move_cursor((self.pos[0], self.pos[1] - 1)),
            "l": lambda: self.move_cursor((self.pos[0] + 1, self.pos[1])),
            "h": lambda: self.move_cursor((self.pos[0] - 1, self.pos[1])),
            "\n": lambda: None
            if self.buffer[self.pos[1] + self.offset - 1][1] is None
            else self.buffer[self.pos[1] + self.offset - 1][1](),
            "q": lambda: self.quit(),
        }

    def backup_pos(self, name: str):
        if name not in self.previous_pos:
            self.previous_pos[name] = (self.offset, self.pos)

    def restore_pos(self, name: str):
        if name in self.previous_pos:
            self.offset, self.pos = self.previous_pos.pop(name)

    def add_line(self, s: str, callback: Optional[Callable] = None):
        self.buffer.append((s, callback))
        self.need_update = True

    def update(self):
        delta = self.size.lines - self.pos[1]

        if delta <= 10 and len(self.buffer) > self.size.lines + self.offset + delta:
            self.need_update = True
            self.pos = (self.pos[0], self.pos[1] - 1)
            if delta > 0:
                self.offset += 1

        if self.pos[1] <= 11 and self.offset > 0:
            self.need_update = True
            self.pos = (self.pos[0], self.pos[1] + 1)
            self.offset -= 1

        if self.need_update:
            self.need_update = False
            self.draw()

    def draw(self):
        old_pos = self.pos
        buffer = self.buffer[self.offset : self.offset + self.size.lines - 1]
        self.clearscr()
        for line, _ in buffer:
            print(line)

        self.pos = old_pos
        print(f"\033[{self.pos[1]};{self.pos[0]}H", end="")
        sys.stdout.flush()

    def move_cursor(self, pos: tuple[int, int]):
        self.pos = pos

        if self.pos[0] > self.size.columns:
            self.pos = (self.size.columns, self.pos[1])

        if self.pos[0] < 1:
            self.pos = (1, self.pos[1])

        if self.pos[1] < 1:
            self.pos = (self.pos[0], 1)

        print(f"\033[{self.pos[1]};{self.pos[0]}H", end="")
        sys.stdout.flush()

    def clearscr(self):
        print("\033[2J")
        print("\033[H", end="")
        self.pos = (1, 1)

    def clear(self):
        self.offset = 0
        self.buffer = []
        self.clearscr()

    def default_quit(self):
        self.clear()
        exit(1)

    def define_quit_action(self, callback: Callable):
        self.quit = callback

    def getch(self) -> str:
        return sys.stdin.read(1)

    def mainloop(self):
        try:
            while True:
                self.update()
                key = self.getch()
                if key in self.bindings:
                    self.bindings[key]()

        except Exception:
            print(traceback.format_exc())
