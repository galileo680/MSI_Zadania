"""
Symulacja algorytmu elekcji tyrana (Bully Algorithm)
Systemy rozproszone - Zadanie 1

Algorytm tyrana:
1. Gdy proces zauważy, że koordynator nie odpowiada, rozpoczyna elekcję
2. Proces wysyła wiadomość ELECTION do wszystkich procesów o wyższych ID
3. Jeśli żaden nie odpowie - proces zostaje koordynatorem i wysyła COORDINATOR
4. Jeśli ktoś odpowie (OK) - proces czeka na ogłoszenie nowego koordynatora
5. Proces o najwyższym ID zawsze wygrywa (stąd nazwa "tyran")
"""

import threading
import time
import random
from enum import Enum


class MessageType(Enum):
    ELECTION = "ELECTION"
    OK = "OK"
    COORDINATOR = "COORDINATOR"


class Process:
    def __init__(self, process_id, network):
        self.id = process_id
        self.network = network
        self.coordinator_id = None
        self.alive = True
        self.in_election = False
        self.lock = threading.Lock()
    
    def send_message(self, target_id, msg_type):
        """Wysyła wiadomość do procesu o podanym ID."""
        target = self.network.get_process(target_id)
        if target and target.alive:
            print(f"  [P{self.id}] -> [P{target_id}]: {msg_type.value}")
            return target.receive_message(self.id, msg_type)
        return False
    
    def receive_message(self, sender_id, msg_type):
        """Odbiera wiadomość od innego procesu."""
        if not self.alive:
            return False
        
        if msg_type == MessageType.ELECTION:
            # Odpowiedz OK i rozpocznij własną elekcję
            print(f"  [P{self.id}] <- [P{sender_id}]: {msg_type.value} (odpowiadam OK)")
            threading.Thread(target=self.start_election, daemon=True).start()
            return True  # OK
        
        elif msg_type == MessageType.COORDINATOR:
            print(f"  [P{self.id}] <- [P{sender_id}]: Nowy koordynator to P{sender_id}")
            with self.lock:
                self.coordinator_id = sender_id
                self.in_election = False
            return True
        
        return True
    
    def start_election(self):
        """Rozpoczyna proces elekcji."""
        with self.lock:
            if self.in_election:
                return
            self.in_election = True
        
        print(f"\n[P{self.id}] Rozpoczynam elekcję!")
        
        # Wyślij ELECTION do procesów o wyższych ID
        higher_processes = [p for p in self.network.processes if p.id > self.id]
        got_response = False
        
        for process in higher_processes:
            if self.send_message(process.id, MessageType.ELECTION):
                got_response = True
        
        if not got_response:
            # Nikt nie odpowiedział - zostaję koordynatorem
            self.become_coordinator()
        else:
            # Czekam na ogłoszenie koordynatora
            print(f"[P{self.id}] Otrzymałem OK, czekam na nowego koordynatora...")
    
    def become_coordinator(self):
        """Ogłasza się jako nowy koordynator."""
        print(f"\n*** [P{self.id}] ZOSTAJĘ NOWYM KOORDYNATOREM ***\n")
        with self.lock:
            self.coordinator_id = self.id
            self.in_election = False
        
        # Powiadom wszystkie procesy
        for process in self.network.processes:
            if process.id != self.id:
                self.send_message(process.id, MessageType.COORDINATOR)
    
    def check_coordinator(self):
        """Sprawdza czy koordynator żyje."""
        if self.coordinator_id is None:
            return False
        coord = self.network.get_process(self.coordinator_id)
        return coord is not None and coord.alive


