from collections import defaultdict
from Client.ControlledUnit import ControlledUnit
from Client.Unit import Unit
import pygame
from GlobalConstants import WINDOW_WIDTH, WINDOW_HEIGHT
class UserInterface:
    def __init__(self):
        self.unit_list: list[Unit] = []
        self.player_list: list[ControlledUnit] = []
        self.score_font = pygame.font.SysFont("Arial", 30)  

    def draw(self, screen):
        score_by_id = defaultdict(int)
        player_by_id = {}  
        for player in self.unit_list:
            score_by_id[player.id] += player.score
            if player.id not in player_by_id: 
                player_by_id[player.id] = player

        top_scores = sorted(score_by_id.items(), key=lambda x: x[1], reverse=True)

        y_offset = 10 
        for idx, (player_id, total_score) in enumerate(top_scores[:5]):
            player: Unit = player_by_id.get(player_id, (120, 120, 120))

            score_text = f"{idx+1}. {player.nickname}: {int(total_score)}"
            score_surface = self.score_font.render(score_text, True, player.color) 
            screen.blit(score_surface, (WINDOW_WIDTH - score_surface.get_width() - 10, y_offset))
            y_offset += 35  