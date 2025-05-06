from typing import List

import pygame

from src.llm.chat_gemma2 import ChatGemma2
from src.sprites.background import Background
from src.sprites.character import Character
from src.sprites.chat_box import ChatBox
from src.sprites.sprite import Sprite


class Game:
    def __init__(self):
        pygame.init()

        self.character_name = "Monika"
        self.player_name = "Akriel"

        self.screen_size = (1920, 1080)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(f"Just {self.character_name}")

        self.character_path = "resources/images/character/monika/"
        self.background_sprite_path = "resources/images/background/club.webp"
        self.sound_path = 'resources/sounds/1-04. Okay, Everyone!.mp3'

        try:
            self.sound = pygame.mixer.Sound(self.sound_path)
            self.sound.play(-1)
        except pygame.error as e:
            print(f"Error loading sound: {e}")
            self.sound = None

        self.clock = pygame.time.Clock()
        self.running = True

        self.character = Character(self.character_path, self.screen_size)
        initial_text = (
            f"\"Hi, I'm {self.character_name}, the president of the Literature Club! "
            f"You must be {self.player_name}? I am so happy to meet you!\""
         )
        self.chat_box = ChatBox(
            self.screen_size,
            initial_text,
            self.character_name,
        )
        self.background = Background(self.background_sprite_path, self.screen_size)

        self.layers: List[Sprite] = [
            self.background,
            self.character,
            self.chat_box
        ]
        self.prompt = ""
        self.llm = ChatGemma2(self.character_name, self.player_name, self.character.available_emotions)

    def set_dummy_answer(self, _unused_prompt: str):
        self.chat_box.set_text("A very long message " * 20)
        self.chat_box.set_character_name(self.character_name)
        self.character.set_mood(self.character.available_emotions[0])

    def set_llm_answer(self, prompt: str):
        answer = self.llm.generate_answer(prompt, last_k_messages=15)
        emotion = answer["emotion"]
        response = answer["response"]
        self.chat_box.set_text(response)
        self.chat_box.set_character_name(self.character_name)
        self.character.set_mood(emotion)

    def run(self):
        self.llm.post_init()
        self._run()

    def _run(self):
        while self.running:
            self.event_handler()
            self.render()
            self.clock.tick(60)

    def render(self):
        if self.chat_box.is_prompt_mode:
            self.chat_box.set_character_name(self.player_name)
            display_prompt = self.prompt if len(self.prompt) else "Type your answer here..."
            self.chat_box.set_prompt(display_prompt)
            self.chat_box.set_text_color(self.llm.is_model_loaded)
        else:
            self.chat_box.set_character_name(self.character_name)

        for layer in self.layers:
            layer.draw(self.screen)

        pygame.display.flip()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self.handle_key_down(event)

    def handle_key_down(self, event: pygame.event.Event):
        self.handle_general_functionalities(event)

        if self.chat_box.is_prompt_mode:
            self.handle_prompt_mode(event)
        else:
            self.handle_read_mode(event)

    def handle_general_functionalities(self, event: pygame.event.Event):
        if event.key == pygame.K_ESCAPE:
            self.running = False

        if event.key == pygame.K_F2:
            pygame.display.toggle_fullscreen()

    def handle_prompt_mode(self, event: pygame.event.Event):
        if event.key == pygame.K_RETURN and self.llm.is_model_loaded:
            if len(self.prompt) == 0:
                return

            self.set_llm_answer(self.prompt)
            self.prompt = ""
            return

        if event.key == pygame.K_BACKSPACE:
            self.prompt = self.prompt[:-1]
            return

        self.prompt += event.unicode

    def handle_read_mode(self, event: pygame.event.Event):
        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.chat_box.finish_text()