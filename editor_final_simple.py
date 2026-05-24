#!/usr/bin/env python3
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import random

class FinalSimpleEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PvZ Editor")
        self.root.geometry("1400x850")
        self.root.configure(bg='#1a1a2e')
        
        with open('manifest.json', 'r') as f:
            self.manifest = json.load(f)
        
        self.all_plants = list(self.manifest.get('plants', {}).keys())
        self.all_zombies = [z for z in self.manifest.get('zombies', {}).keys() if z != 'your_death']
        
        self.current_wave = []
        self.level_waves = []
        self.selected_plants = []
        
        self.create_ui()
        self.update_plant_lists()
        self.load_levels()
        self.setup_wave_drag_drop()
    
    def create_ui(self):
        top = tk.Frame(self.root, bg='#e94560', height=45)
        top.pack(fill='x')
        top.pack_propagate(False)
        tk.Label(top, text="🌱 PvZ DESKTOP EDITOR 🧟", 
                 font=('Arial', 14, 'bold'), bg='#e94560', fg='white').pack(expand=True)
        
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ========== ЛЕВАЯ ПАНЕЛЬ ==========
        left = tk.Frame(main, bg='#2a2a3e', width=450)
        left.pack(side='left', fill='both', expand=True)
        left.pack_propagate(False)
        
        # ПАРАМЕТРЫ УРОВНЯ
        params = tk.LabelFrame(left, text="📝 ПАРАМЕТРЫ УРОВНЯ", bg='#2a2a3e', fg='#ffd700')
        params.pack(fill='x', padx=10, pady=5)
        
        pf = tk.Frame(params, bg='#2a2a3e')
        pf.pack(padx=10, pady=8)
        
        tk.Label(pf, text="НАЗВАНИЕ:", bg='#2a2a3e', fg='white').grid(row=0, column=0, sticky='w')
        self.name_entry = tk.Entry(pf, bg='#1a1a2e', fg='#ffd700', width=28)
        self.name_entry.grid(row=0, column=1, padx=10)
        
        tk.Label(pf, text="СТАРТ. СОЛНЦЕ:", bg='#2a2a3e', fg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.sun_entry = tk.Entry(pf, bg='#1a1a2e', fg='#ffd700', width=10)
        self.sun_entry.insert(0, "150")
        self.sun_entry.grid(row=1, column=1, sticky='w')
        
        self.night_var = tk.BooleanVar()
        tk.Checkbutton(pf, text="🌙 НОЧНОЙ РЕЖИМ", variable=self.night_var,
                       bg='#2a2a3e', fg='#8888ff', selectcolor='#2a2a3e').grid(row=2, column=1, sticky='w')
        
        # РАСТЕНИЯ
        plants_frame = tk.LabelFrame(left, text="🌱 РАСТЕНИЯ ДЛЯ УРОВНЯ", bg='#2a2a3e', fg='#4ecdc4')
        plants_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(plants_frame, text="Доступные растения:", bg='#2a2a3e', fg='#aaa').pack(anchor='w', padx=10)
        
        avail_frame = tk.Frame(plants_frame, bg='#2a2a3e')
        avail_frame.pack(fill='x', padx=10, pady=5)
        
        scroll_avail = tk.Scrollbar(avail_frame)
        scroll_avail.pack(side='right', fill='y')
        
        self.avail_plants = tk.Listbox(avail_frame, bg='#1a1a2e', fg='#4ecdc4', 
                                        height=5, yscrollcommand=scroll_avail.set)
        self.avail_plants.pack(side='left', fill='both', expand=True)
        scroll_avail.config(command=self.avail_plants.yview)
        
        plant_btns = tk.Frame(plants_frame, bg='#2a2a3e')
        plant_btns.pack(pady=5)
        tk.Button(plant_btns, text="→ ДОБАВИТЬ ВЫБРАННОЕ", command=self.add_plant,
                  bg='#4ecdc4', fg='#1a1a2e').pack(side='left', padx=5)
        tk.Button(plant_btns, text="→ ДОБАВИТЬ ВСЕ", command=self.add_all_plants,
                  bg='#27ae60', fg='white').pack(side='left', padx=5)
        
        tk.Label(plants_frame, text="Выбранные (будут в уровне):", bg='#2a2a3e', fg='#ffd700').pack(anchor='w', padx=10)
        
        sel_frame = tk.Frame(plants_frame, bg='#2a2a3e')
        sel_frame.pack(fill='x', padx=10, pady=5)
        
        scroll_sel = tk.Scrollbar(sel_frame)
        scroll_sel.pack(side='right', fill='y')
        
        self.sel_plants = tk.Listbox(sel_frame, bg='#1a1a2e', fg='#ffd700', 
                                      height=4, yscrollcommand=scroll_sel.set)
        self.sel_plants.pack(side='left', fill='both', expand=True)
        scroll_sel.config(command=self.sel_plants.yview)
        
        rem_btns = tk.Frame(plants_frame, bg='#2a2a3e')
        rem_btns.pack(pady=5)
        tk.Button(rem_btns, text="← УДАЛИТЬ ВЫБРАННОЕ", command=self.remove_plant,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        tk.Button(rem_btns, text="❌ ОЧИСТИТЬ ВСЕ", command=self.clear_plants,
                  bg='#e67e22', fg='white').pack(side='left', padx=5)
        
        # СОХРАНЁННЫЕ УРОВНИ
        levels_frame = tk.LabelFrame(left, text="📁 СОХРАНЁННЫЕ УРОВНИ", bg='#2a2a3e', fg='#ffd700')
        levels_frame.pack(fill='x', padx=10, pady=5)
        
        levels_list_frame = tk.Frame(levels_frame, bg='#2a2a3e')
        levels_list_frame.pack(fill='x', padx=10, pady=5)
        
        scroll_levels = tk.Scrollbar(levels_list_frame)
        scroll_levels.pack(side='right', fill='y')
        
        self.levels_list = tk.Listbox(levels_list_frame, bg='#1a1a2e', fg='#ffd700', 
                                       height=6, yscrollcommand=scroll_levels.set)
        self.levels_list.pack(side='left', fill='both', expand=True)
        scroll_levels.config(command=self.levels_list.yview)
        
        level_btns = tk.Frame(levels_frame, bg='#2a2a3e')
        level_btns.pack(pady=5)
        tk.Button(level_btns, text="📂 ЗАГРУЗИТЬ", command=self.load_level,
                  bg='#4ecdc4', fg='#1a1a2e').pack(side='left', padx=5)
        tk.Button(level_btns, text="🗑 УДАЛИТЬ", command=self.delete_level,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        
        # ========== ПРАВАЯ ПАНЕЛЬ - ВОЛНЫ ==========
        right = tk.Frame(main, bg='#2a2a3e', width=750)
        right.pack(side='right', fill='both', expand=True)
        right.pack_propagate(False)
        
        # ДОБАВЛЕНИЕ ЗОМБИ
        add_frame = tk.LabelFrame(right, text="➕ ДОБАВИТЬ ЗОМБИ В ВОЛНУ", bg='#2a2a3e', fg='#ffd700')
        add_frame.pack(fill='x', padx=10, pady=5)
        
        af = tk.Frame(add_frame, bg='#2a2a3e')
        af.pack(pady=8)
        
        tk.Label(af, text="Тип:", bg='#2a2a3e', fg='white').pack(side='left')
        self.zombie_type = ttk.Combobox(af, values=self.all_zombies, width=20)
        self.zombie_type.pack(side='left', padx=5)
        
        tk.Label(af, text="Ряд:", bg='#2a2a3e', fg='white').pack(side='left', padx=10)
        self.row_spin = tk.Spinbox(af, from_=1, to=5, width=4)
        self.row_spin.pack(side='left', padx=5)
        
        tk.Label(af, text="Задержка (мс):", bg='#2a2a3e', fg='white').pack(side='left', padx=10)
        self.delay_entry = tk.Entry(af, width=8)
        self.delay_entry.insert(0, "0")
        self.delay_entry.pack(side='left', padx=5)
        
        tk.Button(af, text="➕ ДОБАВИТЬ", command=self.add_zombie,
                  bg='#2d6a2d', fg='white').pack(side='left', padx=5)
        
        # ===== НОВАЯ КНОПКА 🎲 С ПОЛЕМ ВВОДА КОЛИЧЕСТВА =====
        random_frame = tk.Frame(af, bg='#2a2a3e')
        random_frame.pack(side='left', padx=10)
        
        tk.Label(random_frame, text="🎲 x", bg='#2a2a3e', fg='#ffd700', font=('Arial', 10, 'bold')).pack(side='left')
        self.random_count = tk.Spinbox(random_frame, from_=1, to=50, width=3)
        self.random_count.pack(side='left', padx=2)
        tk.Button(random_frame, text="РАНДОМНЫХ", command=self.add_random_zombies,
                  bg='#9b59b6', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=2)
        
        # Быстрые кнопки
        quick = tk.Frame(add_frame, bg='#2a2a3e')
        quick.pack(pady=5)
        tk.Button(quick, text="👑 БОСС", command=self.add_boss,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        tk.Button(quick, text="🗑 ОЧИСТИТЬ ВОЛНУ", command=self.clear_wave,
                  bg='#e67e22', fg='white').pack(side='left', padx=5)
        
        # ТЕКУЩАЯ ВОЛНА
        current_frame = tk.LabelFrame(right, text="📋 ТЕКУЩАЯ ВОЛНА", bg='#2a2a3e', fg='#4ecdc4')
        current_frame.pack(fill='x', padx=10, pady=5)
        
        cur_list_frame = tk.Frame(current_frame, bg='#2a2a3e')
        cur_list_frame.pack(fill='x', padx=10, pady=5)
        
        scroll_cur = tk.Scrollbar(cur_list_frame)
        scroll_cur.pack(side='right', fill='y')
        
        self.current_list = tk.Listbox(cur_list_frame, bg='#1a1a2e', fg='#4ecdc4', 
                                        height=6, yscrollcommand=scroll_cur.set,
                                        selectmode='extended')
        self.current_list.pack(side='left', fill='both', expand=True)
        scroll_cur.config(command=self.current_list.yview)
        
        # Кнопки для текущей волны
        cur_btns = tk.Frame(current_frame, bg='#2a2a3e')
        cur_btns.pack(pady=5)
        tk.Button(cur_btns, text="❌ УДАЛИТЬ ВЫБРАННЫХ", command=self.remove_selected,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        tk.Button(cur_btns, text="🎲 ЗАМЕНИТЬ ВЫБРАННЫХ НА РАНДОМНЫХ", command=self.replace_selected,
                  bg='#9b59b6', fg='white').pack(side='left', padx=5)
        
        # Замена по типу
        replace_frame = tk.Frame(current_frame, bg='#2a2a3e')
        replace_frame.pack(pady=5)
        tk.Label(replace_frame, text="Заменить ВСЕХ зомби типа:", bg='#2a2a3e', fg='#aaa').pack(side='left')
        self.replace_type = ttk.Combobox(replace_frame, values=self.all_zombies, width=18)
        self.replace_type.pack(side='left', padx=5)
        tk.Button(replace_frame, text="🔄 ЗАМЕНИТЬ ВСЕХ", command=self.replace_all_of_type,
                  bg='#f39c12', fg='white').pack(side='left', padx=5)
        
        # Сохранение волны
        tk.Button(current_frame, text="💾 СОХРАНИТЬ ВОЛНУ", command=self.save_wave,
                  bg='#3498db', fg='white', font=('Arial', 11, 'bold')).pack(fill='x', padx=10, pady=5)
        
        # СПИСОК ВОЛН (с перетаскиванием)
        waves_frame = tk.LabelFrame(right, text="📋 СОЗДАННЫЕ ВОЛНЫ (перетаскивайте мышкой)", 
                                     bg='#2a2a3e', fg='#ffd700')
        waves_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        waves_list_frame = tk.Frame(waves_frame, bg='#2a2a3e')
        waves_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scroll_waves = tk.Scrollbar(waves_list_frame)
        scroll_waves.pack(side='right', fill='y')
        
        self.waves_list = tk.Listbox(waves_list_frame, bg='#1a1a2e', fg='#ffd700', 
                                      height=8, yscrollcommand=scroll_waves.set)
        self.waves_list.pack(side='left', fill='both', expand=True)
        scroll_waves.config(command=self.waves_list.yview)
        
        # Кнопки для волн
        waves_btns = tk.Frame(waves_frame, bg='#2a2a3e')
        waves_btns.pack(pady=5)
        tk.Button(waves_btns, text="✏ РЕДАКТИРОВАТЬ", command=self.edit_wave,
                  bg='#2d6a2d', fg='white').pack(side='left', padx=5)
        tk.Button(waves_btns, text="🗑 УДАЛИТЬ", command=self.delete_wave,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        
        # Сохранение уровня
        tk.Button(right, text="💾 СОХРАНИТЬ УРОВЕНЬ", command=self.save_level,
                  bg='#e94560', fg='white', font=('Arial', 14, 'bold')).pack(pady=10, padx=10, fill='x')
    
    def add_random_zombies(self):
        """Добавляет N случайных зомби (без всплывающих окон)"""
        try:
            count = int(self.random_count.get())
        except:
            count = 1
        
        for _ in range(count):
            ztype = random.choice(self.all_zombies)
            row = random.randint(1, 5)
            delay = random.randint(0, 5000)
            self.current_wave.append({"type": ztype, "row": row, "delay": delay})
        
        self.current_wave.sort(key=lambda x: x['delay'])
        self.update_current_display()
    
    def setup_wave_drag_drop(self):
        self.waves_list.bind('<Button-1>', self.on_drag_start)
        self.waves_list.bind('<B1-Motion>', self.on_drag_motion)
        self.waves_list.bind('<ButtonRelease-1>', self.on_drag_end)
    
    def on_drag_start(self, event):
        self.drag_start = self.waves_list.nearest(event.y)
    
    def on_drag_motion(self, event):
        if hasattr(self, 'drag_start') and self.drag_start is not None:
            new = self.waves_list.nearest(event.y)
            if new != self.drag_start:
                wave = self.level_waves.pop(self.drag_start)
                self.level_waves.insert(new, wave)
                self.update_waves_display()
                self.drag_start = new
    
    def on_drag_end(self, event):
        self.drag_start = None
    
    def update_plant_lists(self):
        self.avail_plants.delete(0, tk.END)
        for p in self.all_plants:
            self.avail_plants.insert(tk.END, p)
    
    def add_plant(self):
        sel = self.avail_plants.curselection()
        if sel:
            p = self.avail_plants.get(sel[0])
            if p not in self.selected_plants:
                self.selected_plants.append(p)
                self.sel_plants.insert(tk.END, p)
    
    def add_all_plants(self):
        self.selected_plants = self.all_plants.copy()
        self.sel_plants.delete(0, tk.END)
        for p in self.selected_plants:
            self.sel_plants.insert(tk.END, p)
    
    def remove_plant(self):
        sel = self.sel_plants.curselection()
        if sel:
            self.selected_plants.pop(sel[0])
            self.sel_plants.delete(sel[0])
    
    def clear_plants(self):
        self.selected_plants = []
        self.sel_plants.delete(0, tk.END)
    
    def add_zombie(self):
        t = self.zombie_type.get()
        if not t:
            return
        r = int(self.row_spin.get())
        d = int(self.delay_entry.get() or 0)
        self.current_wave.append({"type": t, "row": r, "delay": d})
        self.update_current_display()
    
    def add_boss(self):
        self.current_wave.append({"type": "your_death", "row": 3, "delay": 0})
        self.update_current_display()
    
    def clear_wave(self):
        self.current_wave = []
        self.update_current_display()
    
    def remove_selected(self):
        sel = self.current_list.curselection()
        if not sel:
            return
        for i in sorted(sel, reverse=True):
            del self.current_wave[i]
        self.update_current_display()
    
    def replace_selected(self):
        sel = self.current_list.curselection()
        if not sel:
            return
        for i in sel:
            possible = [z for z in self.all_zombies if z != self.current_wave[i]['type']]
            if not possible:
                possible = self.all_zombies
            self.current_wave[i] = {
                "type": random.choice(possible),
                "row": random.randint(1, 5),
                "delay": random.randint(0, 5000)
            }
        self.current_wave.sort(key=lambda x: x['delay'])
        self.update_current_display()
    
    def replace_all_of_type(self):
        find_type = self.replace_type.get()
        if not find_type:
            return
        indices = [i for i, z in enumerate(self.current_wave) if z['type'] == find_type]
        if not indices:
            return
        for i in indices:
            possible = [z for z in self.all_zombies if z != find_type]
            if not possible:
                possible = self.all_zombies
            self.current_wave[i] = {
                "type": random.choice(possible),
                "row": random.randint(1, 5),
                "delay": random.randint(0, 5000)
            }
        self.current_wave.sort(key=lambda x: x['delay'])
        self.update_current_display()
    
    def update_current_display(self):
        self.current_list.delete(0, tk.END)
        for z in self.current_wave:
            self.current_list.insert(tk.END, f"{z['type']} | ряд {z['row']} | {z['delay']}мс")
    
    def save_wave(self):
        if not self.current_wave:
            return
        self.level_waves.append({"zombies": self.current_wave.copy()})
        self.current_wave = []
        self.update_current_display()
        self.update_waves_display()
    
    def update_waves_display(self):
        self.waves_list.delete(0, tk.END)
        for i, w in enumerate(self.level_waves):
            self.waves_list.insert(tk.END, f"Волна {i+1}: {len(w['zombies'])} зомби")
    
    def edit_wave(self):
        sel = self.waves_list.curselection()
        if sel:
            self.current_wave = self.level_waves[sel[0]]['zombies'].copy()
            self.level_waves.pop(sel[0])
            self.update_current_display()
            self.update_waves_display()
    
    def delete_wave(self):
        sel = self.waves_list.curselection()
        if sel:
            self.level_waves.pop(sel[0])
            self.update_waves_display()
    
    def save_level(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название")
            return
        if not self.level_waves:
            messagebox.showerror("Ошибка", "Добавьте волны")
            return
        
        level = {
            "name": name,
            "author": "Editor",
            "startSun": int(self.sun_entry.get() or 150),
            "nightMode": self.night_var.get(),
            "plants": self.selected_plants if self.selected_plants else None,
            "zombies": None,
            "waves": self.level_waves
        }
        
        os.makedirs("custom_waves", exist_ok=True)
        fn = name.lower().replace(' ', '_') + ".json"
        with open(f"custom_waves/{fn}", 'w') as f:
            json.dump(level, f, indent=2)
        
        messagebox.showinfo("Успех", f"Уровень '{name}' сохранён!")
        
        self.level_waves = []
        self.current_wave = []
        self.update_current_display()
        self.update_waves_display()
        self.name_entry.delete(0, tk.END)
        self.load_levels()
    
    def load_levels(self):
        self.levels = []
        if os.path.exists('custom_waves'):
            for f in os.listdir('custom_waves'):
                if f.endswith('.json'):
                    try:
                        with open(f"custom_waves/{f}", 'r') as file:
                            lvl = json.load(file)
                            lvl['_file'] = f
                            self.levels.append(lvl)
                    except:
                        pass
        self.levels_list.delete(0, tk.END)
        for lvl in self.levels:
            self.levels_list.insert(tk.END, lvl.get('name', '?'))
    
    def load_level(self):
        sel = self.levels_list.curselection()
        if sel:
            lvl = self.levels[sel[0]]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, lvl.get('name', ''))
            self.sun_entry.delete(0, tk.END)
            self.sun_entry.insert(0, str(lvl.get('startSun', 150)))
            self.night_var.set(lvl.get('nightMode', False))
            self.level_waves = lvl.get('waves', []).copy()
            self.update_waves_display()
            
            plants = lvl.get('plants')
            if plants:
                self.selected_plants = plants.copy()
                self.sel_plants.delete(0, tk.END)
                for p in self.selected_plants:
                    self.sel_plants.insert(tk.END, p)
            else:
                self.selected_plants = []
                self.sel_plants.delete(0, tk.END)
            
            messagebox.showinfo("Загружено", f"Уровень '{lvl.get('name')}' загружен")
    
    def delete_level(self):
        sel = self.levels_list.curselection()
        if sel:
            lvl = self.levels[sel[0]]
            if messagebox.askyesno("Удалить", f"Удалить '{lvl.get('name')}'?"):
                os.remove(f"custom_waves/{lvl['_file']}")
                self.load_levels()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalSimpleEditor(root)
    root.mainloop()
