import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock

import threading
import requests
import tempfile
from gtts import gTTS
import playsound
from config import GOOGLE_API_KEY  # Your API key

class JusticeApp(App):
    def build(self):
        self.title = "Justice AI Assistant"

        self.layout = BoxLayout(orientation='vertical')

        self.chat_history = Label(size_hint_y=None, markup=True)
        self.chat_history.bind(texture_size=self.update_height)

        scroll = ScrollView(size_hint=(1, 0.85))
        scroll.add_widget(self.chat_history)

        self.user_input = TextInput(size_hint=(1, 0.1), multiline=False)
        self.user_input.bind(on_text_validate=self.on_enter)

        btn_layout = BoxLayout(size_hint=(1, 0.05))
        self.speak_btn = Button(text="Speak")
        self.speak_btn.bind(on_press=self.listen)
        btn_layout.add_widget(self.speak_btn)

        self.layout.add_widget(scroll)
        self.layout.add_widget(self.user_input)
        self.layout.add_widget(btn_layout)

        self.append_chat("[b][color=00ff00]Justice:[/color][/b] Ready to assist you!")

        return self.layout

    def update_height(self, instance, value):
        instance.height = instance.texture_size[1]

    def append_chat(self, message):
        self.chat_history.text += message + "\n\n"
        Clock.schedule_once(self.scroll_to_bottom, 0.1)

    def scroll_to_bottom(self, dt):
        self.layout.children[2].scroll_y = 0

    def on_enter(self, instance):
        text = self.user_input.text.strip()
        if text:
            self.append_chat(f"[b][color=0000ff]You:[/color][/b] {text}")
            self.user_input.text = ""
            threading.Thread(target=self.get_response, args=(text,)).start()

    def get_response(self, prompt):
        try:
            response = self.call_gemini_api(prompt)
            answer = response.strip()
        except Exception as e:
            answer = "Sorry, I had trouble connecting to Gemini API."

        self.append_chat(f"[b][color=00ff00]Justice:[/color][/b] {answer}")
        self.speak(answer)

    def call_gemini_api(self, prompt):
        url = "https://api.gemini.example.com/v1/chat"  # Replace with actual Gemini API URL
        headers = {
            "Authorization": f"Bearer {GOOGLE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gemini-1",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "Gemini API error or limit reached."

    def listen(self, instance):
        self.append_chat("[b][color=ff0000]Justice:[/color][/b] Voice input not set up yet.")

    def speak(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            tmpfile = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3")
            tts.save(tmpfile.name)
            playsound.playsound(tmpfile.name, True)
            tmpfile.close()
        except Exception:
            pass

if __name__ == '__main__':
    JusticeApp().run()