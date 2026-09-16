import tkinter as tk
import time
import random
import sys

try:
    import pygame
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    



AUDIO_FILE = "" 


LYRICS = [
    (0.0, "And I've been waiting for the sunset"),
    (03.1, "Waiting on a sorry"),
    (04.6, "But you're never sorry, are you?"),
    (07.6, "No, you don't even care how"),
    (10.1, "Can you stand and watch"),
    (13.1, "while I'm"),

    (15.0, "Breaking all my bones"),
    (16.6, "Try'na hold you close"),
    (18.6, "Cut my heart right out my body"),
    (22.0, "Tearing off my skin"),
    (23.9, "Just to let you in"),
    (26.2, "Isn't it a bit unethical?"),
    (29.2, "Got me on my knees"),
    (31.0, "Have you any mercy"),
    (33.1, "Every time you hurt me, baby?"),
    (36.3, "Tell me have I not"), 
    (37.9, "Given you enough?"),
    (40.0, "If you ever loved me, let me go"),

]

BOX_W, BOX_H = 400, 250
FONT = (" UI", 40, "bold")
BG_COLOR = "#000000"
FG_COLOR = "#FFFFFF"

RISE_SPEED = 80         # pixels per second every box moves upward
SPAWN_INTERVAL_MIN = 1   # not used directly; spawning follows LYRICS times
SAFE_EDGE_MARGIN = 320    # min distance from left/right screen edges
BOTTOM_SPAWN_OFFSET = 150  # how far above the bottom edge new boxes spawn



class LyricBox:
    """A single fixed-size lyric popup that rises forever and stays visible."""
    def glitch_effect(self):
                glitch_colors = [
                    "#000000",  # Black
                    "#FF0000",  # Red
                    "#00FFFF",  # Cyan
                    "#FF00FF",  # Magenta
                    "#0000FF"   # Blue
                ]
    
                # Random color
                color = random.choice(glitch_colors)
    
                # Change text color
                self.label.config(bg=color)
    
                # Random text jitter
                if random.random() < 0.25:
                    self.label.config(
                        padx=random.randint(10, 25)
                    )
                else:
                    self.label.config(padx=15)

                # Repeat glitch effect
                self.win.after(
                    random.randint(50, 150),
                    self.glitch_effect
                )
                
    def __init__(self, master, text, x, y):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)   # no title bar, popup look
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        # Lock the geometry to the fixed box size — same as Start window
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        self.full_text = text

        self.label = tk.Label(
            self.win,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=BOX_W - 30,
            justify="center"
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=15)

        self.typewriter_index = 0
        self.typewriter()

        self.x = x
        self.y = float(y)
        
        #Start the glitch effect
        self.glitch_effect()
        
    def rise(self, dy):
        
        self.y -= dy
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50
    
    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[:self.typewriter_index])
            self.typewriter_index += 1
            # Faster typewriter speed
            self.win.after(70, self.typewriter)


class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lyric Float Controller")
        # The controller "Start" window uses the SAME fixed size/font
        # as every lyric box, per the same style.
        self.root.geometry(f"{BOX_W}x{BOX_H}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.start_btn = tk.Button(
            root, text="Start", font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            relief="flat", command=self.start
        )
        self.start_btn.pack(expand=True, fill="both", padx=15, pady=15)

        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None
        self.current_side = "left"  # Alternate between left and right

    def random_safe_x(self):
        """Alternate between left and right positions only."""
        # Calculate left and right positions - closer together
        center_x = self.screen_w // 2
        spacing = BOX_W + 60  # Small gap between boxes
        
        left_x = center_x - spacing
        right_x = center_x + 60
        
        # Alternate between left and right
        if self.current_side == "left":
            self.current_side = "right"
            return left_x
        else:
            self.current_side = "left"
            return right_x

    def start(self):
        self.start_btn.pack_forget()
        self.root.iconify()  
        self.start_time = time.time()
        self.last_frame_time = self.start_time

        if HAS_AUDIO and AUDIO_FILE:
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(AUDIO_FILE)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Audio failed to load: {e}")

        self.tick()

    def tick(self):
        now = time.time()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now

        # Spawn any lyric windows whose time has come
        while (self.next_lyric_idx < len(LYRICS) and
               LYRICS[self.next_lyric_idx][0] <= elapsed):
            t, text = LYRICS[self.next_lyric_idx]
            x = self.random_safe_x()
            y = self.screen_h - BOX_H - BOTTOM_SPAWN_OFFSET
            box = LyricBox(self.root, text, x, y)
            self.boxes.append(box)
            self.next_lyric_idx += 1

        # Continuously rise ALL existing boxes upward, every frame
        dy = RISE_SPEED * dt
        for box in self.boxes:
            box.rise(dy)

        # Boxes stay visible permanently; we just stop tracking ones that
        # have scrolled fully off the top of the screen (saves memory),
        # but we never fade or destroy them early.
        still_visible = []
        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)
        self.boxes = still_visible

        # Keep looping as long as there are lyrics left to show or
        # boxes still on screen
        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick)  # ~60fps


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
