"""
Testy jednostkowe dla algorytmu tyrana - wersja asynchroniczna
30% pokrycia kodu
"""

import unittest
import asyncio
import bully_async as ba


def reset_globals():
    """Resetuje globalne zmienne przed każdym testem."""
    ba.PROCESS_IDS = [1, 2, 3, 4]
    ba.STEP_SEC = 0.1
    ba.HEARTBEAT_INTERVAL = 0.3
    ba.HEARTBEAT_TIMEOUT = 1.0
    ba.PROB_CRASH = 0.0
    ba.PROB_RECOVER = 0.0
    ba.SIM_STEPS = 10
    ba.RANDOM_SEED = 42
    ba.STRICT_BULLY_ON_RECOVERY = True
    ba.mailboxes = {pid: asyncio.Queue() for pid in ba.PROCESS_IDS}
    ba.alive = {pid: True for pid in ba.PROCESS_IDS}
    ba.current_leader = None
    ba.last_heartbeat = None
    ba.leader_lock = asyncio.Lock()
    ba.start_time_monotonic = None


class TestSend(unittest.TestCase):
    """Testy funkcji send"""

    def test_send_puts_message_in_queue(self):
        """send() dodaje wiadomość do kolejki odbiorcy"""
        async def run():
            reset_globals()
            await ba.send(2, ("ELECTION", 1))
            self.assertEqual(ba.mailboxes[2].qsize(), 1)
        asyncio.run(run())

    def test_send_correct_message(self):
        """send() dodaje poprawną wiadomość"""
        async def run():
            reset_globals()
            await ba.send(3, ("COORDINATOR", 4))
            msg = await ba.mailboxes[3].get()
            self.assertEqual(msg, ("COORDINATOR", 4))
        asyncio.run(run())


class TestBroadcast(unittest.TestCase):
    """Testy funkcji broadcast"""

    def test_broadcast_sends_to_all(self):
        """broadcast() wysyła do wszystkich procesów"""
        async def run():
            reset_globals()
            await ba.broadcast(("HEARTBEAT", 4))
            for pid in ba.PROCESS_IDS:
                self.assertEqual(ba.mailboxes[pid].qsize(), 1)
        asyncio.run(run())


class TestCheckAndMaybeStartElection(unittest.TestCase):
    """Testy funkcji check_and_maybe_start_election"""

    def test_dead_process_does_nothing(self):
        """Martwy proces nie rozpoczyna elekcji"""
        async def run():
            reset_globals()
            ba.alive[2] = False
            await ba.check_and_maybe_start_election(2)
            # Skrzynki powinny byc puste
            for pid in ba.PROCESS_IDS:
                self.assertEqual(ba.mailboxes[pid].qsize(), 0)
        asyncio.run(run())

    def test_highest_becomes_leader(self):
        """Najwyzszy proces zostaje liderem"""
        async def run():
            reset_globals()
            await ba.check_and_maybe_start_election(4)
            self.assertEqual(ba.current_leader, 4)
        asyncio.run(run())

    def test_lower_sends_election_to_higher(self):
        """Nizszy proces wysyła ELECTION do wyzszych"""
        async def run():
            reset_globals()
            await ba.check_and_maybe_start_election(1)
            # P2, P3, P4 powinny miec wiadomosci ELECTION
            for pid in [2, 3, 4]:
                self.assertGreater(ba.mailboxes[pid].qsize(), 0)
        asyncio.run(run())

    def test_skips_dead_processes(self):
        """Elekcja pomija martwe procesy"""
        async def run():
            reset_globals()
            ba.alive[3] = False
            ba.alive[4] = False
            await ba.check_and_maybe_start_election(1)
            # Tylko P2 powinien dostać ELECTION
            self.assertGreater(ba.mailboxes[2].qsize(), 0)
            self.assertEqual(ba.mailboxes[3].qsize(), 0)
            self.assertEqual(ba.mailboxes[4].qsize(), 0)
        asyncio.run(run())


class TestHandleMailbox(unittest.TestCase):
    """Testy funkcji handle_mailbox"""

    def test_dead_process_clears_mailbox(self):
        """Martwy proces oproznia skrzynke"""
        async def run():
            reset_globals()
            await ba.send(2, ("ELECTION", 1))
            await ba.send(2, ("COORDINATOR", 4))
            ba.alive[2] = False
            await ba.handle_mailbox(2)
            self.assertEqual(ba.mailboxes[2].qsize(), 0)
        asyncio.run(run())

    def test_coordinator_sets_leader(self):
        """COORDINATOR ustawia lidera"""
        async def run():
            reset_globals()
            await ba.send(1, ("COORDINATOR", 4))
            await ba.handle_mailbox(1)
            self.assertEqual(ba.current_leader, 4)
        asyncio.run(run())

    def test_election_response_ok(self):
        """Wyzszy proces odpowiada OK na ELECTION"""
        async def run():
            reset_globals()
            await ba.send(3, ("ELECTION", 1))
            await ba.handle_mailbox(3)
            # P1 powinien dostać OK
            self.assertGreater(ba.mailboxes[1].qsize(), 0)
        asyncio.run(run())


class TestSimTime(unittest.TestCase):
    """Testy funkcji sim_time"""

    def test_sim_time_zero_when_not_started(self):
        """sim_time() zwraca 0 gdy symulacja nie wystartowala"""
        reset_globals()
        ba.start_time_monotonic = None
        self.assertEqual(ba.sim_time(), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)