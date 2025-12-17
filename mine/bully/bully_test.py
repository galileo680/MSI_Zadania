import unittest
import time
from bully import Process, Network, MessageType


class TestProcess(unittest.TestCase):
    
    def setUp(self):
        self.network = Network(5)
    
    def test_process_creation(self):
        process = self.network.processes[0]
        self.assertEqual(process.id, 0)
        self.assertTrue(process.alive)
        self.assertEqual(process.coordinator_id, 4)
    
    def test_initial_coordinator(self):
        for p in self.network.processes:
            self.assertEqual(p.coordinator_id, 4)
    
    def test_process_alive_by_default(self):
        for p in self.network.processes:
            self.assertTrue(p.alive)


class TestNetwork(unittest.TestCase):
    
    def setUp(self):
        self.network = Network(5)
    
    def test_network_size(self):
        self.assertEqual(len(self.network.processes), 5)
    
    def test_get_process(self):
        process = self.network.get_process(2)
        self.assertIsNotNone(process)
        self.assertEqual(process.id, 2)
    
    def test_get_nonexistent_process(self):
        process = self.network.get_process(99)
        self.assertIsNone(process)
    
    def test_kill_process(self):
        self.network.kill_process(2)
        process = self.network.get_process(2)
        self.assertFalse(process.alive)
    
    def test_revive_process(self):
        self.network.kill_process(2)
        self.network.revive_process(2)
        process = self.network.get_process(2)
        self.assertTrue(process.alive)


class TestElection(unittest.TestCase):
    
    def setUp(self):
        self.network = Network(5)
    
    def test_check_coordinator_alive(self):
        process = self.network.processes[0]
        self.assertTrue(process.check_coordinator())
    
    def test_check_coordinator_dead(self):
        self.network.kill_process(4)
        process = self.network.processes[0]
        self.assertFalse(process.check_coordinator())
    
    def test_election_highest_wins(self):
        self.network.kill_process(4)
        
        self.network.processes[1].start_election()
        time.sleep(0.5)
        
        for p in self.network.processes:
            if p.alive:
                self.assertEqual(p.coordinator_id, 3)
    
    def test_election_with_multiple_dead(self):
        self.network.kill_process(4)
        self.network.kill_process(3)  
        
        self.network.processes[0].start_election()
        time.sleep(0.5)
        
        for p in self.network.processes:
            if p.alive:
                self.assertEqual(p.coordinator_id, 2)
    
    def test_lowest_process_starts_election(self):
        self.network.kill_process(4)
        
        self.network.processes[0].start_election()
        time.sleep(0.5)
        
        self.assertEqual(self.network.processes[0].coordinator_id, 3)


class TestMessagePassing(unittest.TestCase):
    
    def setUp(self):
        self.network = Network(5)
    
    def test_send_to_alive_process(self):
        sender = self.network.processes[0]
        result = sender.send_message(1, MessageType.COORDINATOR)
        self.assertTrue(result)
    
    def test_send_to_dead_process(self):
        self.network.kill_process(1)
        sender = self.network.processes[0]
        result = sender.send_message(1, MessageType.COORDINATOR)
        self.assertFalse(result)
    
    def test_dead_process_cannot_receive(self):
        self.network.kill_process(1)
        dead_process = self.network.processes[1]
        result = dead_process.receive_message(0, MessageType.ELECTION)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)