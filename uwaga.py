#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import visual, core, event, gui
import os
import random
import csv
import configparser
import shutil
from numpy import sin, cos, deg2rad, linspace
from datetime import datetime
import glob

# ==================== KATALOG KONFIGURACJI ====================
CONFIG_DIR = 'config'

# ==================== WYBÓR KONFIGURACJI ====================
def find_config_files():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_files = glob.glob(os.path.join(CONFIG_DIR, 'config_*.ini'))
    return [os.path.basename(f) for f in config_files]

def create_default_configs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    test_config = """# ==================== KONFIGURACJA TESTOWA ====================
[EKSPERYMENT]
nazwa = test
opis = Tryb testowy - skrocona wersja badania

[WYSWIETLANIE]
fullscreen = False
screen_width = 1920
screen_height = 1080

[WERSJA]
# Wersja A: Niebieski (Lewy Shift) = trojkat, Czerwony (Prawy Shift) = romb
# Wersja B: Czerwony (Lewy Shift) = trojkat, Niebieski (Prawy Shift) = romb
wersja = A

[IKONA]
icon_in_center = True
icon_size = 0.04

[KSZTALTY]
use_colors = False
unique_shapes = True
target_size = 0.06
distractor_size = 0.06
fixation_size = 0.008
radius = 0.25

[CZASY]
fixation_time = 0.5
stimulus_time = 0.1
max_response_time = 2.0
feedback_time = 0.5

[PROBY]
n_training_trials = 8
n_experimental_trials = 32
n_blocks = 2

[FEEDBACK]
show_feedback = True

[APLIKACJE]
social_apps = tiktok.png, messenger.png, instagram.png
neutral_apps = calculator.png, calendar.png, weather.png, notes.png, clock.png, maps.png
"""
    
    badanie_config = """# ==================== KONFIGURACJA BADANIA ====================
[EKSPERYMENT]
nazwa = badanie
opis = Pelne badanie eksperymentalne

[WYSWIETLANIE]
fullscreen = True
screen_width = 1920
screen_height = 1080

[WERSJA]
# Wersja A: Niebieski (Lewy Shift) = trojkat, Czerwony (Prawy Shift) = romb
# Wersja B: Czerwony (Lewy Shift) = trojkat, Niebieski (Prawy Shift) = romb
wersja = A

[IKONA]
icon_in_center = True
icon_size = 0.04

[KSZTALTY]
use_colors = False
unique_shapes = True
target_size = 0.06
distractor_size = 0.06
fixation_size = 0.008
radius = 0.25

[CZASY]
fixation_time = 0.5
stimulus_time = 0.1
max_response_time = 2.0
feedback_time = 0.5

[PROBY]
n_training_trials = 32
n_experimental_trials = 320
n_blocks = 4

[FEEDBACK]
show_feedback = True

[APLIKACJE]
social_apps = tiktok.png, messenger.png, instagram.png
neutral_apps = calculator.png, calendar.png, weather.png, notes.png, clock.png, maps.png
"""
    
    with open(os.path.join(CONFIG_DIR, 'config_test.ini'), 'w', encoding='utf-8') as f:
        f.write(test_config)
    
    with open(os.path.join(CONFIG_DIR, 'config_badanie.ini'), 'w', encoding='utf-8') as f:
        f.write(badanie_config)

def select_config():
    while True:
        config_files = find_config_files()
        
        if not config_files:
            print("Brak plików konfiguracyjnych. Tworzę domyślne...")
            create_default_configs()
            config_files = find_config_files()
        
        choices = config_files + ['[Własna konfiguracja]']
        
        dlg = gui.Dlg(title='Wybór konfiguracji')
        dlg.addField('Wybierz konfigurację:', choices=choices)
        data = dlg.show()
        
        if not dlg.OK:
            core.quit()
        
        selected = data[0]
        
        if selected == '[Własna konfiguracja]':
            result = create_custom_config()
            if result is None:
                continue
            else:
                return result
        else:
            return os.path.join(CONFIG_DIR, selected)

