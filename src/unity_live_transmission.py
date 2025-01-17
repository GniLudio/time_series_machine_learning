import os
import random
import string
import tkinter as tk
import uuid
import tkinter
from tkinter import messagebox
import tkinter.simpledialog
import cv2
from PIL import Image, ImageTk
import csv
import numpy as np
import pyautogui
import time
import threading

class VideoPlayer:
    def __init__(self, root, video_folders):
        self.root = root
        self.participant_id = tkinter.simpledialog.askstring(title="Participant", prompt="Enter the participant identifier:\t\t") or 'test'  # Generiere zufällige ID

        # Webcam starten
        threading.Thread(target=self.show_webcam, daemon=True).start()

        self.initSampleVideos(video_folders)

        self.createCanvas()

        self.generateButtons()
        self.generateQuestions()



        self.update_video()

    def createCanvas(self):
        # Setze die Canvas-Größe auf die halbe Originalgröße
        self.canvas_width = self.video_width // 2
        self.canvas_height = self.video_height // 2

        # Linken Frame für Video erstellen
        self.left_frame = tk.Frame(self.root, width=300, height=400, bg='grey')
        self.left_frame.grid(row=0, column=0, padx=10, pady=5)

        # Rechten Frame für Fragen erstellen
        self.right_frame = tk.Frame(self.root, width=600, height=400, bg='grey')
        self.right_frame.grid(row=0, column=1, padx=10, pady=5)

        # GUI-Elemente im linken Frame erstellen
        self.label_action_unit = tk.Label(self.left_frame, text=self.get_current_action_unit_description(), bg='grey')
        self.label_action_unit.grid(row=0, column=0, padx=5, pady=5)

        # Canvas erstellen mit halber Originalgröße
        self.canvas = tk.Canvas(self.left_frame, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=1, column=0, padx=5, pady=5)
    def initSampleVideos(self, video_folders):
        self.is_paused = False  # Video ist standardmäßig pausiert
        self.video_folders = sorted(video_folders, key= lambda x: int(x[2:]))  # Videos in chronologischer Reihenfolge
        self.current_video_index = 0
        self.video_path = self.get_video_path()
        self.video = cv2.VideoCapture(self.video_path)

        # Originalgröße des Videos abrufen
        self.video_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def generateButtons(self):
        # Start/Pause-Button
        self.button_start = tk.Button(self.left_frame, text="Start/Pause", command=self.toggle_video)
        self.button_start.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        # Weiter-Button
        self.button_next = tk.Button(self.right_frame, text="Weiter", command=self.next_video)
        self.button_next.grid(row=18, column=5, sticky='ew', padx=5, pady=5)

        # Zurück-Button
        self.button_prev = tk.Button(self.right_frame, text="Zurück", command=self.prev_video)
        self.button_prev.grid(row=19, column=5, sticky='ew', padx=5, pady=5)

        # Start Recording Button
        self.button_record = tk.Button(self.left_frame, text="Start Recording", command=self.start_recording_thread)
        self.button_record.grid(row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

    def generateQuestions(self):
        # Likert-Optionen einmalig über dem ersten Fragenblock platzieren
        likert_options = ['Not at All', 'Not Much', '', 'Somewhat', 'Very Much']
        for i, option in enumerate(likert_options, 1):
            label_option = tk.Label(self.right_frame, text=option, bg='grey')
            label_option.grid(row=0, column=i, sticky='n', padx=(5, 5))

        # Fragen im rechten Frame mit Überschrift "CC4"
        self.var_ratings = []  # Liste für die Bewertungsvariablen
        self.create_question(self.right_frame, "How well does the final expression represent the intended action unit?",
                             2, "CC4")
        self.create_question(self.right_frame, "Were there any noticeable delays or breaks in the animation?", 3, "CC4")
        self.create_question(self.right_frame, "How well does the animation reflect your intended expression of the action unit over time?", 4,
                             "CC4")

    def show_webcam(self):
        print("Webcam-Funktion aufgerufen.")
        cap = None
        for index in range(3):  # Probiere mehrere mögliche Webcam-Indices (0, 1, 2)
            #cap = cv2.VideoCapture(index)
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # DirectShow erzwingen (Windows)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            if cap.isOpened():
                print(f"Webcam erkannt an Index {index}")
                break
        else:
            messagebox.showerror("Fehler", "Keine Webcam gefunden! Bitte überprüfen Sie die Verbindung.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Fehler beim Lesen des Webcam-Feeds.")
                break

            # Zeige das Webcam-Bild in einem separaten Fenster
            cv2.imshow("Webcam Input (Drücke 'q' zum Beenden)", frame)

            # Beende das Fenster mit der Taste 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Webcam-Fenster geschlossen.")
                break

        cap.release()
        cv2.destroyAllWindows()


    def generate_random_id(self):
        return str(uuid.uuid4())[:8]

    def create_header(self, frame, header_text, row):
        """Erstellt eine Überschrift im angegebenen Frame."""
        label_header = tk.Label(frame, text=header_text, bg='grey', font=("Arial", 12, "bold"))
        label_header.grid(row=row, column=0, columnspan=6, padx=5, pady=5, sticky='w')  # Zentriert über die gesamte Breite

    def create_question(self, frame, question_text, row, block_name):
        """Erstellt eine Frage mit Radiobuttons im angegebenen Frame."""
        label_question = tk.Label(frame, text=question_text, bg='grey')
        label_question.grid(row=row + 1, column=0, padx=5, pady=5, sticky='w')

        var_rating = tk.IntVar(value=0)  # Variable für die Bewertung der Frage
        self.var_ratings.append((var_rating, question_text, block_name))  # Füge die Variable, die Frage und den Blocknamen zur Liste hinzu

        for i in range(1, 6):
            rb = tk.Radiobutton(frame, variable=var_rating, value=i, bg='grey')
            rb.grid(row=row + 1, column=i, sticky='n', padx=(5, 5))  # Horizontale Anordnung

    def get_video_path(self):
        """Gibt den Pfad des aktuellen Videos zurück."""
        if self.current_video_index < len(self.video_folders):
            folder = self.video_folders[self.current_video_index]
            video_path = os.path.join("resources", "Videos", folder, "WM.avi")
            print(video_path)
            return video_path
        return ""

    def get_current_action_unit_description(self):
        """Gibt die aktuelle Action Unit und deren Beschreibung zurück."""
        if self.current_video_index < len(self.video_folders):
            action_unit = self.video_folders[self.current_video_index]
            # Hier die Beschreibung der Action Units
            descriptions = {
                "AU1": "Inner brow raiser lifts the medial brow and forehead area.",
                "AU2": "Outer brow raiser lifts the lateral brow and forehead areas.",
                "AU4": "Brow lowerer knits (corrugator supercilii) and" + "\n" + "lowers (procerus, depressor supercilii, and parts of corrugator supercilii)" + "\n" + "the brow area and lower central forehead.",
                "AU9": "Nose wrinkler lifts the sides of the nose, nostrils, and central upper lip area.",
                "AU12": "Lip corner puller draws the lip corners up, back, and laterally.",
                "AU17": "Chin raiser pushes the up lower lip and chin area.",
                "AU20": "Beschreibung für AU20: ...",
                "AU24": "Lip presser compresses the top and bottom lip against each other.",
            }
            return f"Action Unit: {action_unit}\n{descriptions.get(action_unit, 'Keine Beschreibung verfügbar.')}"
        return "Keine Action Unit verfügbar."

    def update_video(self):
        """Aktualisiert das Video im Canvas."""
        if not self.is_paused:
            ret, frame = self.video.read()
            if ret:
                # Resize frame for display
                frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                self.photo = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.root.after(10, self.update_video)
            else:
                # Wenn das Video zu Ende ist, von vorne abspielen
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Video von vorne abspielen
                self.update_video()  # Update erneut aufrufen

    def toggle_video(self):
        """Startet oder pausiert das Video."""
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self.update_video()  # Video starten/fortsetzen

    def next_video(self):
        """Wechselt zum nächsten Video und speichert die Antworten in einer CSV-Datei."""
        action_unit = self.video_folders[self.current_video_index]
        answers = [(question_text, var_rating.get(), block_name) for var_rating, question_text, block_name in self.var_ratings]
        self.save_answers(action_unit, answers)  # Speichere die Antworten

        self.current_video_index += 1
        if self.current_video_index < len(self.video_folders):
            self.video.release()
            self.video_path = self.get_video_path()
            self.video = cv2.VideoCapture(self.video_path)

            # Update die Action Unit Beschreibung
            self.label_action_unit.config(text=self.get_current_action_unit_description())

            # Setze den Startstatus zurück
            self.is_paused = False  # Setze auf spielen, damit das neue Video automatisch abgespielt wird
            self.update_video()  # Update starten

            # Antworten zurücksetzen
            self.reset_answers()
        else:
            messagebox.showinfo("Info", "Keine weiteren Videos vorhanden.")

    def prev_video(self):
        """Wechselt zum vorherigen Video, wenn möglich."""
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.video.release()
            self.video_path = self.get_video_path()
            self.video = cv2.VideoCapture(self.video_path)

            # Update die Action Unit Beschreibung
            self.label_action_unit.config(text=self.get_current_action_unit_description())

            # Setze den Startstatus zurück
            self.is_paused = False  # Setze auf spielen, damit das neue Video automatisch abgespielt wird
            self.update_video()  # Update starten

            # Antworten zurücksetzen
            self.reset_answers()
        else:
            messagebox.showinfo("Info", "Dies ist das erste Video.")

    def save_answers(self, action_unit, answers):
        """Speichert die Antworten in einer CSV-Datei."""
        filename = "responses.csv"
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Header hinzufügen, falls die Datei leer ist
            if file.tell() == 0:
                writer.writerow(["Participant ID", "Action Unit", "Frage", "Antwort", "Block"])

            # Zeilen mit Antworten hinzufügen
            for question_text, answer, block_name in answers:
                writer.writerow([self.participant_id, action_unit, question_text, answer, block_name])

    def reset_answers(self):
        """Setzt die Antworten der Radiobuttons zurück."""
        for var_rating, _, _ in self.var_ratings:
            var_rating.set(0)  # Setze den Wert auf 0

    def start_recording_thread(self):
        """Startet die Bildschirmaufnahme in einem separaten Thread."""
        recording_thread = threading.Thread(target=self.start_recording)
        recording_thread.start()

    def start_recording(self):
        action_unit = self.video_folders[self.current_video_index]
        participant_folder = os.path.join("teilnehmerVideos", self.participant_id)
        os.makedirs(participant_folder, exist_ok=True)

        output_filename = os.path.join(participant_folder, f"recording_{self.participant_id}_{action_unit}.mp4")
        screen_size = (1920, 1080)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 20.0  # Frames pro Sekunde
        out = cv2.VideoWriter(output_filename, fourcc, fps, screen_size)

        start_time = time.time()
        end_time = start_time + 5  # 30 Sekunden aufnehmen


        messagebox.showinfo("Info", "Aufnahme gestartet! Die Aufnahme dauert 30 Sekunden.")

        while time.time() < end_time:

            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame = cv2.resize(frame, screen_size)
            out.write(frame)

        out.release()
        messagebox.showinfo("Info", "Aufnahme abgeschlossen!")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Player and Screen Recorder")
    root.maxsize(1280, 1000)
    root.config(bg="grey")

    video_folders = ['AU1', 'AU2', 'AU4', 'AU9', 'AU12', 'AU17', 'AU20', 'AU24']
    player = VideoPlayer(root, video_folders)

    root.mainloop()
