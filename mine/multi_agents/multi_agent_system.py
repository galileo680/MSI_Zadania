import random
import time
import os

GRID_SIZE = 8
NUM_SCOUTS = 2
NUM_COLLECTORS = 2
NUM_RESOURCES = 6
BASE_POS = (4, 4)
SIM_STEPS = 50

# Wspolna tablica - znane zasoby
known_resources = set()


class Scout:
    
    def __init__(self, agent_id):
        self.id = agent_id
        self.row, self.col = BASE_POS
        self.symbol = "S"
    
    def choose_action(self):
        return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
    
    def move(self, action):
        new_row, new_col = self.row, self.col
        if action == "UP": new_row -= 1
        elif action == "DOWN": new_row += 1
        elif action == "LEFT": new_col -= 1
        elif action == "RIGHT": new_col += 1
        
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            self.row, self.col = new_row, new_col
    
    def scan(self, resources):
        if (self.row, self.col) in resources:
            known_resources.add((self.row, self.col))
            return True
        return False


class Collector:
    
    def __init__(self, agent_id):
        self.id = agent_id
        self.row, self.col = BASE_POS
        self.carry = False
        self.target = None
        self.delivered = 0
        self.symbol = "C"
    
    def choose_action(self):
        if self.carry:
            # Idz do bazy
            dr = BASE_POS[0] - self.row
            dc = BASE_POS[1] - self.col
            if abs(dr) >= abs(dc):
                return "DOWN" if dr > 0 else "UP"
            else:
                return "RIGHT" if dc > 0 else "LEFT"
        
        elif known_resources:
            # Idz do najblizszego znanego zasobu
            if not self.target or self.target not in known_resources:
                self.target = min(known_resources, 
                    key=lambda r: abs(r[0]-self.row) + abs(r[1]-self.col))
            
            dr = self.target[0] - self.row
            dc = self.target[1] - self.col
            if abs(dr) >= abs(dc):
                return "DOWN" if dr > 0 else "UP"
            else:
                return "RIGHT" if dc > 0 else "LEFT"
        
        else:
            # Czekaj lub losowa eksploracja w poblizu bazy
            if random.random() < 0.3:
                return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            return "WAIT"
    
    def move(self, action):
        if action == "WAIT":
            return
        
        new_row, new_col = self.row, self.col
        if action == "UP": new_row -= 1
        elif action == "DOWN": new_row += 1
        elif action == "LEFT": new_col -= 1
        elif action == "RIGHT": new_col += 1
        
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            self.row, self.col = new_row, new_col


class Environment:
    def __init__(self):
        self.scouts = [Scout(i) for i in range(NUM_SCOUTS)]
        self.collectors = [Collector(i) for i in range(NUM_COLLECTORS)]
        self.resources = set()
        self.total_delivered = 0
        
        while len(self.resources) < NUM_RESOURCES:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if (r, c) != BASE_POS:
                self.resources.add((r, c))
    
    def step(self):
        # Ruch skautow
        for scout in self.scouts:
            action = scout.choose_action()
            scout.move(action)
            scout.scan(self.resources)
        
        # Ruch zbieraczy
        for collector in self.collectors:
            action = collector.choose_action()
            collector.move(action)
            
            # Podnies zasob
            pos = (collector.row, collector.col)
            if not collector.carry and pos in self.resources:
                collector.carry = True
                collector.symbol = "*"
                self.resources.remove(pos)
                if pos in known_resources:
                    known_resources.remove(pos)
                collector.target = None
            
            # Dostarcz do bazy
            if collector.carry and pos == BASE_POS:
                collector.carry = False
                collector.symbol = "C"
                collector.delivered += 1
                self.total_delivered += 1
    
    def display(self, step_num):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"=== KROK {step_num} === Dostarczone: {self.total_delivered}/{NUM_RESOURCES}")
        print(f"Znane zasoby (blackboard): {len(known_resources)}")
        print("+" + "-" * 17 + "+")
        
        for r in range(GRID_SIZE):
            print("| ", end="")
            for c in range(GRID_SIZE):
                # Kto jest na polu?
                scouts_here = [s for s in self.scouts if s.row == r and s.col == c]
                collectors_here = [c for c in self.collectors if c.row == r and c.col == c]
                
                if scouts_here:
                    symbol = "S"
                elif collectors_here:
                    symbol = collectors_here[0].symbol
                elif (r, c) == BASE_POS:
                    symbol = "B"
                elif (r, c) in known_resources:
                    symbol = "!"  # Znany zasob
                elif (r, c) in self.resources:
                    symbol = "R"  # Nieznany zasob
                else:
                    symbol = "."
                
                print(symbol + " ", end="")
            print("|")
        
        print("+" + "-" * 17 + "+")
        print("S=skaut, C=zbieracz, *=zbieracz z zasobem")
        print("R=nieznany zasob, !=znany zasob, B=baza")


def main():
    global known_resources
    known_resources = set()
    
    env = Environment()
    
    print("SYSTEM AGENTOWY - SKAUCI I ZBIERACZE")
    print(f"Skauci: {NUM_SCOUTS}, Zbieracze: {NUM_COLLECTORS}")
    print(f"Zasoby: {NUM_RESOURCES}")
    input("Enter aby rozpoczac...")
    
    for step in range(SIM_STEPS):
        env.display(step)
        env.step()
        time.sleep(0.3)
        
        if env.total_delivered >= NUM_RESOURCES:
            env.display(step + 1)
            print(f"\n*** SUKCES w {step+1} krokach! ***")
            break
    else:
        env.display(SIM_STEPS)
        print(f"\n*** Koniec. Zebrano: {env.total_delivered}/{NUM_RESOURCES} ***")


if __name__ == "__main__":
    main()