import tkinter as tk
from tkinter import filedialog, messagebox, font
import json
import os
import sys
import urllib.request

class SimpleTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur de texte simple")
        self.root.geometry("950x600")

        # Barre d'onglets
        self.tab_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.tab_frame.pack(side="top", fill="x")

        self.tabs = ["Accueil", "Insertion", "Aide", "Fichier", "Autres"]
        self.current_tab = tk.StringVar(value="Accueil")

        for tab in self.tabs:
            btn = tk.Radiobutton(
                self.tab_frame, text=tab, variable=self.current_tab, value=tab,
                indicatoron=0, width=12, font=("Arial", 11, "bold"),
                bg="#f5f5f5", selectcolor="#e3e3e3", relief="flat",
                command=self.update_toolbar
            )
            btn.pack(side="left", padx=2, pady=2)

        # Barre d'outils
        self.toolbar = tk.Frame(self.root, bg="#ffffff")
        self.toolbar.pack(side="top", fill="x", pady=(0, 2))

        self.create_home_toolbar()

        # Cadre principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Zone de texte
        self.text = tk.Text(self.main_frame, wrap="word", undo=True)
        self.text.pack(side="left", fill="both", expand=True)
        self.text.bind("<<Modified>>", self.on_text_change)

        # Scrollbar pour la zone de texte
        self.scroll_y = tk.Scrollbar(self.text, orient="vertical", command=self.text.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.text["yscrollcommand"] = self.scroll_y.set

        # Volet latéral pour les titres/sous-titres
        self.section_listbox = tk.Listbox(self.main_frame, width=35)
        self.section_listbox.pack(side="right", fill="y")
        self.section_listbox.bind("<<ListboxSelect>>", self.go_to_section)

        # Polices personnalisées
        self.title_font = font.Font(self.text, self.text.cget("font"))
        self.title_font.configure(size=18, weight="bold")
        self.subtitle_font = font.Font(self.text, self.text.cget("font"))
        self.subtitle_font.configure(size=14, weight="bold", slant="italic")
        self.bold_font = font.Font(self.text, self.text.cget("font"))
        self.bold_font.configure(weight="bold")
        self.italic_font = font.Font(self.text, self.text.cget("font"))
        self.italic_font.configure(slant="italic")
        self.underline_font = font.Font(self.text, self.text.cget("font"))
        self.underline_font.configure(underline=1)

        # Balises pour la mise en forme
        self.text.tag_configure("title", font=self.title_font, foreground="#1a237e")
        self.text.tag_configure("subtitle", font=self.subtitle_font, foreground="#3949ab")
        self.text.tag_configure("bold", font=self.bold_font)
        self.text.tag_configure("italic", font=self.italic_font)
        self.text.tag_configure("underline", font=self.underline_font)
        self.text.tag_configure("highlight", background="#fff59d")

        # Raccourcis clavier
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-b>", lambda event: self.set_bold())
        self.root.bind("<Control-i>", lambda event: self.set_italic())
        self.root.bind("<Control-u>", lambda event: self.set_underline())

        self.current_file = None

    def create_home_toolbar(self):
        for widget in self.toolbar.winfo_children():
            widget.destroy()
        tk.Label(self.toolbar, text="Style :", bg="#ffffff", font=("Arial", 10, "bold")).pack(side="left", padx=(8,5))
        tk.Button(self.toolbar, text="Titre", command=self.set_title).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Sous-titre", command=self.set_subtitle).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Gras", command=self.set_bold).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Italique", command=self.set_italic).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Souligné", command=self.set_underline).pack(side="left", padx=2, pady=2)

    def create_insert_toolbar(self):
        for widget in self.toolbar.winfo_children():
            widget.destroy()
        tk.Label(self.toolbar, text="Insertion :", bg="#ffffff", font=("Arial", 10, "bold")).pack(side="left", padx=(8,5))
        tk.Button(self.toolbar, text="Image", state="disabled").pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Tableau", state="disabled").pack(side="left", padx=2, pady=2)

    def create_help_toolbar(self):
        for widget in self.toolbar.winfo_children():
            widget.destroy()
        tk.Button(self.toolbar, text="Github du projet", command=self.open_github_url).pack(side="left", padx=2, pady=2)

    def create_file_toolbar(self):
        for widget in self.toolbar.winfo_children():
            widget.destroy()
        tk.Button(self.toolbar, text="Nouveau", command=self.new_file).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Ouvrir...", command=self.open_file).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Enregistrer", command=self.save_file).pack(side="left", padx=2, pady=2)

    def create_other_toolbar(self):
        for widget in self.toolbar.winfo_children():
            widget.destroy()
        tk.Button(self.toolbar, text="Mettre à jour", command=self.update_from_github).pack(side="left", padx=2, pady=2)
        tk.Button(self.toolbar, text="Quitter", command=quit).pack(side="left", padx=2, pady=2)

    def update_toolbar(self):
        tab = self.current_tab.get()
        if tab == "Accueil":
            self.create_home_toolbar()
        elif tab == "Insertion":
            self.create_insert_toolbar()
        elif tab == "Aide":
            self.create_help_toolbar()
        elif tab == "Fichier":
            self.create_file_toolbar()
        elif tab == "Autres":
            self.create_other_toolbar()

    def new_file(self):
        self.text.delete(1.0, tk.END)
        self.current_file = None
        self.update_section_list()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MonTexteEditor", "*.mte"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.text.delete(1.0, tk.END)
                    self.text.insert(1.0, data.get("text", ""))
                    for tag in ["title", "subtitle", "bold", "italic", "underline"]:
                        self.text.tag_remove(tag, "1.0", tk.END)
                    for tagdata in data.get("tags", []):
                        tag = tagdata["tag"]
                        start = tagdata["start"]
                        end = tagdata["end"]
                        self.text.tag_add(tag, start, end)
                    self.current_file = file_path
                    self.update_section_list()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier :\n{e}")

    def save_file(self):
        file_path = self.current_file
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mte",
                filetypes=[("MonTexteEditor", "*.mte"), ("Tous les fichiers", "*.*")]
            )
        if file_path:
            text_content = self.text.get("1.0", tk.END)
            tags_data = []
            for tag in ["title", "subtitle", "bold", "italic", "underline"]:
                ranges = self.text.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    start = str(ranges[i])
                    end = str(ranges[i+1])
                    tags_data.append({"tag": tag, "start": start, "end": end})
            data = {
                "text": text_content,
                "tags": tags_data
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.current_file = file_path
            messagebox.showinfo("Enregistrement", "Fichier enregistré avec succès.")

    def set_title(self):
        try:
            start, end = self.text.tag_ranges("sel")
            self.text.tag_add("title", start, end)
            self.text.tag_remove("subtitle", start, end)
            self.update_section_list()
        except ValueError:
            messagebox.showwarning("Sélection", "Sélectionnez le texte à mettre en titre.")

    def set_subtitle(self):
        try:
            start, end = self.text.tag_ranges("sel")
            self.text.tag_add("subtitle", start, end)
            self.text.tag_remove("title", start, end)
            self.update_section_list()
        except ValueError:
            messagebox.showwarning("Sélection", "Sélectionnez le texte à mettre en sous-titre.")

    def set_bold(self):
        try:
            start, end = self.text.tag_ranges("sel")
            self.text.tag_add("bold", start, end)
        except ValueError:
            messagebox.showwarning("Sélection", "Sélectionnez le texte à mettre en gras.")

    def set_italic(self):
        try:
            start, end = self.text.tag_ranges("sel")
            self.text.tag_add("italic", start, end)
        except ValueError:
            messagebox.showwarning("Sélection", "Sélectionnez le texte à mettre en italique.")

    def set_underline(self):
        try:
            start, end = self.text.tag_ranges("sel")
            self.text.tag_add("underline", start, end)
        except ValueError:
            messagebox.showwarning("Sélection", "Sélectionnez le texte à souligner.")

    def update_section_list(self, event=None):
        self.section_listbox.delete(0, tk.END)
        for tag in ("title", "subtitle"):
            ranges = self.text.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                line = int(str(start).split('.')[0])
                content = self.text.get(start, end).strip()
                if content:
                    label = f"{'Titre' if tag=='title' else 'Sous-titre'} : {content} (Ligne {line})"
                    self.section_listbox.insert(tk.END, label)
                    self.section_listbox.itemconfig(tk.END, {'bg':'#e8eaf6' if tag=='title' else '#f3e5f5'})
        self.text.edit_modified(False)

    def go_to_section(self, event):
        self.text.tag_remove("highlight", "1.0", tk.END)
        selected = self.section_listbox.curselection()
        if selected:
            label = self.section_listbox.get(selected[0])
            tag = "title" if "Titre" in label else "subtitle"
            search_text = label.split(": ", 1)[1].rsplit(" (Ligne", 1)[0]
            ranges = self.text.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                content = self.text.get(start, end).strip()
                if content == search_text:
                    self.text.see(start)
                    self.text.tag_add("highlight", start, end)
                    self.root.after(1000, lambda: self.text.tag_remove("highlight", start, end))
                    break

    def on_text_change(self, event=None):
        if self.text.edit_modified():
            self.update_section_list()

    def open_github_url(self):
        import webbrowser
        webbrowser.open("https://github.com/codeartemis37/word-maison")

    def update_from_github(self):
        url = "https://raw.githubusercontent.com/codeartemis37/word-maison/main/notepad.py"
        local_path = os.path.abspath(sys.argv[0])
        backup_path = local_path + ".bak"
        try:
            with open(local_path, "rb") as f:
                content = f.read()
            with open(backup_path, "wb") as f:
                f.write(content)
        except Exception as e:
            messagebox.showwarning("Sauvegarde", f"Impossible de sauvegarder le fichier actuel : {e}")

        try:
            response = urllib.request.urlopen(url)
            new_code = response.read()
            with open(local_path, "wb") as f:
                f.write(new_code)
            # Suppression du .bak après mise à jour réussie
            try:
                os.remove(backup_path)
            except Exception:
                pass
            messagebox.showinfo("Mise à jour", "Mise à jour réussie !\nRedémarrez l'application.")
        except Exception as e:
            messagebox.showerror("Erreur de mise à jour", f"Erreur lors de la mise à jour :\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    editor = SimpleTextEditor(root)
    root.mainloop()
