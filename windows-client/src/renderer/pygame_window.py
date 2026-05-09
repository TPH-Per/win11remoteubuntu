import pygame
import queue
import time
import numpy as np

class PygameWindow:
    def __init__(self, initial_w: int, initial_h: int, kvm_manager, stats):
        self.w = initial_w
        self.h = initial_h
        self._kvm = kvm_manager
        self._stats = stats
        self._frame_queue = queue.Queue(maxsize=2)
        self._last_frame = None
        self._running = False
        self._overlay_until = 0

    def start(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self.w, self.h),
            pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("ThunderKVM — SCROLL LOCK to toggle")
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont(None, 24)
        self._running = True
        
        def on_toggle():
            self._overlay_until = time.monotonic() + 1.5
        self._kvm.on_toggle = on_toggle

    def push_frame(self, frame_rgb: np.ndarray) -> None:
        try:
            self._frame_queue.put_nowait(frame_rgb)
        except queue.Full:
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                pass
            self._frame_queue.put_nowait(frame_rgb)

    def run_event_loop(self) -> None:
        while self._running:
            self._handle_events()
            self._render()
            self._clock.tick(60)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if self._kvm.handle_key(event):
                    continue
                mods = pygame.key.get_mods()
                if event.key == pygame.K_q and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_ALT):
                    self._running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            elif event.type == pygame.VIDEORESIZE:
                self.w, self.h = event.w, event.h
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL):
                pass # Handled internally by input capture

    def _draw_overlay(self):
        now = time.monotonic()
        if now < getattr(self, '_overlay_until', 0):
            state_str = "REMOTE" if self._kvm.state.name == "FOCUSED_REMOTE" else "LOCAL"
            if state_str == "REMOTE":
                color = (200, 0, 0)
                text = "● REMOTE"
            else:
                color = (0, 200, 0)
                text = "● LOCAL"
            
            overlay = pygame.Surface((120, 24))
            overlay.fill(color)
            text_surf = self._font.render(text, True, (255, 255, 255))
            overlay.blit(text_surf, (10, 2))
            w, _ = self._screen.get_size()
            self._screen.blit(overlay, (w - 130, 10))

    def _render(self) -> None:
        try:
            frame = self._frame_queue.get_nowait()
            self._last_frame = frame
        except queue.Empty:
            frame = self._last_frame
        
        if frame is not None:
            surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            scaled = pygame.transform.scale(surface, self._screen.get_size())
            self._screen.blit(scaled, (0, 0))
            
        self._draw_overlay()
        pygame.display.flip()
