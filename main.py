from pathlib import Path

import pygame


SCREEN_WIDTH = 900
SCREEN_HEIGHT = 400
PLAYER_SPEED = 260
PLAYER_SIZE = (72, 54)

BACKGROUND_COLOR = (135, 206, 235)
GROUND_COLOR = (92, 166, 76)
BLOCK_COLOR = (240, 135, 35)


def move_player(
    player_rect: pygame.Rect,
    obstacle_rect: pygame.Rect,
    movement: pygame.Vector2,
) -> bool:
    """Move the player while keeping it on-screen and outside the obstacle."""
    hit_obstacle = False
    player_rect.x += round(movement.x)

    if player_rect.colliderect(obstacle_rect):
        hit_obstacle = True
        if movement.x > 0:
            player_rect.right = obstacle_rect.left
        elif movement.x < 0:
            player_rect.left = obstacle_rect.right

    player_rect.y += round(movement.y)

    if player_rect.colliderect(obstacle_rect):
        hit_obstacle = True
        if movement.y > 0:
            player_rect.bottom = obstacle_rect.top
        elif movement.y < 0:
            player_rect.top = obstacle_rect.bottom

    player_rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    return hit_obstacle


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bird and Block")
    clock = pygame.time.Clock()

    bird_path = Path(__file__).parent / "imgs" / "bird.gif"
    hit_sound_path = Path(__file__).parent / "sounds" / "sound.mp3"
    bird_frames = [
        (
            pygame.transform.smoothscale(frame.convert_alpha(), PLAYER_SIZE),
            max(delay / 1000, 0.01),
        )
        for frame, delay in pygame.image.load_animation(bird_path)
    ]
    hit_sound = pygame.mixer.Sound(hit_sound_path)

    player_rect = bird_frames[0][0].get_rect(midleft=(40, SCREEN_HEIGHT // 2))
    obstacle_rect = pygame.Rect(700, 120, 120, 160)
    collision_active = False
    animation_frame = 0
    animation_elapsed = 0.0

    running = True
    while running:
        delta_time = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            int(keys[pygame.K_DOWN] or keys[pygame.K_s])
            - int(keys[pygame.K_UP] or keys[pygame.K_w]),
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()

        animation_elapsed += delta_time
        while animation_elapsed >= bird_frames[animation_frame][1]:
            animation_elapsed -= bird_frames[animation_frame][1]
            animation_frame = (animation_frame + 1) % len(bird_frames)

        hit_obstacle = move_player(
            player_rect,
            obstacle_rect,
            direction * PLAYER_SPEED * delta_time,
        )
        if hit_obstacle and not collision_active:
            hit_sound.play()
        collision_active = hit_obstacle

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(
            screen,
            GROUND_COLOR,
            (0, SCREEN_HEIGHT - 35, SCREEN_WIDTH, 35),
        )
        pygame.draw.rect(screen, BLOCK_COLOR, obstacle_rect, border_radius=6)
        screen.blit(bird_frames[animation_frame][0], player_rect)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
