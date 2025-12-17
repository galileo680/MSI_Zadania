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
    
    def test_process_not_in_election_initially(self):
        for p in self.network.processes:
            self.assertFalse(p.in_election)


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
    
    def test_kill_nonexistent_process(self):
        # Should not raise exception
        self.network.kill_process(99)
    
    def test_revive_nonexistent_process(self):
        # Should not raise exception
        self.network.revive_process(99)
    
    def test_processes_have_correct_ids(self):
        for i, p in enumerate(self.network.processes):
            self.assertEqual(p.id, i)
    
    def test_highest_id_is_coordinator(self):
        network = Network(3)
        for p in network.processes:
            self.assertEqual(p.coordinator_id, 2)


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
    
    def test_check_coordinator_none(self):
        process = self.network.processes[0]
        process.coordinator_id = None
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
    
    def test_highest_alive_becomes_coordinator(self):
        # Kill all except P0 and P1
        self.network.kill_process(4)
        self.network.kill_process(3)
        self.network.kill_process(2)
        
        self.network.processes[0].start_election()
        time.sleep(0.5)
        
        self.assertEqual(self.network.processes[0].coordinator_id, 1)
        self.assertEqual(self.network.processes[1].coordinator_id, 1)
    
    def test_single_process_becomes_coordinator(self):
        # Kill all except P0
        self.network.kill_process(4)
        self.network.kill_process(3)
        self.network.kill_process(2)
        self.network.kill_process(1)
        
        self.network.processes[0].start_election()
        time.sleep(0.5)
        
        self.assertEqual(self.network.processes[0].coordinator_id, 0)
    
    def test_in_election_flag_set(self):
        self.network.kill_process(4)
        process = self.network.processes[0]
        
        # Start election in separate thread
        process.start_election()
        
        # After election completes, flag should be reset
        time.sleep(0.5)
        self.assertFalse(process.in_election)
    
    def test_election_not_started_twice(self):
        self.network.kill_process(4)
        process = self.network.processes[0]
        
        process.start_election()
        initial_coordinator = process.coordinator_id
        time.sleep(0.3)
        
        # Try to start again
        process.start_election()
        time.sleep(0.3)
        
        # Should have same result
        self.assertEqual(process.coordinator_id, 3)


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
    
    def test_receive_coordinator_updates_state(self):
        process = self.network.processes[0]
        process.coordinator_id = None
        process.in_election = True
        
        result = process.receive_message(3, MessageType.COORDINATOR)
        
        self.assertTrue(result)
        self.assertEqual(process.coordinator_id, 3)
        self.assertFalse(process.in_election)
    
    def test_receive_election_from_lower_id(self):
        # P3 receives ELECTION from P1 (lower ID)
        process = self.network.processes[3]
        result = process.receive_message(1, MessageType.ELECTION)
        
        self.assertTrue(result)
    
    def test_send_to_nonexistent_process(self):
        sender = self.network.processes[0]
        result = sender.send_message(99, MessageType.ELECTION)
        self.assertFalse(result)
    
    def test_send_election_triggers_response(self):
        # P1 sends ELECTION to P3
        sender = self.network.processes[1]
        result = sender.send_message(3, MessageType.ELECTION)
        
        # P3 should respond (return True means OK)
        self.assertTrue(result)


class TestBecomeCoordinator(unittest.TestCase):
    
    def setUp(self):
        self.network = Network(5)
    
    def test_become_coordinator_sets_self(self):
        process = self.network.processes[2]
        self.network.kill_process(4)
        self.network.kill_process(3)
        
        process.become_coordinator()
        
        self.assertEqual(process.coordinator_id, 2)
    
    def test_become_coordinator_resets_election_flag(self):
        process = self.network.processes[2]
        process.in_election = True
        self.network.kill_process(4)
        self.network.kill_process(3)
        
        process.become_coordinator()
        
        self.assertFalse(process.in_election)
    
    def test_become_coordinator_notifies_others(self):
        self.network.kill_process(4)
        self.network.kill_process(3)
        
        process = self.network.processes[2]
        process.become_coordinator()
        time.sleep(0.3)
        
        # All alive processes should know P2 is coordinator
        for p in self.network.processes:
            if p.alive:
                self.assertEqual(p.coordinator_id, 2)


class TestEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.network = Network(5)
    
    def test_revive_starts_election(self):
        self.network.kill_process(4)
        
        # P3 becomes coordinator
        self.network.processes[0].start_election()
        time.sleep(0.5)
        self.assertEqual(self.network.processes[0].coordinator_id, 3)
        
        # Revive P4 - should start new election
        self.network.revive_process(4)
        time.sleep(0.5)
        
        # P4 should be coordinator again
        self.assertEqual(self.network.processes[4].coordinator_id, 4)
    
    def test_network_with_one_process(self):
        network = Network(1)
        self.assertEqual(len(network.processes), 1)
        self.assertEqual(network.processes[0].coordinator_id, 0)
    
    def test_network_with_two_processes(self):
        network = Network(2)
        self.assertEqual(network.processes[0].coordinator_id, 1)
        self.assertEqual(network.processes[1].coordinator_id, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)