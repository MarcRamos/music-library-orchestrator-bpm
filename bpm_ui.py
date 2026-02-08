# bpm_ui.py
import pygame
import time
import os

def measure_bpm_ui(mp3_path):
    """
    Abre UI para medir BPM:
    - SPACE = Tap
    - ENTER = Guardar
    - ESC = Cancelar
    - Botones:
        ▶ Play
        ⏸ Stop
        ↺ Reset (reinicia reproducción)
    Devuelve BPM medido por el usuario (int) o None si cancelado.
    """

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("BPM Tapper")
    font = pygame.font.SysFont("arial", 24)
    clock = pygame.time.Clock()

    taps = []
    bpm = 0
    playing = False

    # Botones
    btn_play = pygame.Rect(100, 300, 150, 40)
    btn_stop = pygame.Rect(325, 300, 150, 40)
    btn_restart = pygame.Rect(550, 300, 150, 40)

    def draw_button(rect, text):
        mouse = pygame.mouse.get_pos()
        color = (120, 120, 120) if rect.collidepoint(mouse) else (70, 70, 70)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        label = font.render(text, True, (220, 220, 220))
        screen.blit(label, label.get_rect(center=rect.center))

    running = True
    while running:
        screen.fill((30, 30, 30))
        screen.blit(font.render(f"Now Playing:\n{os.path.basename(mp3_path)}", True, (220, 220, 220)), (40, 40))
        bpm_text = f"BPM: {int(bpm) if bpm else '--'}"
        screen.blit(font.render(bpm_text, True, (180, 220, 180)), (40, 100))
        screen.blit(font.render("SPACE=Tap | ENTER=Guardar | ESC=Cancelar", True, (150, 150, 150)), (40, 160))

        draw_button(btn_play, "[> ] Play")
        draw_button(btn_stop, "[||] Stop")
        draw_button(btn_restart, "[R] Restart")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    now = time.time()
                    taps.append(now)
                    if len(taps) > 1:
                        intervals = [taps[i]-taps[i-1] for i in range(1, len(taps))]
                        bpm = 60 / (sum(intervals)/len(intervals))
                elif event.key == pygame.K_RETURN and bpm:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    pygame.quit()
                    return int(bpm)
                elif event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    pygame.quit()
                    return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(event.pos):
                    if not playing:
                        pygame.mixer.music.load(mp3_path)
                        pygame.mixer.music.play()
                        playing = True
                elif btn_stop.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    playing = False
                elif btn_restart.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(mp3_path)
                    pygame.mixer.music.play()
                    playing = True

        pygame.display.flip()
        clock.tick(60)