from typing import Optional, List, Dict, Any

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig


class ChatGemma2:
    def __init__(
            self,
            character_name: str,
            player_name: str,
            emotion_list: List[str],
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.chat_messages_complex = []
        self.chat_messages_simple = []
        self.character_name = character_name
        self.player_name = player_name
        self.emotion_list = emotion_list

        self.generate_response_kwargs = {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.8,
            "do_sample": True,
        }

        self.generate_mood_kwargs = {
            "max_new_tokens": 10,
            "temperature": 1.0,
            "do_sample": False,
        }
        self._model_loaded = False

    def post_init(self):
        quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
        self.model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2-2b-it",
            quantization_config=quantization_config,
            low_cpu_mem_usage=True,
        )
        self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
        self._model_loaded = True

    @property
    def is_model_loaded(self):
        return self._model_loaded

    def _add_message(self, role: str, content: str, simple: bool = False):
        if simple:
            self.chat_messages_simple.append({"role": role, "content": content})
        else:
            self.chat_messages_complex.append({"role": role, "content": content})

    def reset_messages(self):
        self.chat_messages_complex = []
        self.chat_messages_simple = []

    def _add_user_message(self, content: str):
        prompt = (
            f'You are {self.character_name} from Doki Doki Literature Club, chatting with player {self.player_name}. '
            f'{self.player_name} said: "{content}".\n'
            f'Give a chat-like response to the player with no action tags. \n'
        )

        self._add_message("user", prompt, simple=False)
        self._add_message("user", content, simple=True)

    def _add_model_message(self, model_response: str):
        self._add_message("model", model_response, simple=False)
        self._add_message("model", model_response, simple=True)

    @staticmethod
    def _parse_model_answer(all_text: str):
        start_of_turn = all_text.rfind("<start_of_turn>model")
        if start_of_turn == -1:
            raise ValueError("Could not find the model response in the generated text.")

        start_of_turn += len("<start_of_turn>model")
        model_response = all_text[start_of_turn:]
        end_of_turn = model_response.find("<end_of_turn>")
        if end_of_turn == -1:
            end_of_turn = len(model_response)
        model_response = model_response[:end_of_turn]

        return model_response

    @staticmethod
    def parse_only_letters(text: str):
        small_letters = [chr(i) for i in range(ord("a"), ord("z") + 1)]
        big_letters = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
        letters = small_letters + big_letters
        return "".join([c for c in text if c in letters])

    @property
    def mixed_messages(self):
        # Get the last 2 complex messages
        if len(self.chat_messages_complex) < 2:
            return self.chat_messages_complex

        return self.chat_messages_simple[:-2] + self.chat_messages_complex[-2:]

    @property
    def len_chat(self):
        return len(self.chat_messages_complex)

    def _generate(
            self,
            messages: List[Dict[str, str]],
            generate_kwargs: Dict[str, Any],
    ) -> str:
        input_ids = self.tokenizer.apply_chat_template(
            messages, return_tensors="pt", return_dict=True, add_generation_prompt=True
        ).to(self.device)
        outputs = self.model.generate(**input_ids, **generate_kwargs)[0]

        all_text = self.tokenizer.decode(outputs)
        model_response = self._parse_model_answer(all_text)
        return model_response

    def _generate_response(self, last_k_messages: Optional[int] = None) -> str:
        selected_messages = self.mixed_messages
        if last_k_messages is not None:
            selected_messages = self.mixed_messages[-last_k_messages:]

        model_answer = self._generate(selected_messages, self.generate_response_kwargs)
        self._add_model_message(model_answer)
        return model_answer

    def _identify_mood(self, text: str) -> str:
        prompt = (
            f'Analyze this text {text} and select the most appropriate mood from the following list: {self.emotion_list}'
            f'Answer in one word, e.g. {self.emotion_list[0]}. \n'
        )
        messages = [
            {
                'role': 'user',
                'content': prompt,
            }
        ]
        mood = self._generate(messages, self.generate_mood_kwargs)
        mood = self.parse_only_letters(mood)
        return mood

    def generate_answer(
            self,
            user_input: str,
            last_k_messages: Optional[int] = None
    ) -> Dict[str, str]:
        self._add_user_message(user_input)

        model_response = self._generate_response(last_k_messages)
        mood = self._identify_mood(model_response)

        return {'emotion': mood, 'response': model_response}