def create_custom_config():
    dlg = gui.Dlg(title='Własna konfiguracja (Anuluj = Cofnij)')
    
    dlg.addText('=== EKSPERYMENT ===')
    dlg.addField('Nazwa konfiguracji:', 'custom')
    dlg.addField('Opis:', 'Wlasna konfiguracja')
    
    dlg.addText('=== WERSJA ===')
    dlg.addField('Wersja (A/B):', choices=['A', 'B'])
    
    dlg.addText('=== WYŚWIETLANIE ===')
    dlg.addField('Pełny ekran:', choices=['True', 'False'])
    dlg.addField('Szerokość ekranu:', 1920)
    dlg.addField('Wysokość ekranu:', 1080)
    
    dlg.addText('=== IKONA ===')
    dlg.addField('Ikona w centrum:', choices=['True', 'False'])
    dlg.addField('Rozmiar ikony:', 0.04)
    
    dlg.addText('=== KSZTAŁTY ===')
    dlg.addField('Kolorowe kształty:', choices=['False', 'True'])
    dlg.addField('Unikalne kształty:', choices=['True', 'False'])
    dlg.addField('Rozmiar targetu:', 0.06)
    dlg.addField('Promień okręgu:', 0.25)
    
    dlg.addText('=== CZASY (sekundy) ===')
    dlg.addField('Czas fiksacji:', 0.5)
    dlg.addField('Czas bodźca:', 0.1)
    dlg.addField('Max czas odpowiedzi:', 2.0)
    
    dlg.addText('=== PRÓBY ===')
    dlg.addField('Próby treningowe:', 32)
    dlg.addField('Próby eksperymentalne:', 320)
    dlg.addField('Liczba bloków:', 4)
    
    dlg.addText('=== FEEDBACK ===')
    dlg.addField('Pokazuj feedback:', choices=['True', 'False'])
    
    data = dlg.show()
    
    if not dlg.OK:
        return None
    
    config_name = f"config_{data[0]}.ini"
    config_path = os.path.join(CONFIG_DIR, config_name)
    
    config_content = f"""# ==================== KONFIGURACJA WŁASNA ====================
[EKSPERYMENT]
nazwa = {data[0]}
opis = {data[1]}

[WYSWIETLANIE]
fullscreen = {data[3]}
screen_width = {data[4]}
screen_height = {data[5]}

[WERSJA]
wersja = {data[2]}

[IKONA]
icon_in_center = {data[6]}
icon_size = {data[7]}

[KSZTALTY]
use_colors = {data[8]}
unique_shapes = {data[9]}
target_size = {data[10]}
distractor_size = {data[10]}
fixation_size = 0.008
radius = {data[11]}

[CZASY]
fixation_time = {data[12]}
stimulus_time = {data[13]}
max_response_time = {data[14]}
feedback_time = 0.5

[PROBY]
n_training_trials = {data[15]}
n_experimental_trials = {data[16]}
n_blocks = {data[17]}

[FEEDBACK]
show_feedback = {data[18]}

[APLIKACJE]
social_apps = tiktok.png, messenger.png, instagram.png
neutral_apps = calculator.png, calendar.png, weather.png, notes.png, clock.png, maps.png
"""
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"Utworzono konfigurację: {config_path}")
    return config_path

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    cfg = {}
    
    cfg['nazwa'] = config.get('EKSPERYMENT', 'nazwa', fallback='badanie')
    cfg['opis'] = config.get('EKSPERYMENT', 'opis', fallback='')
    
    cfg['fullscreen'] = config.getboolean('WYSWIETLANIE', 'fullscreen', fallback=True)
    cfg['screen_width'] = config.getint('WYSWIETLANIE', 'screen_width', fallback=1920)
    cfg['screen_height'] = config.getint('WYSWIETLANIE', 'screen_height', fallback=1080)
    
    cfg['wersja'] = config.get('WERSJA', 'wersja', fallback='A').upper()
    
    cfg['icon_in_center'] = config.getboolean('IKONA', 'icon_in_center', fallback=True)
    cfg['icon_size'] = config.getfloat('IKONA', 'icon_size', fallback=0.04)
    
    cfg['use_colors'] = config.getboolean('KSZTALTY', 'use_colors', fallback=False)
    cfg['unique_shapes'] = config.getboolean('KSZTALTY', 'unique_shapes', fallback=True)
    cfg['target_size'] = config.getfloat('KSZTALTY', 'target_size', fallback=0.06)
    cfg['distractor_size'] = config.getfloat('KSZTALTY', 'distractor_size', fallback=0.06)
    cfg['fixation_size'] = config.getfloat('KSZTALTY', 'fixation_size', fallback=0.008)
    cfg['radius'] = config.getfloat('KSZTALTY', 'radius', fallback=0.25)
    
    cfg['fixation_time'] = config.getfloat('CZASY', 'fixation_time', fallback=0.5)
    cfg['stimulus_time'] = config.getfloat('CZASY', 'stimulus_time', fallback=0.1)
    cfg['max_response_time'] = config.getfloat('CZASY', 'max_response_time', fallback=2.0)
    cfg['feedback_time'] = config.getfloat('CZASY', 'feedback_time', fallback=0.5)
    
    cfg['n_training_trials'] = config.getint('PROBY', 'n_training_trials', fallback=32)
    cfg['n_experimental_trials'] = config.getint('PROBY', 'n_experimental_trials', fallback=320)
    cfg['n_blocks'] = config.getint('PROBY', 'n_blocks', fallback=4)
    cfg['trials_per_block'] = cfg['n_experimental_trials'] // cfg['n_blocks']
    
    cfg['show_feedback'] = config.getboolean('FEEDBACK', 'show_feedback', fallback=True)
    
    social_str = config.get('APLIKACJE', 'social_apps', fallback='tiktok.png, messenger.png, instagram.png')
    neutral_str = config.get('APLIKACJE', 'neutral_apps', fallback='calculator.png, calendar.png, weather.png')
    cfg['social_apps'] = [x.strip() for x in social_str.split(',')]
    cfg['neutral_apps'] = [x.strip() for x in neutral_str.split(',')]
    
    return cfg

