from collections import deque

# ----------------------------
# Kapazitätstabelle
# Einheit = Aufträge pro Tag
# 80% von max. Kapazität
# ----------------------------
lookup_capa_per_day = {
    "Analyselabor": 20,         #Annahme (keine aktuellen Daten)
    "AOI": 27,
    "Bohren & Fräsen": 50,
    "Dumpresistor": 3,
    "Dünnschichtlabor": 6,
    "Endkontrolle Hilfsp": 31,
    "Endprüfung Visuell": 17,
    "Extern Allgemein": 20,     #Annahme (keine aktuellen Daten)
    "Extern Hofstetter": 20,    #Annahme (keine aktuellen Daten)
    "Extern MicroContact": 20,  #Annahme (keine aktuellen Daten)
    "Fotochemie": 147,
    "Fotochemie Cu-Reduzieren": 22,
    "Gal Cu Yasmin": 16,
    "Gal Nickel Gold": 10,
    "Galvanik Hilfsp": 34,
    "IST Tester": 16,
    "Lager": 30,
    "Laser": 44,
    "Laser CO2": 6,
    "Plasma": 25,
    "Presserei": 55,
    "Presserei Hilfsp": 30,
    "Schlifflabor": 20,        #Annahme (keine aktuellen Daten)
    "Siebdruck": 37,
    "XY-Messanlage": 14,
    "Zwischenkontrolle": 27,
}

class Workplace:
    def __init__(self, name, capa_per_day):
        self.name = name
        self.location = None
        self.capa_per_day = capa_per_day
        self.input_wip = deque()
        self.output_wip = deque()

    def run(self):
        """

        :return:
        """
        self.output_wip = self.input_wip[:self.capa_per_day]
        self.input_wip =  self.input_wip[self.capa_per_day:]
        return None

class ProductionOrder:
    def __init__(self, id, operationcycles):
        self.id = id
        self.operationcycles = operationcycles
        self.current_step = 10
        self.current_dispatchdep = None
        self.next_step = 0
        self.next_dispatchdep = None
        self.age = 0