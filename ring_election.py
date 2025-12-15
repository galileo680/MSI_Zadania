"""
Symulacja algorytmu elekcji pierścieniowej (Ring Election Algorithm)
Systemy rozproszone - Zadanie 2

Algorytm pierścieniowy:
1. Procesy są ułożone w logiczny pierścień (każdy zna swojego następnika)
2. Gdy proces wykryje brak koordynatora, wysyła wiadomość ELECTION z własnym ID
3. Każdy proces dodaje swoje ID do wiadomości i przekazuje dalej
4. Gdy wiadomość wróci do inicjatora, wybierany jest proces o najwyższym ID
5. Inicjator wysyła wiadomość COORDINATOR z ID zwycięzcy
"""

import time
import random


class Process:
    def __init__(self, process_id):
        self.id = process_id
        self.next_process = None  # następnik w pierścieniu
        self.coordinator_id = None
        self.alive = True
    
    def find_next_alive(self):
        """Znajduje najbliższy żywy proces w pierścieniu."""
        next_p = self.next_process
        visited = set()
        while next_p and next_p.id not in visited:
            if next_p.alive:
                return next_p
            visited.add(next_p.id)
            next_p = next_p.next_process
        return None
    
    def start_election(self):
        """Rozpoczyna elekcję - wysyła wiadomość z własnym ID."""
        if not self.alive:
            return
        
        print(f"\n[P{self.id}] Rozpoczynam elekcję pierścieniową!")
        self.send_election([self.id])
    
    def send_election(self, candidates):
        """Wysyła listę kandydatów do następnika."""
        next_alive = self.find_next_alive()
        if next_alive:
            print(f"  [P{self.id}] -> [P{next_alive.id}]: ELECTION {candidates}")
            next_alive.receive_election(candidates, self.id)
    
    def receive_election(self, candidates, initiator_id):
        """Odbiera wiadomość elekcyjną."""
        if not self.alive:
            return
        
        # Jeśli moje ID jest już na liście - wiadomość okrążyła pierścień
        if self.id in candidates:
            # Wybieram proces o najwyższym ID
            winner = max(candidates)
            print(f"\n[P{self.id}] Wiadomość okrążyła pierścień. Kandydaci: {candidates}")
            print(f"*** Zwycięzca elekcji: P{winner} ***\n")
            self.send_coordinator(winner)
        else:
            # Dodaję siebie do listy i przekazuję dalej
            candidates.append(self.id)
            self.send_election(candidates)
    
    def send_coordinator(self, winner_id):
        """Wysyła informację o nowym koordynatorze."""
        self.coordinator_id = winner_id
        next_alive = self.find_next_alive()
        if next_alive and next_alive.coordinator_id != winner_id:
            print(f"  [P{self.id}] -> [P{next_alive.id}]: COORDINATOR P{winner_id}")
            next_alive.receive_coordinator(winner_id)
    
    def receive_coordinator(self, winner_id):
        """Odbiera informację o nowym koordynatorze."""
        if not self.alive:
            return
        
        if self.coordinator_id != winner_id:
            self.coordinator_id = winner_id
            print(f"  [P{self.id}] przyjął koordynatora P{winner_id}")
            self.send_coordinator(winner_id)


class RingNetwork:
    def __init__(self, num_processes):
        # Tworzę procesy
        self.processes = [Process(i) for i in range(num_processes)]
        
        # Łączę w pierścień: 0 -> 1 -> 2 -> ... -> n-1 -> 0
        for i in range(num_processes):
            self.processes[i].next_process = self.processes[(i + 1) % num_processes]
        
        # Początkowy koordynator - najwyższe ID
        initial_coord = num_processes - 1
        for p in self.processes:
            p.coordinator_id = initial_coord
        
        print(f"Pierścień: {' -> '.join(f'P{p.id}' for p in self.processes)} -> P0")
        print(f"Początkowy koordynator: P{initial_coord}\n")
    
    def kill_process(self, process_id):
        """Zabija proces."""
        self.processes[process_id].alive = False
        print(f"\n!!! Proces P{process_id} został zabity !!!")
    
    def revive_process(self, process_id):
        """Wskrzesza proces."""
        self.processes[process_id].alive = True
        print(f"\n!!! Proces P{process_id} został wskrzeszony !!!")


class RingSimulator:
    def __init__(self, num_processes=5, max_events=8):
        self.network = RingNetwork(num_processes)
        self.max_events = max_events
    
    def run(self):
        print("=" * 60)
        print("SYMULACJA ALGORYTMU PIERŚCIENIOWEGO")
        print("=" * 60)
        
        for event_num in range(1, self.max_events + 1):
            time.sleep(1)
            print(f"\n--- Zdarzenie {event_num}/{self.max_events} ---")
            
            alive = [p for p in self.network.processes if p.alive]
            dead = [p for p in self.network.processes if not p.alive]
            
            event = random.choice(["check", "kill", "revive"] if dead else ["check", "kill"])
            
            if event == "check" and alive:
                checker = random.choice(alive)
                coord = self.network.processes[checker.coordinator_id]
                print(f"[P{checker.id}] Sprawdzam koordynatora P{checker.coordinator_id}...")
                if not coord.alive:
                    print(f"[P{checker.id}] Koordynator nie żyje!")
                    checker.start_election()
                else:
                    print(f"[P{checker.id}] Koordynator żyje.")
            
            elif event == "kill" and alive:
                victim = random.choice(alive)
                self.network.kill_process(victim.id)
            
            elif event == "revive" and dead:
                revived = random.choice(dead)
                self.network.revive_process(revived.id)
        
        self.print_final_state()
    
    def print_final_state(self):
        print("\n" + "=" * 60)
        print("STAN KOŃCOWY")
        print("=" * 60)
        for p in self.network.processes:
            status = "ŻYWY" if p.alive else "MARTWY"
            is_coord = " [KOORDYNATOR]" if p.alive and p.coordinator_id == p.id else ""
            print(f"P{p.id}: {status}, koordynator=P{p.coordinator_id}{is_coord}")


if __name__ == "__main__":
    simulator = RingSimulator(num_processes=5, max_events=8)
    simulator.run()