# ==================== GŁÓWNY PROGRAM ====================
config_file = select_config()
CFG = load_config(config_file)

print(f"Wczytano konfigurację: {config_file}")
print(f"Nazwa: {CFG['nazwa']}")
print(f"Wersja: {CFG['wersja']}")
print(f"Próby treningowe: {CFG['n_training_trials']}")
print(f"Próby eksperymentalne: {CFG['n_experimental_trials']}")

# ==================== SPRAWDZENIE ISTNIEJĄCYCH ID ====================
def check_existing_id(participant_id):
    os.makedirs('data', exist_ok=True)
    existing_files = glob.glob(f'data/result_{participant_id}_*.csv')
    return len(existing_files) > 0

# ==================== DIALOG INFO O BADANYM ====================
while True:
    exp_info = {
        'ID badanego': '',
        'Wiek': '',
        'Płeć': ['Kobieta', 'Mężczyzna', 'Inna', 'Nie chcę podawać'],
        'System telefonu': ['iOS', 'Android', 'Inny'],
        'Ręczność': ['Praworęczny', 'Leworęczny', 'Oburęczny'],
        'Korekta wzroku': ['Brak', 'Okulary', 'Soczewki'],
        'Uwagi': ''
    }
    dlg = gui.DlgFromDict(dictionary=exp_info, title='Eksperyment - Przeszukiwanie Sceny Wzrokowej')
    if not dlg.OK:
        core.quit()
    
    if check_existing_id(exp_info['ID badanego']):
        warn_dlg = gui.Dlg(title='Uwaga!')
        warn_dlg.addText(f"ID '{exp_info['ID badanego']}' już istnieje w bazie danych!")
        warn_dlg.addText("Proszę podać inne ID.")
        warn_dlg.show()
    else:
        break

