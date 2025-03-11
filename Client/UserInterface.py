from collections import defaultdict
from Client.ControlledUnit import Controlled_Unit
from Client.Unit import Unit
import pygame
from GlobalConstants import WINDOW_WIDTH, WINDOW_HEIGHT
class UserInterface:
    def __init__(self):
        self.unit_list : list[Unit] = []
        self.player_list : list[Controlled_Unit] = []
        self.score_font = pygame.font.SysFont("Arial", 30)  

    def draws(self, screen):
        score_text = f"Score: {int(sum(player.score_ for player in self.player_list))}"
        score_surface = self.score_font.render(score_text, True, self.player_list[0].color_) 
        screen.blit(score_surface, (WINDOW_WIDTH - score_surface.get_width() - 10, 10)) 

    def draw(self, screen):

        score_by_id = defaultdict(int)
        player_by_id = {}  
        for player in self.unit_list:
            score_by_id[player.id_] += player.score_
            if player.id_ not in player_by_id: 
                player_by_id[player.id_] = player

        top_scores = sorted(score_by_id.items(), key=lambda x: x[1], reverse=True)

        y_offset = 10 
        for idx, (player_id, total_score) in enumerate(top_scores[:5]):
            player : Unit = player_by_id.get(player_id, (120, 120, 120))

            score_text = f"{idx+1}. {player.nickname_}: {int(total_score)}"
            score_surface = self.score_font.render(score_text, True, player.color_) 
            screen.blit(score_surface, (WINDOW_WIDTH - score_surface.get_width() - 10, y_offset))
            y_offset += 35  