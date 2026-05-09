import pygame
import queue
import threading
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

    def start(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self.w, self.h),
            pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont(None, 36)
        self._running = True

    def push_frame(self, frame_rgb: np.ndarray) -> None:
        """Called from decoder thread. Non-blocking: drop if queue full."""
        try:
            self._frame_queue.put_nowait(frame_rgb)
        except queue.Full:
            # Drop oldest, push newest
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                pass
            self._frame_queue.put_nowait(frame_rgb)

    def run_event_loop(self) -> None:
        """Blocks. Call from main thread."""
        while self._running:
            self._handle_events()
            self._render()
            self._clock.tick(1000)  # 1000Hz event loop, render only when needed

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                # Quit hotkey
                mods = pygame.key.get_mods()
                if (event.key == pygame.K_q and
                    mods & pygame.KMOD_CTRL and mods & pygame.KMOD_ALT):
                    self._running = False
                # Fullscreen
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                # KVM toggle (delegated)
                elif self._kvm.handle_key(event):
                    pass  # consumed
            elif event.type == pygame.VIDEORESIZE:
                self.w, self.h = event.w, event.h

    def _toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def _draw_overlay(self):
        state_str = "REMOTE" if self._kvm.state.name == "FOCUSED_REMOTE" else "LOCAL"
        color = (0, 255, 0) if state_str == "REMOTE" else (255, 0, 0)
        text_surf = self._font.render(f" KVM: {state_str} ", True, (255, 255, 255), color)
        self._screen.blit(text_surf, (10, 10))

    def _render(self) -> None:
        try:
            frame = self._frame_queue.get_nowait()
            self._last_frame = frame
        except queue.Empty:
            frame = self._last_frame
        
        if frame is None:
            return
        
        # Upload frame to pygame surface
        if frame.shape[:2] == (self.h, self.w):
            # Same size: zero-copy blit
            surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        else:
            # Scale to window size
            surf = pygame.transform.smoothscale(
                pygame.surfarray.make_surface(frame.swapaxes(0, 1)),
                (self.w, self.h)
            )
        
        self._screen.blit(surf, (0, 0))
        self._draw_overlay()
        pygame.display.flip()