class Network:
    def __init__(self, num_processes):
        self.processes = []
        for i in range(num_processes):
            self.processes.append(Process(i, self))
        # Na początku koordynatorem jest proces o najwyższym ID
        highest = max(self.processes, key=lambda p: p.id)
        for p in self.processes:
            p.coordinator_id = highest.id
        print(f"Inicjalizacja: Koordynator to P{highest.id}\n")
    
    def get_process(self, process_id):
        """Zwraca proces o podanym ID."""
        for p in self.processes:
            if p.id == process_id:
                return p
        return None
    
    def kill_process(self, process_id):
        """Zabija proces o podanym ID."""
        process = self.get_process(process_id)
        if process:
            process.alive = False
            print(f"\n!!! Proces P{process_id} został zabity !!!\n")
    
    def revive_process(self, process_id):
        """Wskrzesza proces o podanym ID."""
        process = self.get_process(process_id)
        if process:
            process.alive = True
            print(f"\n!!! Proces P{process_id} został wskrzeszony !!!\n")
            # Wskrzeszony proces rozpoczyna elekcję
            process.start_election()


class BullySimulator:
    def __init__(self, num_processes=5, max_events=10):
        self.network = Network(num_processes)
        self.max_events = max_events
        self.event_count = 0
        self.running = True
    
    def run(self):
        """Uruchamia symulację z ograniczoną liczbą zdarzeń."""
        print("=" * 60)
        print("SYMULACJA ALGORYTMU TYRANA (BULLY ALGORITHM)")
        print("=" * 60)
        print(f"Liczba procesów: {len(self.network.processes)}")
        print(f"Maksymalna liczba zdarzeń: {self.max_events}")
        print("=" * 60)
        
        while self.event_count < self.max_events and self.running:
            time.sleep(1)
            self.event_count += 1
            
            print(f"\n--- Zdarzenie {self.event_count}/{self.max_events} ---")
            
            # Losowe zdarzenie
            event = random.choice(["check", "kill_coordinator", "kill_random", "revive"])
            
            if event == "check":
                # Losowy proces sprawdza koordynatora
                alive_processes = [p for p in self.network.processes if p.alive]
                if alive_processes:
                    checker = random.choice(alive_processes)
                    print(f"[P{checker.id}] Sprawdzam koordynatora P{checker.coordinator_id}...")
                    if not checker.check_coordinator():
                        print(f"[P{checker.id}] Koordynator nie odpowiada!")
                        checker.start_election()
                    else:
                        print(f"[P{checker.id}] Koordynator P{checker.coordinator_id} żyje.")
            
            elif event == "kill_coordinator":
                # Zabij obecnego koordynatora
                alive_processes = [p for p in self.network.processes if p.alive]
                if alive_processes:
                    coord_id = alive_processes[0].coordinator_id
                    coord = self.network.get_process(coord_id)
                    if coord and coord.alive:
                        self.network.kill_process(coord_id)
            
            elif event == "kill_random":
                # Zabij losowy proces (nie koordynatora)
                alive_non_coord = [p for p in self.network.processes 
                                   if p.alive and p.id != p.coordinator_id]
                if alive_non_coord:
                    victim = random.choice(alive_non_coord)
                    self.network.kill_process(victim.id)
            
            elif event == "revive":
                # Wskrześ losowy martwy proces
                dead_processes = [p for p in self.network.processes if not p.alive]
                if dead_processes:
                    revived = random.choice(dead_processes)
                    self.network.revive_process(revived.id)
            
            time.sleep(0.5)  # Daj czas na propagację wiadomości
        
        self.print_final_state()
    
    def print_final_state(self):
        """Wypisuje końcowy stan systemu."""
        print("\n" + "=" * 60)
        print("STAN KOŃCOWY SYSTEMU")
        print("=" * 60)
        for p in self.network.processes:
            status = "ŻYWY" if p.alive else "MARTWY"
            coord_info = f"koordynator=P{p.coordinator_id}" if p.coordinator_id else "brak koordynatora"
            is_coord = " [KOORDYNATOR]" if p.alive and p.coordinator_id == p.id else ""
            print(f"P{p.id}: {status}, {coord_info}{is_coord}")
        print("=" * 60)


def main():
    # Symulacja z 5 procesami i maksymalnie 10 zdarzeniami
    simulator = BullySimulator(num_processes=5, max_events=10)
    simulator.run()


if __name__ == "__main__":
    main()