exp_info['data'] = datetime.now().strftime('%Y-%m-%d')
exp_info['czas_rozpoczecia'] = datetime.now().strftime('%H:%M:%S')
exp_info['timestamp_start'] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
exp_info['config_file'] = config_file
exp_info['config_nazwa'] = CFG['nazwa']
exp_info['wersja'] = CFG['wersja']

# ==================== PARAMETRY Z KONFIGURACJI ====================
TARGETS = ['triangle', 'diamond']
DISTRACTORS = ['circle', 'square', 'hexagon', 'trapezoid']
AVAILABLE_COLORS = ['green', 'yellow', 'blue', 'red', 'white', 'black']

# ==================== INICJALIZACJA OKNA ====================
win = visual.Window(
    size=[CFG['screen_width'], CFG['screen_height']],
    fullscr=CFG['fullscreen'],
    screen=0,
    color=[0.2, 0.2, 0.2],
    units='height',
    allowGUI=not CFG['fullscreen']
)

# ==================== SPRAWDZANIE IKON ====================
def check_images(file_list):
    valid = []
    for f in file_list:
        if os.path.exists(f):
            valid.append(f)
    return valid

social_images = check_images(CFG['social_apps'])
neutral_images = check_images(CFG['neutral_apps'])

if not social_images:
    print("UWAGA: Brak ikon aplikacji społecznościowych!")
if not neutral_images:
    print("UWAGA: Brak ikon aplikacji neutralnych!")

# ==================== BODŹCE ====================
fixation = visual.ShapeStim(
    win,
    vertices='cross',
    size=(CFG['fixation_size'], CFG['fixation_size']),
    lineColor='white',
    fillColor='white'
)

app_icon = visual.ImageStim(win, size=(CFG['icon_size'], CFG['icon_size']), pos=(0, 0))

def create_shape(shape_type, size=None, color='white'):
    if size is None:
        size = CFG['target_size']
    half_size = size / 2
    
    if shape_type == 'diamond':
        vertices = [(0, half_size), (half_size*0.866, 0), (0, -half_size), (-half_size*0.866, 0)]
    elif shape_type == 'triangle':
        vertices = [(0, half_size), (half_size*0.866, -half_size), (-half_size*0.866, -half_size)]
    elif shape_type == 'hexagon':
        vertices = [(cos(deg2rad(a)) * half_size, sin(deg2rad(a)) * half_size) 
                   for a in range(0, 360, 60)]
    elif shape_type == 'circle':
        return visual.Circle(win, radius=half_size, lineColor=color, fillColor=None, lineWidth=3)
    elif shape_type == 'square':
        return visual.Rect(win, width=size*0.866, height=size*0.866, lineColor=color, fillColor=None, lineWidth=3)
    else:
        vertices = [(half_size*0.7, half_size), (half_size, -half_size), 
                   (-half_size, -half_size), (-half_size*0.7, half_size)]
    
    return visual.ShapeStim(win, vertices=vertices, lineColor=color, 
                           fillColor=None, lineWidth=3)

shape_stimuli = []
for i in range(6):
    shape_stimuli.append(create_shape('circle'))

feedback_text = visual.TextStim(win, text='', height=0.05, color='white')

notification_radius = CFG['icon_size'] * 0.2
notification_badge = visual.Circle(win, radius=notification_radius, fillColor='red', 
                                   lineColor='white', lineWidth=2)
notification_num = visual.TextStim(win, text='1', height=notification_radius*1.2, 
                                  color='white', bold=True)

# ==================== TWORZENIE LISTY PRÓB ====================
def create_trial_list():
    conditions = []
    n_per_condition = CFG['n_experimental_trials'] // 8
    
    for target in TARGETS:
        for app_type in ['social', 'neutral']:
            for app_side in ['left', 'right']:
                for _ in range(n_per_condition):
                    conditions.append({
                        'target': target,
                        'app_type': app_type,
                        'app_side': app_side
                    })
    
    random.shuffle(conditions)
    return conditions

