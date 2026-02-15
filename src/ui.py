import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import ttkbootstrap as tb
from audio_engine import AudioEngine
from preset_manager import PresetManager

class BinauralBeatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binaural Beat Generator 0.9.0")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.audio_engine = AudioEngine()
        self.preset_manager = PresetManager()

        # Load theme
        initial_theme = self.preset_manager.get_theme()
        if initial_theme:
            self.root.style.theme_use(initial_theme)

        self.setup_menu()
        self.create_widgets()

        # Start update loop
        self.update_live_status()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        settings_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="About", command=self.show_about)

        user_profile_menu = tk.Menu(settings_menu, tearoff=False)
        settings_menu.add_cascade(label="User Profile", menu=user_profile_menu)
        user_profile_menu.add_command(label="Import User Profile", command=self.import_config_json)
        user_profile_menu.add_command(label="Export User Profile", command=self.export_config_json)

        theme_menu = tk.Menu(settings_menu, tearoff=False)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Dark (Darkly)", command=lambda: self.set_theme("darkly"))
        theme_menu.add_command(label="Dark (Superhero)", command=lambda: self.set_theme("superhero"))
        theme_menu.add_command(label="Light (Flatly)", command=lambda: self.set_theme("flatly"))

    def create_widgets(self):
        # Main layout: Left (Audio Controls), Right (Presets & Extras)
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_column = ttk.Frame(main_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_column = ttk.Frame(main_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left Column ---

        # Frequency Controls
        freq_frame = ttk.Frame(left_column)
        freq_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_frequency_controls(freq_frame)

        # Ramp Controls
        self.create_ramp_controls(left_column)

        # Noise Controls
        self.create_noise_controls(left_column)

        # Timer Controls
        self.create_timer_controls(left_column)

        # Playback Controls
        playback_frame = ttk.Frame(left_column)
        playback_frame.pack(fill=tk.X, pady=10)

        self.generate_button = ttk.Button(playback_frame, text="Generate Beat", command=self.play_audio, bootstyle="success")
        self.generate_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.stop_button = ttk.Button(playback_frame, text="Stop", command=self.stop_audio, bootstyle="danger")
        self.stop_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        # Status Bar
        self.status_var = tk.StringVar(value="Beat: — Hz | L: — Hz | R: — Hz")
        self.status_label = ttk.Label(left_column, textvariable=self.status_var, bootstyle="info")
        self.status_label.pack(fill=tk.X, pady=5)

        # --- Right Column ---

        # Presets
        self.create_presets_ui(right_column)


    def create_frequency_controls(self, parent):
        # Validation command
        vcmd = (self.root.register(self.validate_float), '%P')

        # Left Ear
        left_frame = ttk.LabelFrame(parent, text="Left Ear Frequency (Hz)")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="Frequency:").grid(row=0, column=0, padx=5, pady=5)
        self.left_freq_entry = ttk.Entry(left_frame, validate="key", validatecommand=vcmd)
        self.left_freq_entry.grid(row=0, column=1, padx=5, pady=5)
        self.left_freq_entry.insert(0, "432")

        ttk.Label(left_frame, text="Volume (%):").grid(row=1, column=0, padx=5, pady=5)
        self.left_vol_entry = ttk.Entry(left_frame, validate="key", validatecommand=vcmd)
        self.left_vol_entry.grid(row=1, column=1, padx=5, pady=5)
        self.left_vol_entry.insert(0, "50")

        ttk.Label(left_frame, text="Waveform:").grid(row=2, column=0, padx=5, pady=5)
        self.left_wave_var = tk.StringVar(value="Sine")
        self.left_wave_combo = ttk.Combobox(left_frame, textvariable=self.left_wave_var, values=["Sine", "Square", "Sawtooth"], state="readonly")
        self.left_wave_combo.grid(row=2, column=1, padx=5, pady=5)

        # Right Ear
        right_frame = ttk.LabelFrame(parent, text="Right Ear Frequency (Hz)")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="Frequency:").grid(row=0, column=0, padx=5, pady=5)
        self.right_freq_entry = ttk.Entry(right_frame, validate="key", validatecommand=vcmd)
        self.right_freq_entry.grid(row=0, column=1, padx=5, pady=5)
        self.right_freq_entry.insert(0, "432")

        ttk.Label(right_frame, text="Volume (%):").grid(row=1, column=0, padx=5, pady=5)
        self.right_vol_entry = ttk.Entry(right_frame, validate="key", validatecommand=vcmd)
        self.right_vol_entry.grid(row=1, column=1, padx=5, pady=5)
        self.right_vol_entry.insert(0, "50")

        ttk.Label(right_frame, text="Waveform:").grid(row=2, column=0, padx=5, pady=5)
        self.right_wave_var = tk.StringVar(value="Sine")
        self.right_wave_combo = ttk.Combobox(right_frame, textvariable=self.right_wave_var, values=["Sine", "Square", "Sawtooth"], state="readonly")
        self.right_wave_combo.grid(row=2, column=1, padx=5, pady=5)

    def create_ramp_controls(self, parent):
        vcmd = (self.root.register(self.validate_float), '%P')

        ramp_frame = ttk.LabelFrame(parent, text="Binaural Ramp")
        ramp_frame.pack(fill=tk.X, pady=10)

        self.ramp_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(ramp_frame, text="Enable Ramp", variable=self.ramp_enabled_var, command=self.toggle_ramp_ui).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        ttk.Label(ramp_frame, text="Carrier (Hz):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.carrier_entry = ttk.Entry(ramp_frame, validate="key", validatecommand=vcmd)
        self.carrier_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.carrier_entry.insert(0, "432")

        ttk.Label(ramp_frame, text="Start beat (Hz):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.start_beat_entry = ttk.Entry(ramp_frame, validate="key", validatecommand=vcmd)
        self.start_beat_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.start_beat_entry.insert(0, "20")

        ttk.Label(ramp_frame, text="End beat (Hz):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.end_beat_entry = ttk.Entry(ramp_frame, validate="key", validatecommand=vcmd)
        self.end_beat_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.end_beat_entry.insert(0, "3")

        ttk.Label(ramp_frame, text="Duration (min):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.ramp_minutes_entry = ttk.Entry(ramp_frame, validate="key", validatecommand=vcmd)
        self.ramp_minutes_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.ramp_minutes_entry.insert(0, "30")

    def toggle_ramp_ui(self):
        state = "normal" if self.ramp_enabled_var.get() else "disabled"
        # self.carrier_entry.config(state=state)
        # self.start_beat_entry.config(state=state)
        # self.end_beat_entry.config(state=state)
        # self.ramp_minutes_entry.config(state=state)
        pass # ttkbootstrap specific styling handles this visually usually, or just leave enabled

    def create_noise_controls(self, parent):
        noise_frame = ttk.LabelFrame(parent, text="Background Noise")
        noise_frame.pack(fill=tk.X, pady=10)

        ttk.Label(noise_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.noise_type_var = tk.StringVar(value="None")
        self.noise_type_combo = ttk.Combobox(noise_frame, textvariable=self.noise_type_var, values=["None", "White", "Pink", "Brown"], state="readonly")
        self.noise_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(noise_frame, text="Volume (%):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.noise_vol_scale = ttk.Scale(noise_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.noise_vol_scale.set(10)
        self.noise_vol_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    def create_timer_controls(self, parent):
        timer_frame = ttk.LabelFrame(parent, text="Auto Stop Timer")
        timer_frame.pack(fill=tk.X, pady=10)

        vcmd = (self.root.register(self.validate_float), '%P')

        ttk.Label(timer_frame, text="Stop after (min):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.timer_entry = ttk.Entry(timer_frame, width=10, validate="key", validatecommand=vcmd)
        self.timer_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.timer_entry.insert(0, "0")
        ttk.Label(timer_frame, text="(0 = disabled)").grid(row=0, column=2, padx=5, pady=5, sticky="w")

    def create_presets_ui(self, parent):
        presets_frame = ttk.LabelFrame(parent, text="Presets")
        presets_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tabbed interface for presets? Or just scrollable?
        # Let's use tabs for Monaural / Binaural
        notebook = ttk.Notebook(presets_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.monaural_frame = ttk.Frame(notebook)
        notebook.add(self.monaural_frame, text="Monaural")

        self.binaural_frame = ttk.Frame(notebook)
        notebook.add(self.binaural_frame, text="Binaural")

        # Create Preset Area
        create_frame = ttk.LabelFrame(presets_frame, text="User Presets")
        create_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(create_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.preset_name_entry = ttk.Entry(create_frame)
        self.preset_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(create_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.preset_cat_var = tk.StringVar(value="Binaural")
        self.preset_cat_combo = ttk.Combobox(create_frame, textvariable=self.preset_cat_var, values=["Binaural", "Monaural"], state="readonly")
        self.preset_cat_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        save_btn = ttk.Button(create_frame, text="Save Current Settings", command=self.save_preset)
        save_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Manage User Presets
        manage_frame = ttk.LabelFrame(presets_frame, text="Manage User Presets")
        manage_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(manage_frame, text="Select Preset:").pack(padx=5, pady=2)
        self.user_preset_var = tk.StringVar()
        self.user_preset_combo = ttk.Combobox(manage_frame, textvariable=self.user_preset_var, state="readonly")
        self.user_preset_combo.pack(fill=tk.X, padx=5, pady=2)

        del_btn = ttk.Button(manage_frame, text="Delete Selected Preset", command=self.delete_preset, bootstyle="danger-outline")
        del_btn.pack(fill=tk.X, padx=5, pady=5)

        self.refresh_presets()

    def refresh_presets(self):
        # Clear existing buttons
        for widget in self.monaural_frame.winfo_children():
            widget.destroy()
        for widget in self.binaural_frame.winfo_children():
            widget.destroy()

        all_presets = self.preset_manager.get_all_presets()

        # Monaural
        for i, p in enumerate(all_presets["Monaural"]):
            btn = ttk.Button(
                self.monaural_frame,
                text=p["label"],
                command=lambda l=p["left_hz"], r=p["right_hz"]: self.apply_preset(l, r)
            )
            btn.pack(fill=tk.X, padx=5, pady=2)

        # Binaural
        for i, p in enumerate(all_presets["Binaural"]):
            btn = ttk.Button(
                self.binaural_frame,
                text=p["label"],
                command=lambda l=p["left_hz"], r=p["right_hz"]: self.apply_preset(l, r)
            )
            btn.pack(fill=tk.X, padx=5, pady=2)

        # Update User Presets Combo
        user_presets = self.preset_manager.get_user_presets()
        # Flatten list for combo: "Category: Label"
        combo_values = []
        for cat in ["Monaural", "Binaural"]:
            for p in user_presets.get(cat, []):
                combo_values.append(f"{cat}: {p['label']}")
        self.user_preset_combo['values'] = combo_values
        if combo_values:
            self.user_preset_combo.current(0)
        else:
            self.user_preset_combo.set("")


    def apply_preset(self, left_hz, right_hz):
        self.left_freq_entry.delete(0, tk.END)
        self.left_freq_entry.insert(0, str(left_hz))
        self.right_freq_entry.delete(0, tk.END)
        self.right_freq_entry.insert(0, str(right_hz))

    def save_preset(self):
        name = self.preset_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a preset name.")
            return

        try:
            left_hz = float(self.left_freq_entry.get())
            right_hz = float(self.right_freq_entry.get())
            category = self.preset_cat_var.get()

            self.preset_manager.add_user_preset(category, name, left_hz, right_hz)
            self.preset_name_entry.delete(0, tk.END)
            self.refresh_presets()
            messagebox.showinfo("Success", f"Preset '{name}' saved.")
        except ValueError:
            messagebox.showerror("Error", "Invalid frequency values.")

    def delete_preset(self):
        selection = self.user_preset_var.get()
        if not selection:
            return

        try:
            category, label = selection.split(": ", 1)
            if messagebox.askyesno("Confirm", f"Delete preset '{label}'?"):
                if self.preset_manager.remove_user_preset(category, label):
                    self.refresh_presets()
                    messagebox.showinfo("Success", "Preset deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def validate_float(self, new_value):
        if new_value == "": return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    def play_audio(self):
        try:
            left_hz = float(self.left_freq_entry.get())
            right_hz = float(self.right_freq_entry.get())
            left_vol = float(self.left_vol_entry.get()) / 100.0
            right_vol = float(self.right_vol_entry.get()) / 100.0
            left_wave = self.left_wave_var.get()
            right_wave = self.right_wave_var.get()

            use_ramp = self.ramp_enabled_var.get()
            ramp_carrier = float(self.carrier_entry.get())
            ramp_start = float(self.start_beat_entry.get())
            ramp_end = float(self.end_beat_entry.get())
            ramp_mins = float(self.ramp_minutes_entry.get())

            noise_type = self.noise_type_var.get()
            noise_vol = self.noise_vol_scale.get() / 100.0 # scale 0-100 -> 0.0-1.0

            # Timer
            timer_mins = float(self.timer_entry.get())
            if timer_mins > 0:
                self.stop_time = time.time() + timer_mins * 60.0
            else:
                self.stop_time = 0

            self.audio_engine.start(
                left_hz=left_hz,
                right_hz=right_hz,
                left_vol=left_vol,
                right_vol=right_vol,
                left_waveform=left_wave,
                right_waveform=right_wave,
                use_ramp=use_ramp,
                ramp_carrier_hz=ramp_carrier,
                ramp_start_beat_hz=ramp_start,
                ramp_end_beat_hz=ramp_end,
                ramp_duration_s=ramp_mins * 60.0,
                noise_type=noise_type,
                noise_vol=noise_vol
            )

            # Update frequency display for ramp mode
            if use_ramp:
                 self.left_freq_entry.delete(0, tk.END)
                 self.right_freq_entry.delete(0, tk.END)
                 self.left_freq_entry.insert(0, f"{ramp_carrier - ramp_start/2:.2f}")
                 self.right_freq_entry.insert(0, f"{ramp_carrier + ramp_start/2:.2f}")

        except ValueError:
            messagebox.showerror("Error", "Invalid input values. Please check frequencies and volumes.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_audio(self):
        self.audio_engine.stop()
        self.stop_time = 0

    def update_live_status(self):
        if not self.root.winfo_exists():
            return

        status = self.audio_engine.get_status()
        if status:
            beat = status["beat_hz"]
            lf = status["left_hz"]
            rf = status["right_hz"]

            # Check timer
            if self.stop_time > 0 and time.time() >= self.stop_time:
                self.stop_audio()
                self.status_var.set("Timer Expired. Stopped.")
            else:
                msg = f"Beat: {beat:.2f} Hz | L: {lf:.2f} Hz | R: {rf:.2f} Hz"

                if status["is_ramp"]:
                    remaining = max(0, status["ramp_duration"] - status["elapsed"])
                    rem_m = int(remaining // 60)
                    rem_s = int(remaining % 60)
                    msg += f" | Ramp Remaining: {rem_m:02d}:{rem_s:02d}"

                if self.stop_time > 0:
                    timer_rem = max(0, self.stop_time - time.time())
                    tm = int(timer_rem // 60)
                    ts = int(timer_rem % 60)
                    msg += f" | Timer: {tm:02d}:{ts:02d}"

                self.status_var.set(msg)
        else:
            self.status_var.set("Beat: — Hz | L: — Hz | R: — Hz")

        self.root.after(200, self.update_live_status)

    def set_theme(self, theme_name):
        try:
            self.root.style.theme_use(theme_name)
            self.preset_manager.set_theme(theme_name)
        except Exception as e:
            messagebox.showerror("Theme Error", str(e))

    def show_about(self):
        about_text = """
Binaural Beat Generator 0.9.0

Features:
- Binaural & Monaural Beats
- Ramp Mode
- Background Noise (White/Pink/Brown)
- Timer
- Presets

Licensed under GPL-3.0.
"""
        messagebox.showinfo("About", about_text)

    def import_config_json(self):
        try:
            in_path = filedialog.askopenfilename(
                title="Import config.json",
                filetypes=[("JSON files", "*.json")],
            )
            if in_path:
                self.preset_manager.import_config(in_path)

                # Apply theme
                theme = self.preset_manager.get_theme()
                if theme:
                    self.root.style.theme_use(theme)

                self.refresh_presets()
                messagebox.showinfo("Import", "Configuration imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def export_config_json(self):
        try:
            out_path = filedialog.asksaveasfilename(
                title="Export config.json",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile="config.json",
            )
            if out_path:
                self.preset_manager.export_config(out_path)
                messagebox.showinfo("Export", "Configuration exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def on_close(self):
        self.stop_audio()
        self.root.destroy()
