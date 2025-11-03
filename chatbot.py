# chatbot_tkinter.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from datetime import datetime
import random
import numpy as np
from textblob import TextBlob
import threading
import time
from openai import OpenAI  # <-- Nueva importación

# ======================================
# CONFIGURA TU CLAVE DE OPENAI AQUÍ
# ======================================
API_KEY = "TU_API_KEY_AQUI"  # Reemplaza con tu clave real


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Chatbot PIA - Sistemas Inteligentes")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar chatbot
        self.chatbot = IntelligentChatbot(API_KEY)
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(
            main_frame, 
            text="Chatbot Inteligente - PIA Sistemas Inteligentes",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.chat_area = scrolledtext.ScrolledText(
            main_frame, width=80, height=25, font=('Arial', 10), wrap=tk.WORD
        )
        self.chat_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.chat_area.config(state=tk.DISABLED)
        
        self.input_entry = ttk.Entry(main_frame, font=('Arial', 12))
        self.input_entry.grid(row=2, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))
        self.input_entry.bind('<Return>', self.send_message)
        
        send_button = ttk.Button(main_frame, text="Enviar", command=self.send_message)
        send_button.grid(row=2, column=1, padx=5, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Limpiar Chat", command=self.clear_chat).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar Conversación", command=self.export_chat).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Estadísticas", command=self.show_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.add_bot_message("¡Hola! Soy tu asistente inteligente del PIA. ¿En qué puedo ayudarte hoy?")
    
    def add_user_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\n👤 Tú: {message}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def add_bot_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"🤖 Bot: {message}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def send_message(self, event=None):
        user_input = self.input_entry.get().strip()
        if user_input:
            self.add_user_message(user_input)
            self.input_entry.delete(0, tk.END)
            thread = threading.Thread(target=self.process_bot_response, args=(user_input,))
            thread.daemon = True
            thread.start()
    
    def process_bot_response(self, user_input):
        time.sleep(0.5)
        response = self.chatbot.generate_response(user_input)
        self.root.after(0, lambda: self.add_bot_message(response))
    
    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.chatbot.clear_history()
        self.add_bot_message("Chat limpiado. ¿En qué puedo ayudarte?")
    
    def export_chat(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_export_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Conversación del Chatbot PIA - Sistemas Inteligentes\n")
                f.write("=" * 50 + "\n\n")
                for msg in self.chatbot.conversation_history:
                    role = "Usuario" if msg['role'] == 'user' else "Bot"
                    f.write(f"{role} ({msg['timestamp']}): {msg['content']}\n\n")
            messagebox.showinfo("Éxito", f"Conversación exportada como: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
    
    def show_stats(self):
        stats = self.chatbot.get_conversation_stats()
        stats_text = f"""
Estadísticas de la Conversación:
────────────────────────────
• Mensajes totales: {stats['total_messages']}
• Tus mensajes: {stats['user_messages']}
• Mis respuestas: {stats['assistant_messages']}
• Longitud promedio: {stats['avg_user_length']:.1f} caracteres
"""
        messagebox.showinfo("Estadísticas", stats_text)


class IntelligentChatbot:
    def __init__(self, api_key):
        self.conversation_history = []
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, user_input):
        self.add_message("user", user_input)

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un chatbot educativo que ayuda en el PIA de Sistemas Inteligentes."},
                    {"role": "user", "content": user_input}
                ]
            )
            response = completion.choices[0].message.content.strip()
        except Exception as e:
            response = f"Ocurrió un error al conectar con OpenAI: {e}"

        self.add_message("assistant", response)
        return response

    def add_message(self, role, content):
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def clear_history(self):
        self.conversation_history = []

    def get_conversation_stats(self):
        user_msgs = [msg for msg in self.conversation_history if msg['role'] == 'user']
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len(user_msgs),
            'assistant_messages': len(self.conversation_history) - len(user_msgs),
            'avg_user_length': np.mean([len(msg['content']) for msg in user_msgs]) if user_msgs else 0
        }


def main():
    try:
        root = tk.Tk()
        app = ChatbotGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Presiona Enter para salir...")


if __name__ == "__main__":
    main()