# ==================== FUNKCJA POJEDYNCZEJ PRÓBY ====================
def run_trial(trial_params, trial_number, block_number, is_practice=False):
    target_shape = trial_params['target']
    app_type = trial_params['app_type']
    app_side = trial_params['app_side']
    
    icon_filename = None
    show_notification = False
    
    if app_type == 'social' and social_images:
        icon_filename = random.choice(social_images)
        app_icon.image = icon_filename
        show_notification = True
    elif app_type == 'neutral' and neutral_images:
        icon_filename = random.choice(neutral_images)
        app_icon.image = icon_filename
        show_notification = False
    else:
        app_icon.image = None
        show_notification = False
    
    if CFG['icon_in_center']:
        app_x = 0
        app_y = 0
    else:
        app_x = 0.45 if app_side == 'right' else -0.45
        app_y = 0
    
    app_icon.pos = (app_x, app_y)
    
    if show_notification:
        badge_offset = CFG['icon_size'] * 0.45
        notification_badge.pos = (app_x + badge_offset, app_y + badge_offset)
        notification_num.pos = (app_x + badge_offset, app_y + badge_offset)
    
    angles = linspace(0, 360, 6, endpoint=False)
    angle_offset = random.random() * 360
    target_idx = random.randint(0, 5)
    
    if CFG['use_colors']:
        shape_colors = AVAILABLE_COLORS.copy()
        random.shuffle(shape_colors)
    else:
        shape_colors = ['white'] * 6
    
    shapes_data = []
    colors_data = []
    
    if CFG['unique_shapes']:
        available_distractors = DISTRACTORS.copy()
        random.shuffle(available_distractors)
        distractors_for_trial = available_distractors + [random.choice(available_distractors)]
        random.shuffle(distractors_for_trial)
    else:
        distractors_for_trial = [random.choice(DISTRACTORS) for _ in range(5)]
    
    distractor_idx = 0
    for i in range(6):
        rad = deg2rad(angles[i] + angle_offset)
        x = CFG['radius'] * cos(rad)
        y = CFG['radius'] * sin(rad)
        
        if i == target_idx:
            shape_stimuli[i] = create_shape(target_shape, color=shape_colors[i])
            shapes_data.append(target_shape)
        else:
            shape_stimuli[i] = create_shape(distractors_for_trial[distractor_idx], color=shape_colors[i])
            shapes_data.append(distractors_for_trial[distractor_idx])
            distractor_idx += 1
        
        shape_stimuli[i].pos = (x, y)
        colors_data.append(shape_colors[i])

    # Lewy Shift = trójkąt, Prawy Shift = romb
    if target_shape == 'triangle':
        correct_key = 'lshift'
    else:
        correct_key = 'rshift'
    
    fixation.draw()
    win.flip()
    core.wait(CFG['fixation_time'])
    
    for shape in shape_stimuli:
        shape.draw()
    
    if app_icon.image:
        if not CFG['icon_in_center']:
            app_icon.draw()
    
    if show_notification and not CFG['icon_in_center']:
        notification_badge.draw()
        notification_num.draw()
    
    if CFG['icon_in_center'] and app_icon.image:
        app_icon.draw()
        if show_notification:
            notification_badge.draw()
            notification_num.draw()
    
    fixation.draw()
    win.flip()
    
    timer = core.Clock()
    
    core.wait(CFG['stimulus_time'])
    fixation.draw()
    win.flip()
    
    response = None
    rt = None
    
    keys = event.waitKeys(maxWait=CFG['max_response_time'] - CFG['stimulus_time'], 
                         keyList=['lshift', 'rshift', 'escape'], 
                         timeStamped=timer)
    if keys:
        if 'escape' in keys[0]:
            save_and_quit()
        response = keys[0][0]
        rt = keys[0][1]
    
    if response:
        correct = (response == correct_key)
        if rt and rt < 0.2:
            correct = False
            feedback_msg = "Za szybko!"
            feedback_color = 'yellow'
        elif rt and rt > 2.0:
            correct = False
            feedback_msg = "Za wolno!"
            feedback_color = 'yellow'
        elif correct:
            feedback_msg = "Poprawnie!"
            feedback_color = 'green'
        else:
            feedback_msg = "Błąd!"
            feedback_color = 'red'
    else:
        correct = False
        feedback_msg = "Za wolno!"
        feedback_color = 'yellow'
    
    if CFG['show_feedback']:
        feedback_text.text = feedback_msg
        feedback_text.color = feedback_color
        feedback_text.draw()
        win.flip()
        
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            save_and_quit()
    
    return {
        'id_badanego': exp_info['ID badanego'],
        'numer_proby': trial_number,
        'numer_bloku': block_number,
        'czy_trening': 1 if is_practice else 0,
        'typ_aplikacji': app_type,
        'strona_aplikacji': app_side,
        'target': target_shape,
        'ikona': icon_filename if icon_filename else '',
        'notyfikacja': 1 if show_notification else 0,
        'target_pozycja': target_idx,
        'ksztalt_0': shapes_data[0],
        'kolor_0': colors_data[0],
        'ksztalt_1': shapes_data[1],
        'kolor_1': colors_data[1],
        'ksztalt_2': shapes_data[2],
        'kolor_2': colors_data[2],
        'ksztalt_3': shapes_data[3],
        'kolor_3': colors_data[3],
        'ksztalt_4': shapes_data[4],
        'kolor_4': colors_data[4],
        'ksztalt_5': shapes_data[5],
        'kolor_5': colors_data[5],
        'odpowiedz': response if response else '',
        'poprawna_odpowiedz': correct_key,
        'czy_poprawna': 1 if correct else (0 if correct is not None else ''),
        'czas_reakcji_ms': round(rt * 1000, 2) if rt else ''
    }

