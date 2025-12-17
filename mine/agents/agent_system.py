import random
import time
import os

# Ustawienia
GRID_SIZE = 8
NUM_AGENTS = 3
NUM_RESOURCES = 5
BASE_POS = (4, 4)  # Srodek planszy
SIM_STEPS = 50


class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.row, self.col = BASE_POS  # Start w bazie
        self.carry = False
        self.delivered = 0  # Ile zasobow dostarczyl
    
    def choose_action(self):
        """Wybiera akcje zgodnie z polityka"""
        if self.carry:
            # Polityka: idz do bazy (zmniejsz odleglosc Manhattan)
            dr = BASE_POS[0] - self.row
            dc = BASE_POS[1] - self.col
            
            if abs(dr) >= abs(dc):
                return "DOWN" if dr > 0 else "UP"
            else:
                return "RIGHT" if dc > 0 else "LEFT"
        else:
            # Polityka: losowa eksploracja
            return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
    
    def move(self, action):
        """Wykonuje ruch"""
        new_row, new_col = self.row, self.col
        
        if action == "UP":
            new_row -= 1
        elif action == "DOWN":
            new_row += 1
        elif action == "LEFT":
            new_col -= 1
        elif action == "RIGHT":
            new_col += 1
        
        # Sprawdz granice
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            self.row, self.col = new_row, new_col


class Environment:
    def __init__(self):
        self.agents = [Agent(i) for i in range(NUM_AGENTS)]
        self.resources = set()
        self.total_delivered = 0
        
        # Losowe rozmieszczenie zasobow
        while len(self.resources) < NUM_RESOURCES:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if (r, c) != BASE_POS:
                self.resources.add((r, c))
    
    def step(self):
        """Jeden krok symulacji"""
        for agent in self.agents:
            # Wybierz i wykonaj akcje
            action = agent.choose_action()
            agent.move(action)
            
            # Sprawdz podniesienie zasobu
            if not agent.carry and (agent.row, agent.col) in self.resources:
                agent.carry = True
                self.resources.remove((agent.row, agent.col))
            
            # Sprawdz dostarczenie do bazy
            if agent.carry and (agent.row, agent.col) == BASE_POS:
                agent.carry = False
                agent.delivered += 1
                self.total_delivered += 1
    
    def display(self, step_num):
        """Wyswietla plansze"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n=== KROK {step_num} === Dostarczone: {self.total_delivered}")
        print("+" + "-" * (GRID_SIZE * 2 + 1) + "+")
        
        for r in range(GRID_SIZE):
            print("| ", end="")
            for c in range(GRID_SIZE):
                # Co jest na tym polu
                agents_here = [a for a in self.agents if a.row == r and a.col == c]
                
                if agents_here:
                    # Agent (z zasobem = duza litera)
                    a = agents_here[0]
                    symbol = str(a.id) if not a.carry else "*"
                elif (r, c) == BASE_POS:
                    symbol = "B"
                elif (r, c) in self.resources:
                    symbol = "R"
                else:
                    symbol = "."
                
                print(symbol + " ", end="")
            print("|")
        
        print("+" + "-" * (GRID_SIZE * 2 + 1) + "+")
        print("Legenda: B=baza, R=zasob, 0-2=agenci, *=agent z zasobem")
        
        for a in self.agents:
            status = "niesie zasob" if a.carry else "szuka"
            print(f"  Agent {a.id}: ({a.row},{a.col}) {status}, dostarczyl: {a.delivered}")


def main():
    env = Environment()
    
    print("SYSTEM AGENTOWY - ZBIERANIE ZASOBOW")
    print(f"Plansza: {GRID_SIZE}x{GRID_SIZE}")
    print(f"Agenci: {NUM_AGENTS}, Zasoby: {NUM_RESOURCES}")
    input("Nacisnij Enter aby rozpoczac...")
    
    for step in range(SIM_STEPS):
        env.display(step)
        env.step()
        time.sleep(0.3)
        
        # Koniec jesli zebrano wszystkie zasoby
        if env.total_delivered >= NUM_RESOURCES:
            env.display(step + 1)
            print(f"\n*** SUKCES! Wszystkie zasoby dostarczone w {step+1} krokach ***")
            break
    else:
        env.display(SIM_STEPS)
        print(f"\n*** Koniec symulacji. Dostarczone: {env.total_delivered}/{NUM_RESOURCES} ***")


if __name__ == "__main__":
    main()