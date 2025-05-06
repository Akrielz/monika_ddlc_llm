from typing import Tuple, Optional

import pygame
from pygame import Surface

from src.sprites.sprite import ScreenSize, Sprite, Coordinates
from src.text_utils.sentence_split import SentenceSplitter


class ChatBox(Sprite):
    def __init__(
            self,
            screen_size: ScreenSize,
            text: str,
            character_name: str,
            text_speed: float = 4.0
    ):

        image_path = "resources/images/chat/chat.webp"
        self.screen_size = screen_size
        self.load_image(image_path)
        super().__init__(self.image)

        self.sentence_splitter = SentenceSplitter()
        self.next_slide_token = "<next_slide>"

        self.prepare_text_info()
        self.set_text(text)
        self.set_character_name(character_name)
        self.set_text_speed(text_speed)

        self._prompt_mode = False

    @property
    def is_prompt_mode(self):
        return self._prompt_mode

    def _set_text_wait_color(self):
        self.chat_text_outer_color = (255, 0, 0)

    def _set_text_normal_color(self):
        self.chat_text_outer_color = (92, 56, 73)

    def set_text_color(self, is_model_loaded: bool):
        if not is_model_loaded:
            self._set_text_wait_color()
        else:
            self._set_text_normal_color()

    def prepare_text_info(self):
        self.chat_text_inner_color = (250, 250, 250)
        self.chat_text_outer_color = (92, 56, 73)

        self.character_inner_color = (250, 250, 250)
        self.character_outer_color = (176, 100, 140)

        self.chat_font = pygame.font.Font("resources/fonts/Aller_Rg.ttf", 30)
        self.character_font = pygame.font.Font("resources/fonts/RifficFree-Bold.ttf", 36)

        self.chat_start_pos = (220, 490)
        self.chat_end_pos = (860, 560)

        self.character_start_pos = (231, 447)
        self.character_end_pos = (359, 473)

        # Scale the start end pos to the new screen_size
        self.scaled_chat_start_pos = (
            self.chat_start_pos[0] * self.screen_size[0] / self.original_size[0],
            self.chat_start_pos[1] * self.screen_size[1] / self.original_size[1]
        )

        self.scaled_chat_end_pos = (
            self.chat_end_pos[0] * self.screen_size[0] / self.original_size[0],
            self.chat_end_pos[1] * self.screen_size[1] / self.original_size[1]
        )

        self.scaled_character_start_pos = (
            self.character_start_pos[0] * self.screen_size[0] / self.original_size[0],
            self.character_start_pos[1] * self.screen_size[1] / self.original_size[1]
        )

        self.scaled_character_end_pos = (
            self.character_end_pos[0] * self.screen_size[0] / self.original_size[0],
            self.character_end_pos[1] * self.screen_size[1] / self.original_size[1]
        )

        self.text_outline_size = 2
        self.character_outline_size = 3

        self.chat_bounding_box = pygame.Rect(
            self.scaled_chat_start_pos[0],
            self.scaled_chat_start_pos[1],
            self.scaled_chat_end_pos[0] - self.scaled_chat_start_pos[0],
            self.scaled_chat_end_pos[1] - self.scaled_chat_start_pos[1]
        )

        self.character_bounding_box = pygame.Rect(
            self.scaled_character_start_pos[0],
            self.scaled_character_start_pos[1],
            self.scaled_character_end_pos[0] - self.scaled_character_start_pos[0],
            self.scaled_character_end_pos[1] - self.scaled_character_start_pos[1]
        )

    def add_next_slides_tokens(
            self,
            text: str
    ):
        sentences = self.sentence_splitter(text)
        current_text = ""
        slides = []
        for sentence in sentences:
            if len(current_text) + len(sentence) > 100:
                current_text += f" {self.next_slide_token}"
                slides.append(current_text)
                current_text = f"{sentence}"
            else:
                current_text += f" {sentence}"
        slides.append(current_text)
        return " ".join(slides)

    def set_text(self, text: str):
        self._prompt_mode = False
        self._whole_text = f"{text}".strip()
        self._whole_text = self.add_next_slides_tokens(self._whole_text)

        text_remained = self._whole_text
        text_chunks = []
        while True:
            text_displayed, is_all_text_displayed = self._print_text_inside_box(
                None, self.chat_bounding_box, self.chat_font, text_remained, self.text_outline_size,
                self.chat_text_inner_color, self.chat_text_outer_color, simulate=True
            )
            text_chunks.append(text_displayed)
            text_remained = text_remained[len(text_displayed):]

            if is_all_text_displayed:
                break
            else:
                text_chunks[-1] = f"{text_chunks[-1]}..."

        text_chunks = [chunk.replace(self.next_slide_token, "") for chunk in text_chunks]
        self.text_chunks = text_chunks

        self.reset_text_index()
        self.set_chunk_index(0)

    def set_prompt(self, prompt: str):
        self._whole_text = f"{prompt}"
        self.text_chunks = [self._whole_text]
        self.finish_index()
        self.set_chunk_index(0)

    def set_chunk_index(self, chunk_index: int):
        self._chunk_index = chunk_index
        self._text = self.text_chunks[chunk_index]

    @property
    def text(self):
        return self._text[:self.text_index]

    def set_text_speed(self, text_speed: float):
        self.text_speed = text_speed

    def reset_text_index(self):
        self.text_index = 0
        self.text_index_float = 0.0

    def finish_index(self):
        self.text_index = len(self._text)
        self.text_index_float = len(self._text)

    def finish_text(self):
        if not self.is_chunk_finished():
            self.finish_index()
            return

        if self.ready_for_next_chunk:
            if self._chunk_index >= len(self.text_chunks) - 1:
                self._prompt_mode = True
                return

            self.set_chunk_index(self._chunk_index + 1)
            self.reset_text_index()

    def set_character_name(self, character_name: str):
        self.character_name = character_name

    def load_image(self, image_path: str):
        self.image = pygame.image.load(image_path)
        self.original_size = self.image.get_size()
        self.image = pygame.transform.smoothscale(self.image, self.screen_size)

    def draw(self, screen: Surface):
        super().draw(screen)
        self.print_character_name(screen)
        self.print_text(screen)
        self.update()

    def print_text(self, screen: Surface):
        text_displayed, is_all_text_displayed = self._print_text_inside_box(
            screen, self.chat_bounding_box, self.chat_font, self.text, self.text_outline_size,
            self.chat_text_inner_color, self.chat_text_outer_color
        )
        return text_displayed, is_all_text_displayed

    def print_character_name(self, screen: Surface):
        text_displayed, is_all_text_displayed = self._print_text_inside_box(
            screen, self.character_bounding_box, self.character_font, self.character_name, self.character_outline_size,
            self.character_inner_color, self.character_outer_color, centered=True
        )
        return text_displayed, is_all_text_displayed

    def is_chunk_finished(self):
        return self.text_index >= len(self._text)

    def update(self):
        if self.is_chunk_finished():
            self.ready_for_next_chunk = True
            return

        self.text_index_float += self.text_speed
        self.text_index = int(self.text_index_float)

    def _wrap_text(
            self,
            max_width: int,
            font: pygame.font.Font,
            text: str
    ):
        words = text.split(' ')
        lines = []
        current_line = words[0]

        for i in range(1, len(words)):
            word = words[i]
            if word == self.next_slide_token:
                lines.append(f"{current_line} {word}")
                current_line = ""
                continue

            test_line = f"{current_line} {word}"
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)

        lines = [f"{line} " for line in lines]
        return lines

    @staticmethod
    def _draw_text_with_outline(
            text: str,
            pos: Coordinates,
            screen: Surface,
            font: pygame.font.Font,
            outline_size,
            inner_color: Tuple[int, int, int],
            outer_color: Tuple[int, int, int],
    ):
        # Create the main text surface
        text_surface = font.render(text, True, inner_color)
        outline_size = outline_size

        # Create the outline by rendering the text multiple times in the outline color
        outline_surface = pygame.Surface(
            (text_surface.get_width() + outline_size * 2, text_surface.get_height() + outline_size * 2), pygame.SRCALPHA)

        # Draw the outline by shifting the text surface in different directions
        for dx in range(-outline_size, outline_size + 1):
            for dy in range(-outline_size, outline_size + 1):
                outline_surface.blit(
                    font.render(
                        text, True, outer_color
                    ),
                    (dx + outline_size, dy + outline_size)
                )

        # Blit the main text onto the outline
        outline_surface.blit(text_surface, (outline_size, outline_size))

        # Blit the text with the outline onto the screen
        screen.blit(outline_surface, pos)

        return outline_surface

    def _print_text_inside_box(
            self,
            screen: Optional[Surface],
            bounding_box: pygame.Rect,
            font: pygame.font.Font,
            text: str,
            outline_size: int = 2,
            inner_color: Tuple[int, int, int] = (255, 255, 255),
            outer_color: Tuple[int, int, int] = (0, 0, 0),
            centered: bool = False,
            simulate: bool = False
    ):
        if screen is None:
            assert simulate, "Screen must be provided if not simulating"

        width = bounding_box.width
        text_lines = self._wrap_text(width, font, text)

        y_offset = bounding_box.y
        x_offset = bounding_box.x

        text_displayed = ""
        is_all_text_displayed = True
        should_stop = False
        for line in text_lines:
            if self.next_slide_token in line:
                should_stop = True

            if centered:
                x_offset = bounding_box.x + (bounding_box.width - font.size(line)[0]) // 2

            if not simulate:
                self._draw_text_with_outline(
                    line,
                    (x_offset, y_offset),
                    screen=screen,
                    font=font,
                    outline_size=outline_size,
                    inner_color=inner_color,
                    outer_color=outer_color,
                )
            y_offset += font.get_linesize()
            text_displayed += line

            # Stop drawing text if we exceed the bounding box height
            if y_offset > bounding_box.y + bounding_box.height or should_stop:
                is_all_text_displayed = False
                break

        return text_displayed, is_all_text_displayed
