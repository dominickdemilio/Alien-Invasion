import sys
import pygame

from time import sleep

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("Dom's Alien Invasion")

        # Create an instance to store game settings
        self.stats = GameStats(self)

        # Set the background color
        self.bg_color = (0, 0, 0)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()

        # Add aliens
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # Keep count of aliens killed
        self.score = 0

    def run_game(self):
        # Start the game's main loop
        while True:
            # Check if any keyboard events have occurred
            self._check_events()

            # Check to see if the game is still active
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        # Player quit the game?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Player press the right / left arrow key?
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            # Player release the arrow key?
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        # Which key was pressed?
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        # Player hit Q?
        elif event.key == pygame.K_q:
            sys.exit()

        # Player hit space bar?
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        # Create a bullet and add it to the group of bullets
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        # Update positions of the bullets and delete old bullets
        self.bullets.update()

        # Delete bullets off screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        # Check if bullets have hit aliens
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )
        if collisions:
            for aliens in collisions.values():
                self.score += len(aliens)

        # Check if the aliens group is empty
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()

    def _update_aliens(self):
        # Update the positions of all aliens in the fleet
        self._check_fleet_edges()
        self.aliens.update()

        # Check for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            print("SHIP HIT!!!")
            self._ship_hit()

        self._check_aliens_bottom()

    def _create_fleet(self):
        aliens = Alien(self)
        alien_width, alien_height = aliens.rect.size

        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (
            self.settings.screen_height - (3 * alien_height) - ship_height
        )
        number_rows = available_space_y // (2 * alien_height)

        # Create full fleet
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        aliens = Alien(self)
        alien_width, alien_height = aliens.rect.size
        alien_width = aliens.rect.width
        aliens.x = alien_width + 2 * alien_width * alien_number
        aliens.rect.x = aliens.x
        aliens.rect.y = alien_height + 2 * aliens.rect.height * row_number
        self.aliens.add(aliens)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        # Drop the fleet
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed

        # Change directions
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        # If alien/ship collision
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1

            # Delete any remaining aliens & bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.75)
        else:
            self.stats.game_active = False

    def _check_aliens_bottom(self):
        # Check if aliens have invaded the bottom of the screen
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        # Draw bullets
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # Draw aliens
        self.aliens.draw(self.screen)

        # Draw scoreboard
        self.draw_scoreboard()

        pygame.display.flip()

    def draw_scoreboard(self):
        font = pygame.font.SysFont(None, 40)

        # Display score
        score_text = font.render(
            "Score: " + str(self.score), True, (255, 255, 255)
        )
        score_rect = score_text.get_rect()
        score_rect.top = 10
        score_rect.right = self.screen_rect.right - 10

        # Display lives
        lives_text = font.render(
            "Remaining Ships: " + str(self.stats.ships_left),
            True,
            (255, 255, 255),
        )
        lives_rect = lives_text.get_rect()
        lives_rect.top = score_rect.bottom + 10
        lives_rect.right = self.screen_rect.right - 10

        self.screen.blit(score_text, score_rect)
        self.screen.blit(lives_text, lives_rect)


if __name__ == "__main__":

    ai = AlienInvasion()
    ai.run_game()

quit()
