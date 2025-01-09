from pyfirmata2 import Arduino, OUTPUT
import time

#makkelijk aanpasbare variabelen
min_wachtrij = 0
max_wachtrij = 160
klanten_per_10_minuten = 30
debounce_delay = 0.05
wachtrij = 0 # bij start van attractie]
# hoe vaak data moet worden omgezet in bericht richting database
overzicht_interval = 3 # in seconden

board = Arduino(Arduino.AUTODETECT)
board.samplingOn(100)


def knop_1_callback(value):
    global knop_1_value
    knop_1_value = value

def knop_2_callback(value):
    global knop_2_value
    knop_2_value = value

def update_leds(wachtrij):
    if wachtrij < (0.5*max_wachtrij):
        led_rood.write(0)
        led_geel.write(0)
        led_groen.write(1)
    elif wachtrij < max_wachtrij:
        led_rood.write(0)
        led_geel.write(1)
        led_groen.write(0)
    else:
        led_rood.write(1)
        led_geel.write(0)
        led_groen.write(0)

def display_number(nummer):
    if nummer not in nummers:
        raise ValueError(f"Ongeldig nummer: {nummer}.")
    
    # Zet de juiste segmenten aan/uit
    for pin, state in zip(segments, nummers[nummer]):
        board.digital[pin].write(1 if state else 0)

def tijd_7_segment_display():
    # Bereken het nummer voor de tijd voor de 7-segment display
    nummer_voor_display = round(wachtrij / klanten_per_10_minuten)
    nummer_voor_display = min(max(nummer_voor_display, 0), 9)  # Limiteer tot 0-9
    display_number(nummer_voor_display)


# 7-segment configuratie
segments = [7, 8, 9, 10, 11, 12, 13]
nummers = {
    0: [True, True, True, True, True, True, False],
    1: [False, True, True, False, False, False, False],
    2: [True, True, False, True, True, False, True],
    3: [True, True, True, True, False, False, True],
    4: [False, True, True, False, False, True, True],
    5: [True, False, True, True, False, True, True],
    6: [True, False, True, True, True, True, True],
    7: [True, True, True, False, False, False, False],
    8: [True, True, True, True, True, True, True],
    9: [True, True, True, True, False, True, True]
}


# Stel segmenten in als output
for pin in segments:
    board.digital[pin].mode = OUTPUT

knop_1_pin = board.get_pin('d:2:i')
knop_1_pin.register_callback(knop_1_callback)
knop_1_pin.enable_reporting()

knop_2_pin = board.get_pin('d:3:i')
knop_2_pin.register_callback(knop_2_callback)
knop_2_pin.enable_reporting()

led_rood = board.get_pin('d:4:o')
led_geel = board.get_pin('d:5:o')
led_groen = board.get_pin('d:6:o')

knop_1_value = 0
last_knop_1_value = 0
knop_2_value = 0
last_knop_2_value = 0
vorige_wachtrij = 0



# voor 7-segment display

#start voor debounce timer
start_debounce = time.time()
start_overzicht_interval = time.time()
while True:
    if time.time() - start_debounce < debounce_delay:
        if knop_1_value != last_knop_1_value:
            if knop_1_value == 1:
                wachtrij = min(wachtrij + 1, max_wachtrij)
                # min geeft aan dat het de kleinste waarde retourneert van:
                # of: wachtrij + 1
                # of: max_wachtrij
                print(f"wachtrij: {wachtrij}")  
            last_knop_1_value = knop_1_value
            update_leds(wachtrij)

        if knop_2_value != last_knop_2_value:
            if knop_2_value == 1:
                wachtrij = max(wachtrij - 1, min_wachtrij)
                # max geeft aan dat de grootste waarde geretourneert word:
                # of: wachtrij - 1
                # of: min_wachtrij
                print(f"wachtrij: {wachtrij}")
            last_knop_2_value = knop_2_value
            update_leds(wachtrij)
        start_debounce = time.time()

        tijd_7_segment_display()
    if (time.time() - start_overzicht_interval) >= overzicht_interval:
        print(f"lengte wachtrij: {wachtrij})")
        
        # 100%
        if wachtrij == max_wachtrij:
            print("De wachtrij is vol")
            if vorige_wachtrij != 160:
                print("Overweeg andere actie te ondernemen")
        # 90%
        # alle blokjes volgen zelfde principe
        elif wachtrij >= (max_wachtrij * 0.9):
            # altijd huidige status van wachtrij printen
            print("De wachtrij is bijna vol")
            if vorige_wachtrij < (max_wachtrij * 0.9):
                # 
                print("Zet maximaal personeel in")
            elif vorige_wachtrij == max_wachtrij:
                print("De wachtrij is niet meer vol")
        # 60%
        elif wachtrij >= (max_wachtrij * 0.6):
            print("De wachtrij is redelijk druk")
            if vorige_wachtrij < (max_wachtrij * 0.6):
                print("Zet extra personeel in")
            elif vorige_wachtrij >= (max_wachtrij * 0.6):
                print("Overweeg personeel af te schalen")
        # 20%
        elif wachtrij >= (max_wachtrij * 0.2):
            print("De wachtrij is bijna leeg")
            if vorige_wachtrij < (max_wachtrij * 0.2):
                print("Zet normaal hoeveelheid personeel in")
            elif vorige_wachtrij >= (max_wachtrij * 0.6):
                print("Overweeg personeel af te schalen tot minimum")
        # 0%
        else:
            print("De wachtrij is leeg")
            if not(vorige_wachtrij <= (max_wachtrij * 0.2)):
                print("Overweeg extra actie te ondernemen")
        start_overzicht_interval = time.time()
        vorige_wachtrij = wachtrij

            


        vorige_wachtrij = wachtrij