# ==================== ZAPIS DANYCH ====================
results = []

def save_data():
    if results:
        os.makedirs('data', exist_ok=True)
        
        timestamp = exp_info['timestamp_start']
        participant_id = exp_info['ID badanego']
        
        filename_csv = f"data/result_{participant_id}_{timestamp}.csv"
        with open(filename_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(results)
        print(f"Wyniki zapisane: {filename_csv}")
        
        config_filename = f"data/config_{participant_id}_{timestamp}.ini"
        shutil.copy(config_file, config_filename)
        print(f"Konfiguracja zapisana: {config_filename}")
        
        summary_filename = f"data/summary_{participant_id}_{timestamp}.txt"
        
        experimental_trials = [r for r in results if r['czy_trening'] == 0]
        correct_trials = [r for r in experimental_trials if r['czy_poprawna'] == 1]
        
        if experimental_trials:
            accuracy = len(correct_trials) / len(experimental_trials) * 100
            rts = [r['czas_reakcji_ms'] for r in correct_trials if r['czas_reakcji_ms'] != '']
            mean_rt = sum(rts) / len(rts) if rts else 0
        else:
            accuracy = 0
            mean_rt = 0
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("PODSUMOWANIE SESJI EKSPERYMENTALNEJ\n")
            f.write("="*60 + "\n\n")
            f.write(f"ID badanego: {exp_info['ID badanego']}\n")
            f.write(f"Data: {exp_info['data']}\n")
            f.write(f"Czas rozpoczęcia: {exp_info['czas_rozpoczecia']}\n")
            f.write(f"Czas zakończenia: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Plik konfiguracji: {config_file}\n")
            f.write(f"Nazwa konfiguracji: {CFG['nazwa']}\n")
            f.write(f"Wersja: {CFG['wersja']}\n\n")
            f.write("-"*60 + "\n")
            f.write("DANE DEMOGRAFICZNE\n")
            f.write("-"*60 + "\n")
            f.write(f"Wiek: {exp_info.get('Wiek', '')}\n")
            f.write(f"Płeć: {exp_info.get('Płeć', '')}\n")
            f.write(f"System telefonu: {exp_info.get('System telefonu', '')}\n")
            f.write(f"Ręczność: {exp_info.get('Ręczność', '')}\n")
            f.write(f"Korekta wzroku: {exp_info.get('Korekta wzroku', '')}\n")
            f.write(f"Uwagi: {exp_info.get('Uwagi', '')}\n\n")
            f.write("-"*60 + "\n")
            f.write("WYNIKI\n")
            f.write("-"*60 + "\n")
            f.write(f"Liczba prób treningowych: {CFG['n_training_trials']}\n")
            f.write(f"Liczba prób eksperymentalnych: {len(experimental_trials)}\n")
            f.write(f"Poprawność ogólna: {accuracy:.1f}%\n")
            f.write(f"Średni czas reakcji (poprawne): {mean_rt:.1f} ms\n\n")
            f.write("-"*60 + "\n")
            f.write("PARAMETRY EKSPERYMENTU\n")
            f.write("-"*60 + "\n")
            f.write(f"Czas fiksacji: {CFG['fixation_time']*1000:.0f} ms\n")
            f.write(f"Czas ekspozycji bodźców: {CFG['stimulus_time']*1000:.0f} ms\n")
            f.write(f"Maks. czas odpowiedzi: {CFG['max_response_time']*1000:.0f} ms\n")
            f.write(f"Ikona w centrum: {'Tak' if CFG['icon_in_center'] else 'Nie'}\n")
            f.write(f"Kolorowe kształty: {'Tak' if CFG['use_colors'] else 'Nie'}\n")
            f.write(f"Unikalne kształty: {'Tak' if CFG['unique_shapes'] else 'Nie'}\n")
            f.write(f"Pełny ekran: {'Tak' if CFG['fullscreen'] else 'Nie'}\n")
        
        print(f"Podsumowanie zapisane: {summary_filename}")

def save_and_quit():
    save_data()
    win.close()
    core.quit()

# ==================== INSTRUKCJE ====================
def show_instruction(text, wait_for_space=True):
    instr = visual.TextStim(win, text=text, height=0.035, color='white', wrapWidth=1.5)
    instr.draw()
    win.flip()
    
    if wait_for_space:
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            save_and_quit()

# ==================== GŁÓWNY PRZEBIEG EKSPERYMENTU ====================
instruction_1 = """Dziękujemy za twój udział w badaniu.

Twoim zadaniem jest jak najszybsze reagowanie na pojawiający się 
na ekranie obiekt (bodziec docelowy), którym będzie trójkąt lub romb.

Na następnych slajdach zostanie ci zaprezentowany przykładowy 
wygląd planszy jaka będzie użyta w zadaniu i dokładna instrukcja 
przebiegu badania.

Naciśnij spację, żeby kontynuować."""

show_instruction(instruction_1)

if CFG['wersja'] == 'A':
    instruction_2 = """Przez cały czas trwania badania skupiaj wzrok na znaku "+" 
wyświetlanym w centralnej części ekranu.

Podczas eksperymentu w krótkim czasie wyświetlane będą plansze z figurami.

Twoim zadaniem będzie:

- nacisnąć Niebieski przycisk (Lewy Shift) kiedy zauważysz, 
  że na ekranie był obecny trójkąt

- nacisnąć Czerwony przycisk (Prawy Shift), kiedy zauważysz, 
  że na ekranie był obecny romb

Postaraj się wykonywać to zadanie możliwie najszybciej 
i z największą możliwą poprawnością.
Pamiętaj, to bardzo ważne dla pomyślnego przebiegu badania.

Po każdej odpowiedzi otrzymasz informację o jej poprawności.

Naciśnij spację żeby kontynuować."""
else:
    instruction_2 = """Przez cały czas trwania badania skupiaj wzrok na znaku "+" 
wyświetlanym w centralnej części ekranu.

Podczas eksperymentu w krótkim czasie wyświetlane będą plansze z figurami.

Twoim zadaniem będzie:

- nacisnąć Czerwony przycisk (Lewy Shift) kiedy zauważysz, 
  że na ekranie był obecny trójkąt

- nacisnąć Niebieski przycisk (Prawy Shift), kiedy zauważysz, 
  że na ekranie był obecny romb

Postaraj się wykonywać to zadanie możliwie najszybciej 
i z największą możliwą poprawnością.
Pamiętaj, to bardzo ważne dla pomyślnego przebiegu badania.

Po każdej odpowiedzi otrzymasz informację o jej poprawności.

Naciśnij spację żeby kontynuować."""

show_instruction(instruction_2)

if CFG['wersja'] == 'A':
    instruction_3 = f"""Badanie jest podzielone na {CFG['n_blocks']} części: 
po każdej z nich, będziesz miał/a chwilę przerwy.

Pamiętaj, naciskaj Niebieski przycisk, gdy zauważysz trójkąt, 
a Czerwony gdy zauważysz romb.

Na początku rozpoczniesz sesję treningową, 
żeby nauczyć się wykonywać badanie.

Kliknij spację, aby rozpocząć sesję treningową."""
else:
    instruction_3 = f"""Badanie jest podzielone na {CFG['n_blocks']} części: 
po każdej z nich, będziesz miał/a chwilę przerwy.

Pamiętaj, naciskaj Czerwony przycisk, gdy zauważysz trójkąt, 
a Niebieski gdy zauważysz romb.

Na początku rozpoczniesz sesję treningową, 
żeby nauczyć się wykonywać badanie.

Kliknij spację, aby rozpocząć sesję treningową."""

show_instruction(instruction_3)

trial_list_training = create_trial_list()[:CFG['n_training_trials']]

for i, trial_params in enumerate(trial_list_training):
    result = run_trial(trial_params, i + 1, block_number=0, is_practice=True)
    if result:
        results.append(result)

if CFG['wersja'] == 'A':
    instruction_after_training = f"""Koniec sesji treningowej!

Teraz rozpocznie się właściwy eksperyment.
Składa się on z {CFG['n_blocks']} bloków po {CFG['trials_per_block']} prób każdy.
Między blokami będziesz mógł/mogła odpocząć.

Pamiętaj:
- Niebieski przycisk (Lewy Shift) = TRÓJKĄT
- Czerwony przycisk (Prawy Shift) = ROMB

Naciśnij spację aby rozpocząć eksperyment"""
else:
    instruction_after_training = f"""Koniec sesji treningowej!

Teraz rozpocznie się właściwy eksperyment.
Składa się on z {CFG['n_blocks']} bloków po {CFG['trials_per_block']} prób każdy.
Między blokami będziesz mógł/mogła odpocząć.

Pamiętaj:
- Czerwony przycisk (Lewy Shift) = TRÓJKĄT
- Niebieski przycisk (Prawy Shift) = ROMB

Naciśnij spację aby rozpocząć eksperyment"""

show_instruction(instruction_after_training)

trial_list = create_trial_list()

for block in range(CFG['n_blocks']):
    block_start = block * CFG['trials_per_block']
    block_end = block_start + CFG['trials_per_block']
    
    show_instruction(f"BLOK {block + 1} z {CFG['n_blocks']}\n\nNaciśnij spację aby rozpocząć")
    
    for i, trial_params in enumerate(trial_list[block_start:block_end]):
        trial_num = block_start + i + 1
        result = run_trial(trial_params, trial_num, block_number=block + 1, is_practice=False)
        if result:
            results.append(result)
    
    if block < CFG['n_blocks'] - 1:
        show_instruction(f"Przerwa!\n\nUkończono blok {block + 1} z {CFG['n_blocks']}.\n\nMożesz chwilę odpocząć.\n\nNaciśnij spację gdy będziesz gotowy/a")

show_instruction("Koniec eksperymentu!\n\nDziękujemy za udział w badaniu.\n\nNaciśnij spację aby zakończyć")

save_data()
win.close()
core.quit()