#!/usr/bin/env python3
import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import random

class FinalEditor:
    def __init__(self, root):
        self.root = root
        self.root.title('PvZ Desktop Editor')
        self.root.geometry('1400x900')
        self.root.configure(bg='#1a1a2e')
        
        with open('manifest.json', 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        
        self.all_plants = sorted(list(self.manifest.get('plants', {}).keys()))
        self.all_zombies = sorted([z for z in self.manifest.get('zombies', {}).keys() if z != 'your_death'])
        
        self.available_plants = self.all_plants.copy()
        self.available_zombies = self.all_zombies.copy()
        
        self.level_waves = []
        self.current_wave_zombies = []
        self.selected_plants = []
        self.selected_zombies = []
        
        self.plant_img = None
        self.zombie_img = None
        
        self.random_delay = tk.BooleanVar(value=False)
        self.random_min = tk.StringVar(value='0')
        self.random_max = tk.StringVar(value='5000')
        self.random_row = tk.BooleanVar(value=False)
        self.random_type = tk.BooleanVar(value=False)
        
        self.use_all_plants = tk.BooleanVar(value=True)
        self.use_all_zombies = tk.BooleanVar(value=True)
        
        # Новая переменная для количества рандомных зомби
        self.random_count = tk.StringVar(value='5')
        
        self.levels = []
        if os.path.exists('custom_waves'):
            for f in os.listdir('custom_waves'):
                if f.endswith('.json'):
                    try:
                        with open(f'custom_waves/{f}', 'r', encoding='utf-8') as file:
                            lvl = json.load(file)
                            lvl['_file'] = f
                            self.levels.append(lvl)
                    except:
                        pass
        
        self.create_ui()
        self.refresh_lists()
    
    def create_ui(self):
        top = tk.Frame(self.root, bg='#e94560', height=45)
        top.pack(fill='x')
        top.pack_propagate(False)
        tk.Label(top, text='🌱 PvZ DESKTOP EDITOR 🧟', 
                 font=('Arial', 16, 'bold'), bg='#e94560', fg='white').pack(expand=True)
        
        nb = ttk.Notebook(self.root)
        nb.pack(fill='both', expand=True, padx=10, pady=10)
        
        tab1 = tk.Frame(nb, bg='#1a1a2e')
        nb.add(tab1, text='🌱 Растения')
        self.plant_ui(tab1)
        
        tab2 = tk.Frame(nb, bg='#1a1a2e')
        nb.add(tab2, text='🧟 Зомби')
        self.zombie_ui(tab2)
        
        tab3 = tk.Frame(nb, bg='#1a1a2e')
        nb.add(tab3, text='📊 Уровни')
        self.level_ui(tab3)
        
        tab4 = tk.Frame(nb, bg='#1a1a2e')
        nb.add(tab4, text='📋 Данные')
        self.list_ui(tab4)
        
        bottom = tk.Frame(self.root, bg='#1a1a2e')
        bottom.pack(fill='x', padx=10, pady=5)
        tk.Button(bottom, text='▶ ЗАПУСТИТЬ ИГРУ', command=self.launch,
                  bg='#4ecdc4', fg='#1a1a2e', font=('Arial', 12, 'bold')).pack()
    
    def plant_ui(self, parent):
        left = tk.Frame(parent, bg='#2a2a3e', width=500)
        left.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        left.pack_propagate(False)
        
        tk.Label(left, text='➕ ДОБАВИТЬ РАСТЕНИЕ', font=('Arial', 12, 'bold'),
                 bg='#2a2a3e', fg='#4ecdc4').pack(pady=10)
        
        self.plant_preview = tk.Label(left, bg='#1a1a2e', width=25, height=8,
                                       text='🖼️ НЕТ КАРТИНКИ', font=('Arial', 10))
        self.plant_preview.pack(pady=10)
        
        tk.Button(left, text='📂 ВЫБРАТЬ КАРТИНКУ', command=self.sel_plant,
                  bg='#4ecdc4', fg='#1a1a2e', font=('Arial', 10)).pack(pady=5)
        
        frame = tk.Frame(left, bg='#2a2a3e')
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text='КЛЮЧ (англ):', bg='#2a2a3e', fg='white').grid(row=0, column=0, sticky='w')
        self.plant_key = tk.Entry(frame, bg='#1a1a2e', fg='#4ecdc4', width=25)
        self.plant_key.grid(row=0, column=1, padx=10)
        
        tk.Label(frame, text='СТОИМОСТЬ:', bg='#2a2a3e', fg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.plant_cost = tk.Entry(frame, bg='#1a1a2e', fg='#4ecdc4', width=10)
        self.plant_cost.insert(0, '100')
        self.plant_cost.grid(row=1, column=1, sticky='w', padx=10)
        
        abilities = tk.LabelFrame(left, text='СПОСОБНОСТИ', bg='#2a2a3e', fg='#ffd700')
        abilities.pack(fill='x', padx=20, pady=10)
        
        self.plant_shoots = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Стреляет', variable=self.plant_shoots,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.plant_explosive = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Взрывается', variable=self.plant_explosive,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.plant_sun = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Даёт солнце', variable=self.plant_sun,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.plant_magnet = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Магнит', variable=self.plant_magnet,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.plant_wall = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Стена', variable=self.plant_wall,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        tk.Button(left, text='💾 СОХРАНИТЬ', command=self.save_plant,
                  bg='#e94560', fg='white', font=('Arial', 12, 'bold')).pack(pady=20, padx=20, fill='x')
        
        right = tk.Frame(parent, bg='#2a2a3e', width=500)
        right.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        right.pack_propagate(False)
        
        tk.Label(right, text='📋 ВСЕ РАСТЕНИЯ', font=('Arial', 12, 'bold'),
                 bg='#2a2a3e', fg='#4ecdc4').pack(pady=10)
        
        scroll = tk.Scrollbar(right)
        scroll.pack(side='right', fill='y')
        self.plant_list = tk.Listbox(right, bg='#1a1a2e', fg='#4ecdc4', font=('Courier', 11), yscrollcommand=scroll.set, height=20)
        self.plant_list.pack(fill='both', expand=True, padx=10, pady=5)
        scroll.config(command=self.plant_list.yview)
        
        btn_frame = tk.Frame(right, bg='#2a2a3e')
        btn_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(btn_frame, text='🗑 УДАЛИТЬ', command=self.del_plant,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
    
    def zombie_ui(self, parent):
        left = tk.Frame(parent, bg='#2a2a3e', width=500)
        left.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        left.pack_propagate(False)
        
        tk.Label(left, text='➕ ДОБАВИТЬ ЗОМБИ', font=('Arial', 12, 'bold'),
                 bg='#2a2a3e', fg='#e94560').pack(pady=10)
        
        self.zombie_preview = tk.Label(left, bg='#1a1a2e', width=25, height=8,
                                        text='🖼️ НЕТ КАРТИНКИ', font=('Arial', 10))
        self.zombie_preview.pack(pady=10)
        
        tk.Button(left, text='📂 ВЫБРАТЬ КАРТИНКУ', command=self.sel_zombie,
                  bg='#e94560', fg='white', font=('Arial', 10)).pack(pady=5)
        
        frame = tk.Frame(left, bg='#2a2a3e')
        frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame, text='КЛЮЧ:', bg='#2a2a3e', fg='white').grid(row=0, column=0, sticky='w')
        self.zombie_key = tk.Entry(frame, bg='#1a1a2e', fg='#e94560', width=25)
        self.zombie_key.grid(row=0, column=1, padx=10)
        
        tk.Label(frame, text='HP (мин,макс):', bg='#2a2a3e', fg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.zombie_hp = tk.Entry(frame, bg='#1a1a2e', fg='#e94560', width=10)
        self.zombie_hp.insert(0, '5,7')
        self.zombie_hp.grid(row=1, column=1, sticky='w', padx=10)
        
        tk.Label(frame, text='СКОРОСТЬ:', bg='#2a2a3e', fg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.zombie_speed = tk.Entry(frame, bg='#1a1a2e', fg='#e94560', width=10)
        self.zombie_speed.insert(0, '0.6')
        self.zombie_speed.grid(row=2, column=1, sticky='w', padx=10)
        
        abilities = tk.LabelFrame(left, text='СПОСОБНОСТИ', bg='#2a2a3e', fg='#ffd700')
        abilities.pack(fill='x', padx=20, pady=10)
        
        self.zombie_system = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Системный файл', variable=self.zombie_system,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.zombie_archive = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Архиватор', variable=self.zombie_archive,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.zombie_catapult = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Катапульта', variable=self.zombie_catapult,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        self.zombie_boss = tk.BooleanVar()
        tk.Checkbutton(abilities, text='Босс', variable=self.zombie_boss,
                       bg='#2a2a3e', fg='white', selectcolor='#2a2a3e').pack(anchor='w', padx=20)
        
        tk.Button(left, text='💾 СОХРАНИТЬ', command=self.save_zombie,
                  bg='#e94560', fg='white', font=('Arial', 12, 'bold')).pack(pady=20, padx=20, fill='x')
        
        right = tk.Frame(parent, bg='#2a2a3e', width=500)
        right.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        right.pack_propagate(False)
        
        tk.Label(right, text='📋 ВСЕ ЗОМБИ', font=('Arial', 12, 'bold'),
                 bg='#2a2a3e', fg='#e94560').pack(pady=10)
        
        scroll = tk.Scrollbar(right)
        scroll.pack(side='right', fill='y')
        self.zombie_list = tk.Listbox(right, bg='#1a1a2e', fg='#e94560', font=('Courier', 11), yscrollcommand=scroll.set, height=20)
        self.zombie_list.pack(fill='both', expand=True, padx=10, pady=5)
        scroll.config(command=self.zombie_list.yview)
        
        btn_frame = tk.Frame(right, bg='#2a2a3e')
        btn_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(btn_frame, text='🗑 УДАЛИТЬ', command=self.del_zombie,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
    
    def level_ui(self, parent):
        canvas = tk.Canvas(parent, bg='#2a2a3e', highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='left', fill='y')
        
        inner = tk.Frame(canvas, bg='#2a2a3e')
        canvas.create_window((0, 0), window=inner, anchor='nw', width=750)
        
        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        inner.bind('<Configure>', on_configure)
        
        def on_mousewheel(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), 'units')
        canvas.bind('<MouseWheel>', on_mousewheel)
        
        params = tk.LabelFrame(inner, text='📝 ПАРАМЕТРЫ УРОВНЯ', bg='#2a2a3e', fg='#ffd700')
        params.pack(fill='x', padx=20, pady=10)
        pf = tk.Frame(params, bg='#2a2a3e')
        pf.pack(padx=10, pady=10)
        
        tk.Label(pf, text='НАЗВАНИЕ:', bg='#2a2a3e', fg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.level_name = tk.Entry(pf, bg='#1a1a2e', fg='#ffd700', width=30)
        self.level_name.grid(row=0, column=1, padx=10)
        
        tk.Label(pf, text='СТАРТ. СОЛНЦЕ:', bg='#2a2a3e', fg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.level_sun = tk.Entry(pf, bg='#1a1a2e', fg='#ffd700', width=10)
        self.level_sun.insert(0, '150')
        self.level_sun.grid(row=1, column=1, sticky='w', padx=10)
        
        self.level_night = tk.BooleanVar()
        tk.Checkbutton(pf, text='🌙 НОЧНОЙ РЕЖИМ', variable=self.level_night,
                       bg='#2a2a3e', fg='#8888ff', selectcolor='#2a2a3e').grid(row=2, column=1, sticky='w', padx=10)
        
        plants_frame = tk.LabelFrame(inner, text='🌱 ВЫБОР РАСТЕНИЙ ДЛЯ УРОВНЯ', bg='#2a2a3e', fg='#4ecdc4')
        plants_frame.pack(fill='x', padx=20, pady=10)
        
        mode_frame = tk.Frame(plants_frame, bg='#2a2a3e')
        mode_frame.pack(fill='x', padx=10, pady=5)
        
        self.use_all_plants = tk.BooleanVar(value=True)
        tk.Radiobutton(mode_frame, text='✅ ВСЕ РАСТЕНИЯ', variable=self.use_all_plants, value=True,
                       bg='#2a2a3e', fg='#4ecdc4', selectcolor='#2a2a3e').pack(side='left', padx=10)
        tk.Radiobutton(mode_frame, text='📋 ТОЛЬКО ВЫБРАННЫЕ', variable=self.use_all_plants, value=False,
                       bg='#2a2a3e', fg='#ffd700', selectcolor='#2a2a3e').pack(side='left', padx=10)
        
        select_frame = tk.Frame(plants_frame, bg='#2a2a3e')
        select_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(select_frame, text='Доступные растения:', bg='#2a2a3e', fg='#aaa').pack(anchor='w')
        
        avail_plants_frame = tk.Frame(select_frame, bg='#2a2a3e')
        avail_plants_frame.pack(fill='x', pady=5)
        
        scroll_avail = tk.Scrollbar(avail_plants_frame)
        scroll_avail.pack(side='right', fill='y')
        
        self.avail_plants_list = tk.Listbox(avail_plants_frame, bg='#1a1a2e', fg='#4ecdc4', height=5, yscrollcommand=scroll_avail.set)
        self.avail_plants_list.pack(side='left', fill='both', expand=True)
        scroll_avail.config(command=self.avail_plants_list.yview)
        
        btn_frame = tk.Frame(select_frame, bg='#2a2a3e')
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text='➕ ДОБАВИТЬ ВЫБРАННОЕ →', command=self.add_selected_plant,
                  bg='#4ecdc4', fg='#1a1a2e').pack(side='left', padx=5)
        tk.Button(btn_frame, text='✅ ДОБАВИТЬ ВСЕ', command=self.add_all_selected_plants,
                  bg='#27ae60', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text='← УДАЛИТЬ ВЫБРАННОЕ', command=self.remove_selected_plant,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text='❌ ОЧИСТИТЬ ВСЕ', command=self.clear_selected_plants,
                  bg='#e67e22', fg='white').pack(side='left', padx=5)
        
        tk.Label(select_frame, text='Выбранные растения:', bg='#2a2a3e', fg='#ffd700').pack(anchor='w')
        
        sel_plants_frame = tk.Frame(select_frame, bg='#2a2a3e')
        sel_plants_frame.pack(fill='x', pady=5)
        
        scroll_sel = tk.Scrollbar(sel_plants_frame)
        scroll_sel.pack(side='right', fill='y')
        
        self.sel_plants_list = tk.Listbox(sel_plants_frame, bg='#1a1a2e', fg='#ffd700', height=4, yscrollcommand=scroll_sel.set)
        self.sel_plants_list.pack(side='left', fill='both', expand=True)
        scroll_sel.config(command=self.sel_plants_list.yview)
        
        zombies_frame = tk.LabelFrame(inner, text='🧟 ВЫБОР ЗОМБИ ДЛЯ УРОВНЯ', bg='#2a2a3e', fg='#e94560')
        zombies_frame.pack(fill='x', padx=20, pady=10)
        
        mode_frame_z = tk.Frame(zombies_frame, bg='#2a2a3e')
        mode_frame_z.pack(fill='x', padx=10, pady=5)
        
        self.use_all_zombies = tk.BooleanVar(value=True)
        tk.Radiobutton(mode_frame_z, text='✅ ВСЕ ЗОМБИ', variable=self.use_all_zombies, value=True,
                       bg='#2a2a3e', fg='#e94560', selectcolor='#2a2a3e').pack(side='left', padx=10)
        tk.Radiobutton(mode_frame_z, text='📋 ТОЛЬКО ВЫБРАННЫЕ', variable=self.use_all_zombies, value=False,
                       bg='#2a2a3e', fg='#ffd700', selectcolor='#2a2a3e').pack(side='left', padx=10)
        
        select_frame_z = tk.Frame(zombies_frame, bg='#2a2a3e')
        select_frame_z.pack(fill='x', padx=10, pady=5)
        
        tk.Label(select_frame_z, text='Доступные зомби:', bg='#2a2a3e', fg='#aaa').pack(anchor='w')
        
        avail_zombies_frame = tk.Frame(select_frame_z, bg='#2a2a3e')
        avail_zombies_frame.pack(fill='x', pady=5)
        
        scroll_z_avail = tk.Scrollbar(avail_zombies_frame)
        scroll_z_avail.pack(side='right', fill='y')
        
        self.avail_zombies_list = tk.Listbox(avail_zombies_frame, bg='#1a1a2e', fg='#e94560', height=5, yscrollcommand=scroll_z_avail.set)
        self.avail_zombies_list.pack(side='left', fill='both', expand=True)
        scroll_z_avail.config(command=self.avail_zombies_list.yview)
        
        btn_frame_z = tk.Frame(select_frame_z, bg='#2a2a3e')
        btn_frame_z.pack(pady=5)
        tk.Button(btn_frame_z, text='➕ ДОБАВИТЬ ВЫБРАННОГО →', command=self.add_selected_zombie,
                  bg='#e94560', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame_z, text='✅ ДОБАВИТЬ ВСЕХ', command=self.add_all_selected_zombies,
                  bg='#27ae60', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame_z, text='← УДАЛИТЬ ВЫБРАННОГО', command=self.remove_selected_zombie,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame_z, text='❌ ОЧИСТИТЬ ВСЕХ', command=self.clear_selected_zombies,
                  bg='#e67e22', fg='white').pack(side='left', padx=5)
        
        tk.Label(select_frame_z, text='Выбранные зомби:', bg='#2a2a3e', fg='#ffd700').pack(anchor='w')
        
        sel_zombies_frame = tk.Frame(select_frame_z, bg='#2a2a3e')
        sel_zombies_frame.pack(fill='x', pady=5)
        
        scroll_z_sel = tk.Scrollbar(sel_zombies_frame)
        scroll_z_sel.pack(side='right', fill='y')
        
        self.sel_zombies_list = tk.Listbox(sel_zombies_frame, bg='#1a1a2e', fg='#ffd700', height=4, yscrollcommand=scroll_z_sel.set)
        self.sel_zombies_list.pack(side='left', fill='both', expand=True)
        scroll_z_sel.config(command=self.sel_zombies_list.yview)
        
        waves_frame = tk.LabelFrame(inner, text='📋 ВОЛНЫ', bg='#2a2a3e', fg='#ffd700')
        waves_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Рандом опции
        rand_frame = tk.Frame(waves_frame, bg='#2a2a3e')
        rand_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Checkbutton(rand_frame, text='🎲 Рандомная задержка', variable=self.random_delay,
                       bg='#2a2a3e', fg='#ffd700', selectcolor='#2a2a3e').pack(side='left', padx=5)
        tk.Label(rand_frame, text='от', bg='#2a2a3e', fg='white').pack(side='left')
        self.rand_min = tk.Entry(rand_frame, width=5, bg='#1a1a2e', fg='#ffd700')
        self.rand_min.insert(0, '0')
        self.rand_min.pack(side='left', padx=2)
        tk.Label(rand_frame, text='до', bg='#2a2a3e', fg='white').pack(side='left')
        self.rand_max = tk.Entry(rand_frame, width=5, bg='#1a1a2e', fg='#ffd700')
        self.rand_max.insert(0, '5000')
        self.rand_max.pack(side='left', padx=2)
        tk.Label(rand_frame, text='мс', bg='#2a2a3e', fg='white').pack(side='left')
        
        tk.Checkbutton(rand_frame, text='🎲 Рандомный ряд', variable=self.random_row,
                       bg='#2a2a3e', fg='#ffd700', selectcolor='#2a2a3e').pack(side='left', padx=10)
        tk.Checkbutton(rand_frame, text='🎲 Рандомный тип зомби', variable=self.random_type,
                       bg='#2a2a3e', fg='#ffd700', selectcolor='#2a2a3e').pack(side='left', padx=10)
        
        # НОВЫЕ КНОПКИ: рандомные зомби и босс
        random_frame = tk.Frame(waves_frame, bg='#2a2a3e')
        random_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(random_frame, text='🎲 ДОБАВИТЬ РАНДОМНЫХ:', bg='#2a2a3e', fg='#ffd700').pack(side='left')
        self.random_count_entry = tk.Entry(random_frame, width=5, bg='#1a1a2e', fg='#ffd700')
        self.random_count_entry.insert(0, '5')
        self.random_count_entry.pack(side='left', padx=5)
        tk.Button(random_frame, text='🎲 РАНДОМНЫЕ ЗОМБИ', command=self.add_random_zombies,
                  bg='#9b59b6', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        tk.Button(random_frame, text='👑 ДОБАВИТЬ БОССА', command=self.add_boss_to_wave,
                  bg='#c0392b', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
        # Добавление зомби в волну
        add_frame = tk.Frame(waves_frame, bg='#2a2a3e')
        add_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(add_frame, text='➕ ДОБАВИТЬ ЗОМБИ В ВОЛНУ:', bg='#2a2a3e', fg='#ffd700').pack(anchor='w')
        
        wr = tk.Frame(add_frame, bg='#2a2a3e')
        wr.pack(fill='x', pady=5)
        
        tk.Label(wr, text='Тип:', bg='#2a2a3e', fg='white').pack(side='left')
        self.wave_type = ttk.Combobox(wr, values=self.all_zombies, width=20)
        self.wave_type.pack(side='left', padx=5)
        
        tk.Label(wr, text='Ряд:', bg='#2a2a3e', fg='white').pack(side='left', padx=10)
        self.wave_row = tk.Spinbox(wr, from_=1, to=5, width=5)
        self.wave_row.pack(side='left', padx=5)
        
        tk.Label(wr, text='Задержка (мс):', bg='#2a2a3e', fg='white').pack(side='left', padx=10)
        self.wave_delay = tk.Entry(wr, width=8, bg='#1a1a2e', fg='white')
        self.wave_delay.insert(0, '0')
        self.wave_delay.pack(side='left', padx=5)
        
        tk.Button(wr, text='➕ ДОБАВИТЬ', command=self.add_to_wave,
                  bg='#4ecdc4', fg='#1a1a2e', font=('Arial', 9, 'bold')).pack(side='left', padx=10)
        
        tk.Label(waves_frame, text='📋 ЗОМБИ В ТЕКУЩЕЙ ВОЛНЕ:', bg='#2a2a3e', fg='#4ecdc4').pack(anchor='w', padx=10)
        self.wave_list = tk.Listbox(waves_frame, bg='#1a1a2e', fg='#4ecdc4', height=4)
        self.wave_list.pack(fill='x', padx=10, pady=5)
        
        wave_btns = tk.Frame(waves_frame, bg='#2a2a3e')
        wave_btns.pack(pady=5)
        tk.Button(wave_btns, text='❌ УДАЛИТЬ ИЗ ВОЛНЫ', command=self.remove_from_wave,
                  bg='#c0392b', fg='white').pack()
        
        wave_ctrl = tk.Frame(waves_frame, bg='#2a2a3e')
        wave_ctrl.pack(pady=5)
        tk.Button(wave_ctrl, text='💾 СОХРАНИТЬ ВОЛНУ', command=self.save_wave,
                  bg='#4ecdc4', fg='#1a1a2e').pack(side='left', padx=5)
        tk.Button(wave_ctrl, text='🗑 ОЧИСТИТЬ ВОЛНУ', command=self.clear_wave,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        
        tk.Label(waves_frame, text='📋 СОЗДАННЫЕ ВОЛНЫ:', bg='#2a2a3e', fg='#ffd700').pack(anchor='w', padx=10)
        self.waves_list = tk.Listbox(waves_frame, bg='#1a1a2e', fg='#ffd700', height=4)
        self.waves_list.pack(fill='x', padx=10, pady=5)
        
        wave_edit = tk.Frame(waves_frame, bg='#2a2a3e')
        wave_edit.pack(pady=5)
        tk.Button(wave_edit, text='✏ РЕДАКТИРОВАТЬ ВОЛНУ', command=self.edit_wave,
                  bg='#f39c12', fg='white').pack(side='left', padx=5)
        tk.Button(wave_edit, text='🗑 УДАЛИТЬ ВОЛНУ', command=self.delete_wave,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        
        tk.Button(inner, text='💾 СОХРАНИТЬ УРОВЕНЬ', command=self.save_level,
                  bg='#e94560', fg='white', font=('Arial', 14, 'bold')).pack(pady=15, padx=20, fill='x')
        
        right = tk.Frame(parent, bg='#2a2a3e', width=400)
        right.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        right.pack_propagate(False)
        
        tk.Label(right, text='📁 СОХРАНЁННЫЕ УРОВНИ', font=('Arial', 12, 'bold'),
                 bg='#2a2a3e', fg='#ffd700').pack(pady=10)
        
        scroll = tk.Scrollbar(right)
        scroll.pack(side='right', fill='y')
        self.levels_list = tk.Listbox(right, bg='#1a1a2e', fg='#ffd700', yscrollcommand=scroll.set, height=25)
        self.levels_list.pack(fill='both', expand=True, padx=10, pady=5)
        scroll.config(command=self.levels_list.yview)
        
        btn_r = tk.Frame(right, bg='#2a2a3e')
        btn_r.pack(fill='x', padx=10, pady=5)
        tk.Button(btn_r, text='📂 ЗАГРУЗИТЬ УРОВЕНЬ', command=self.load_level,
                  bg='#4ecdc4', fg='#1a1a2e').pack(side='left', padx=5)
        tk.Button(btn_r, text='🗑 УДАЛИТЬ УРОВЕНЬ', command=self.del_level,
                  bg='#c0392b', fg='white').pack(side='left', padx=5)
        
        self.refresh_level_lists()
    
    def refresh_level_lists(self):
        self.wave_type['values'] = self.all_zombies
        self.levels_list.delete(0, tk.END)
        for lvl in self.levels:
            self.levels_list.insert(tk.END, lvl.get('name', '?'))
    
    def add_selected_plant(self):
        if self.avail_plants_list.curselection():
            plant = self.avail_plants_list.get(self.avail_plants_list.curselection())
            if plant not in self.selected_plants:
                self.selected_plants.append(plant)
                self.sel_plants_list.insert(tk.END, plant)
    
    def add_all_selected_plants(self):
        self.selected_plants = self.all_plants.copy()
        self.sel_plants_list.delete(0, tk.END)
        for p in self.selected_plants:
            self.sel_plants_list.insert(tk.END, p)
    
    def remove_selected_plant(self):
        if self.sel_plants_list.curselection():
            idx = self.sel_plants_list.curselection()[0]
            self.selected_plants.pop(idx)
            self.sel_plants_list.delete(idx)
    
    def clear_selected_plants(self):
        self.selected_plants = []
        self.sel_plants_list.delete(0, tk.END)
    
    def add_selected_zombie(self):
        if self.avail_zombies_list.curselection():
            zombie = self.avail_zombies_list.get(self.avail_zombies_list.curselection())
            if zombie not in self.selected_zombies:
                self.selected_zombies.append(zombie)
                self.sel_zombies_list.insert(tk.END, zombie)
    
    def add_all_selected_zombies(self):
        self.selected_zombies = self.all_zombies.copy()
        self.sel_zombies_list.delete(0, tk.END)
        for z in self.selected_zombies:
            self.sel_zombies_list.insert(tk.END, z)
    
    def remove_selected_zombie(self):
        if self.sel_zombies_list.curselection():
            idx = self.sel_zombies_list.curselection()[0]
            self.selected_zombies.pop(idx)
            self.sel_zombies_list.delete(idx)
    
    def clear_selected_zombies(self):
        self.selected_zombies = []
        self.sel_zombies_list.delete(0, tk.END)
    
    def add_to_wave(self):
        if self.random_type.get() and self.all_zombies:
            ztype = random.choice(self.all_zombies)
        else:
            ztype = self.wave_type.get()
            if not ztype:
                messagebox.showerror('Ошибка', 'Выберите тип зомби!')
                return
        
        if self.random_delay.get():
            try:
                min_d = int(self.rand_min.get())
                max_d = int(self.rand_max.get())
                delay = random.randint(min_d, max_d)
            except:
                delay = 0
        else:
            try:
                delay = int(self.wave_delay.get() or 0)
            except:
                delay = 0
        
        if self.random_row.get():
            row = random.randint(1, 5)
        else:
            try:
                row = int(self.wave_row.get())
            except:
                row = 1
        
        self.current_wave_zombies.append({'type': ztype, 'row': row, 'delay': delay})
        self.refresh_wave_list()
    
    # НОВЫЕ ФУНКЦИИ
    def add_random_zombies(self):
        """Добавляет X рандомных зомби в текущую волну"""
        try:
            count = int(self.random_count_entry.get())
        except:
            count = 5
        
        types = ['zombie', 'system_zombie', 'hdd_zombie', 'ssd_zombie', 
                 'winrar_zombie', 'trojan_catapult', 'flag_zombie', 'bungee',
                 'pole_loud', 'pole_quiet', 'excel_zombie']
        
        for i in range(count):
            ztype = random.choice(types)
            row = random.randint(1, 5)
            delay = i * random.randint(200, 800)
            self.current_wave_zombies.append({
                "type": ztype,
                "row": row,
                "delay": delay
            })
        
        self.refresh_wave_list()
        messagebox.showinfo("Успех", f"✅ Добавлено {count} рандомных зомби!")
    
    def add_boss_to_wave(self):
        """Добавляет босса 'Ваша смерть' в текущую волну"""
        self.current_wave_zombies.append({
            "type": "your_death",
            "row": 3,
            "delay": 0
        })
        self.refresh_wave_list()
        messagebox.showinfo("Успех", "👑 Босс 'Ваша смерть' добавлен в волну!")
    
    def remove_from_wave(self):
        if self.wave_list.curselection():
            idx = self.wave_list.curselection()[0]
            del self.current_wave_zombies[idx]
            self.refresh_wave_list()
    
    def refresh_wave_list(self):
        self.wave_list.delete(0, tk.END)
        for z in self.current_wave_zombies:
            self.wave_list.insert(tk.END, f"{z['type']}, ряд {z['row']}, {z['delay']}мс")
    
    def save_wave(self):
        if not self.current_wave_zombies:
            messagebox.showerror('Ошибка', 'Добавьте зомби в волну!')
            return
        self.level_waves.append({'zombies': self.current_wave_zombies.copy()})
        self.waves_list.insert(tk.END, f'Волна {len(self.level_waves)}: {len(self.current_wave_zombies)} зомби')
        self.current_wave_zombies = []
        self.refresh_wave_list()
        messagebox.showinfo('Успех', f'Волна {len(self.level_waves)} сохранена!')
    
    def clear_wave(self):
        self.current_wave_zombies = []
        self.refresh_wave_list()
    
    def edit_wave(self):
        if self.waves_list.curselection():
            idx = self.waves_list.curselection()[0]
            wave = self.level_waves[idx]
            self.current_wave_zombies = wave['zombies'].copy()
            self.refresh_wave_list()
            self.waves_list.delete(idx)
            del self.level_waves[idx]
            self.refresh_waves_list()
    
    def delete_wave(self):
        if self.waves_list.curselection():
            idx = self.waves_list.curselection()[0]
            del self.level_waves[idx]
            self.refresh_waves_list()
    
    def refresh_waves_list(self):
        self.waves_list.delete(0, tk.END)
        for i, w in enumerate(self.level_waves):
            self.waves_list.insert(tk.END, f'Волна {i+1}: {len(w.get("zombies", []))} зомби')
    
    def save_level(self):
        name = self.level_name.get().strip()
        if not name:
            messagebox.showerror('Ошибка', 'Введите название уровня!')
            return
        if not self.level_waves:
            messagebox.showerror('Ошибка', 'Добавьте хотя бы одну волну!')
            return
        
        level = {
            'name': name,
            'author': 'Editor',
            'startSun': int(self.level_sun.get() or 150),
            'nightMode': self.level_night.get(),
            'waves': self.level_waves
        }
        
        if self.use_all_plants.get():
            level['plants'] = None
        else:
            level['plants'] = self.selected_plants if self.selected_plants else None
        
        if self.use_all_zombies.get():
            level['zombies'] = None
        else:
            level['zombies'] = self.selected_zombies if self.selected_zombies else None
        
        os.makedirs('custom_waves', exist_ok=True)
        filename = name.lower().replace(' ', '_') + '.json'
        with open(f'custom_waves/{filename}', 'w', encoding='utf-8') as f:
            json.dump(level, f, indent=2, ensure_ascii=False)
        
        self.levels.append(level)
        self.refresh_lists()
        
        self.level_waves = []
        self.waves_list.delete(0, tk.END)
        self.level_name.delete(0, tk.END)
        self.level_sun.delete(0, tk.END)
        self.level_sun.insert(0, '150')
        self.level_night.set(False)
        
        messagebox.showinfo('Успех', f'Уровень "{name}" сохранён!\n\nВолн: {len(level["waves"])}')
    
    def load_level(self):
        if self.levels_list.curselection():
            idx = self.levels_list.curselection()[0]
            level = self.levels[idx]
            self.level_name.delete(0, tk.END)
            self.level_name.insert(0, level.get('name', ''))
            self.level_sun.delete(0, tk.END)
            self.level_sun.insert(0, str(level.get('startSun', 150)))
            self.level_night.set(level.get('nightMode', False))
            self.level_waves = level.get('waves', []).copy()
            self.refresh_waves_list()
            
            plants = level.get('plants')
            if plants is None or len(plants) == 0:
                self.use_all_plants.set(True)
                self.selected_plants = []
                self.sel_plants_list.delete(0, tk.END)
            else:
                self.use_all_plants.set(False)
                self.selected_plants = plants.copy()
                self.sel_plants_list.delete(0, tk.END)
                for p in self.selected_plants:
                    self.sel_plants_list.insert(tk.END, p)
            
            zombies = level.get('zombies')
            if zombies is None or len(zombies) == 0:
                self.use_all_zombies.set(True)
                self.selected_zombies = []
                self.sel_zombies_list.delete(0, tk.END)
            else:
                self.use_all_zombies.set(False)
                self.selected_zombies = zombies.copy()
                self.sel_zombies_list.delete(0, tk.END)
                for z in self.selected_zombies:
                    self.sel_zombies_list.insert(tk.END, z)
            
            messagebox.showinfo('Загружено', f'Уровень "{level.get("name")}" загружен')
    
    def del_level(self):
        if self.levels_list.curselection():
            idx = self.levels_list.curselection()[0]
            level = self.levels[idx]
            if messagebox.askyesno('Удалить', f'Удалить уровень "{level.get("name")}"?'):
                f = f'custom_waves/{level.get("_file")}'
                if os.path.exists(f):
                    os.remove(f)
                self.levels.pop(idx)
                self.refresh_lists()
    
    def del_plant(self):
        if self.plant_list.curselection():
            key = self.plant_list.get(self.plant_list.curselection())
            if key in ['sunflower', 'peashooter', 'folder_magnet', 'siamese_peashooter']:
                messagebox.showerror('Ошибка', 'Нельзя удалить стандартное растение!')
                return
            if messagebox.askyesno('Удалить', f'Удалить растение "{key}"?'):
                del self.manifest['plants'][key]
                with open('manifest.json', 'w', encoding='utf-8') as f:
                    json.dump(self.manifest, f, indent=2, ensure_ascii=False)
                self.all_plants = sorted(list(self.manifest['plants'].keys()))
                self.refresh_lists()
    
    def del_zombie(self):
        if self.zombie_list.curselection():
            key = self.zombie_list.get(self.zombie_list.curselection())
            if key in ['zombie', 'system_zombie', 'hdd_zombie', 'ssd_zombie']:
                messagebox.showerror('Ошибка', 'Нельзя удалить стандартного зомби!')
                return
            if messagebox.askyesno('Удалить', f'Удалить зомби "{key}"?'):
                del self.manifest['zombies'][key]
                with open('manifest.json', 'w', encoding='utf-8') as f:
                    json.dump(self.manifest, f, indent=2, ensure_ascii=False)
                self.all_zombies = sorted([z for z in self.manifest['zombies'].keys() if z != 'your_death'])
                self.refresh_lists()
    
    def refresh_lists(self):
        self.plant_list.delete(0, tk.END)
        for name in self.all_plants:
            self.plant_list.insert(tk.END, name)
        
        self.zombie_list.delete(0, tk.END)
        for name in self.all_zombies:
            self.zombie_list.insert(tk.END, name)
        
        self.levels_list.delete(0, tk.END)
        for lvl in self.levels:
            self.levels_list.insert(tk.END, lvl.get('name', '?'))
    
    def list_ui(self, parent):
        text = tk.Text(parent, bg='#1a1a2e', fg='#4ecdc4', font=('Courier', 10))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        text.insert(tk.END, '='*60 + '\n', 'line')
        text.insert(tk.END, '🌱 ВСЕ РАСТЕНИЯ\n', 'title')
        for name in self.all_plants:
            val = self.manifest['plants'][name]
            text.insert(tk.END, f'  {name} — {val.get("cost", "?")}☀\n', 'plant')
        
        text.insert(tk.END, '\n🧟 ВСЕ ЗОМБИ (кроме босса)\n', 'title')
        for name in self.all_zombies:
            val = self.manifest['zombies'][name]
            hp = val.get('hp', '?')
            if isinstance(hp, list):
                hp = f'{hp[0]}-{hp[1]}'
            text.insert(tk.END, f'  {name} — HP: {hp}, Spd: {val.get("speed", "?")}\n', 'zombie')
        
        text.insert(tk.END, '\n📊 УРОВНИ\n', 'title')
        for lvl in self.levels:
            text.insert(tk.END, f'  {lvl.get("name", "?")}\n', 'level')
        
        text.tag_config('title', font=('Arial', 12, 'bold'), foreground='#e94560')
        text.tag_config('plant', foreground='#4ecdc4')
        text.tag_config('zombie', foreground='#e94560')
        text.tag_config('level', foreground='#ffd700')
        text.tag_config('line', foreground='#333')
        text.config(state='disabled')
    
    def sel_plant(self):
        f = filedialog.askopenfilename(filetypes=[('Images', '*.png *.webp *.jpg *.jpeg')])
        if f:
            self.plant_img = f
            img = Image.open(f)
            img.thumbnail((100, 100))
            self.plant_photo = ImageTk.PhotoImage(img)
            self.plant_preview.config(image=self.plant_photo, text='')
    
    def sel_zombie(self):
        f = filedialog.askopenfilename(filetypes=[('Images', '*.png *.webp *.jpg *.jpeg')])
        if f:
            self.zombie_img = f
            img = Image.open(f)
            img.thumbnail((100, 100))
            self.zombie_photo = ImageTk.PhotoImage(img)
            self.zombie_preview.config(image=self.zombie_photo, text='')
    
    def save_plant(self):
        key = self.plant_key.get().strip().lower()
        if not key or not self.plant_img:
            messagebox.showerror('Ошибка', 'Заполните всё')
            return
        cost = int(self.plant_cost.get() or 100)
        os.makedirs('static/img/plants', exist_ok=True)
        ext = os.path.splitext(self.plant_img)[1]
        target = f'static/img/plants/{key}{ext}'
        shutil.copy2(self.plant_img, target)
        plant_data = {'cost': cost, 'file': f'{key}{ext}'}
        if self.plant_shoots.get(): plant_data['shootInterval'] = 2000
        if self.plant_explosive.get(): plant_data['isExplosive'] = True
        if self.plant_sun.get(): plant_data['sunInterval'] = [6000, 9000]
        if self.plant_magnet.get(): plant_data['attractRadius'] = 3
        if self.plant_wall.get(): plant_data['isWall'] = True
        self.manifest['plants'][key] = plant_data
        with open('manifest.json', 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        self.all_plants = sorted(list(self.manifest['plants'].keys()))
        self.refresh_lists()
        self.plant_key.delete(0, tk.END)
        self.plant_cost.delete(0, tk.END)
        self.plant_cost.insert(0, '100')
        self.plant_preview.config(image='', text='🖼️ НЕТ КАРТИНКИ')
        self.plant_img = None
        messagebox.showinfo('Успех', f'Растение {key} сохранено!')
    
    def save_zombie(self):
        key = self.zombie_key.get().strip().lower()
        if not key or not self.zombie_img:
            messagebox.showerror('Ошибка', 'Заполните всё')
            return
        hp_str = self.zombie_hp.get().strip()
        if ',' in hp_str:
            hp = [int(x.strip()) for x in hp_str.split(',')]
        else:
            hp = [int(hp_str), int(hp_str)]
        speed = float(self.zombie_speed.get() or 0.6)
        os.makedirs('static/img/zombies', exist_ok=True)
        ext = os.path.splitext(self.zombie_img)[1]
        target = f'static/img/zombies/{key}{ext}'
        shutil.copy2(self.zombie_img, target)
        zombie_data = {'hp': hp, 'file': f'{key}{ext}', 'speed': speed}
        if self.zombie_system.get(): zombie_data['hasSystemFile'] = True
        if self.zombie_archive.get(): zombie_data['canArchive'] = True
        if self.zombie_catapult.get(): zombie_data['isCatapult'] = True
        if self.zombie_boss.get(): zombie_data['isBoss'] = True
        self.manifest['zombies'][key] = zombie_data
        with open('manifest.json', 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        self.all_zombies = sorted([z for z in self.manifest['zombies'].keys() if z != 'your_death'])
        self.refresh_lists()
        self.zombie_key.delete(0, tk.END)
        self.zombie_hp.delete(0, tk.END)
        self.zombie_hp.insert(0, '5,7')
        self.zombie_speed.delete(0, tk.END)
        self.zombie_speed.insert(0, '0.6')
        self.zombie_preview.config(image='', text='🖼️ НЕТ КАРТИНКИ')
        self.zombie_img = None
        messagebox.showinfo('Успех', f'Зомби {key} сохранён!')
    
    def launch(self):
        self.root.destroy()
        subprocess.Popen([sys.executable, 'server.py'])

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalEditor(root)
    root.mainloop()
