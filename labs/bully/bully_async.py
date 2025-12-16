"""
Algorytm tyrana (Bully Algorithm) - wersja asynchroniczna
Kod profesora - systemy rozproszone
"""

import asyncio
import random
from typing import Dict, Optional, Tuple, List

# Parametry domyslne 
PROCESS_IDS: List[int] = [1, 2, 3, 4]
STEP_SEC: float = 0.1
HEARTBEAT_INTERVAL: float = 0.3
HEARTBEAT_TIMEOUT: float = 1.0
PROB_CRASH: float = 0.02
PROB_RECOVER: float = 0.01
SIM_STEPS: int = 15 # 400
RANDOM_SEED: int = 42
STRICT_BULLY_ON_RECOVERY: bool = True

# Zmienne systemowe
mailboxes: Dict[int, asyncio.Queue] = {}
alive: Dict[int, bool] = {}
last_heartbeat: Optional[float] = None
current_leader: Optional[int] = None
leader_lock: asyncio.Lock = None
start_time_monotonic: Optional[float] = None


def sim_time() -> float:
    """Czas symulacji wzgledem startu petli."""
    if start_time_monotonic is None:
        return 0.0
    return round(asyncio.get_running_loop().time() - start_time_monotonic, 2)


async def send(to: int, msg: Tuple[str, int]):
    """Wysyla wiadomosc do procesu."""
    await mailboxes[to].put(msg)


async def broadcast(msg: Tuple[str, int]):
    """Wysyla wiadomosc do wszystkich procesow."""
    for p in PROCESS_IDS:
        await send(p, msg)


def log(msg: str):
    """Loguje wiadomosc z timestampem."""
    print(f"[{sim_time():5.2f}] {msg}")


async def check_and_maybe_start_election(pid: int):
    """Sprawdza czy nalezy rozpoczac elekcje i ewentualnie ja rozpoczyna."""
    global current_leader, last_heartbeat
    if not alive.get(pid, False):
        return

    async with leader_lock:
        no_leader = current_leader is None
        hb_timed_out = (last_heartbeat is None) or (sim_time() - last_heartbeat > HEARTBEAT_TIMEOUT)

    if no_leader or hb_timed_out:
        higher = [p for p in PROCESS_IDS if p > pid and alive.get(p, False)]
        if not higher:
            async with leader_lock:
                current_leader = pid
                last_heartbeat = sim_time()
            await broadcast(("COORDINATOR", pid))
            log(f"Proces {pid}: oglaszam sie LIDEREM (brak silniejszych zywych)")
        else:
            for p in higher:
                await send(p, ("ELECTION", pid))
            log(f"Proces {pid}: rozpoczal ELECTION -> wyslano do {higher}")


async def handle_mailbox(pid: int):
    """Obsluguje wszystkie wiadomosci w skrzynce procesu."""
    global current_leader, last_heartbeat

    if not alive.get(pid, False):
        try:
            while True:
                mailboxes[pid].get_nowait()
        except asyncio.QueueEmpty:
            pass
        return

    while True:
        try:
            typ, frm = mailboxes[pid].get_nowait()
        except asyncio.QueueEmpty:
            break

        if typ == "ELECTION":
            if pid > frm and alive.get(pid, False):
                await send(frm, ("OK", pid))
                log(f"Proces {pid}: OTRZYMAL ELECTION od {frm} -> wysyla OK i sam zaczyna wybory")
                await check_and_maybe_start_election(pid)
            else:
                log(f"Proces {pid}: OTRZYMAL ELECTION od {frm}, ale nie odpowiada (nizsze ID lub niezywy)")

        elif typ == "OK":
            log(f"Proces {pid}: OTRZYMAL OK od {frm} -> czeka na COORDINATOR")

        elif typ == "COORDINATOR":
            async with leader_lock:
                current_leader = frm
                last_heartbeat = sim_time()
            log(f"Proces {pid}: OTRZYMAL COORDINATOR -> nowy lider = {frm}")

        elif typ == "HEARTBEAT":
            async with leader_lock:
                if current_leader == frm or current_leader is None:
                    current_leader = frm
                    last_heartbeat = sim_time()
            log(f"Proces {pid}: OTRZYMAL HEARTBEAT od lidera {frm}")


async def process_task(pid: int, stop_event: asyncio.Event):
    """Glowna petla procesu."""
    await asyncio.sleep(STEP_SEC)
    await check_and_maybe_start_election(pid)

    while not stop_event.is_set():
        await handle_mailbox(pid)
        await check_and_maybe_start_election(pid)
        await asyncio.sleep(STEP_SEC)


async def leader_heartbeat_task(stop_event: asyncio.Event):
    """Wysyla heartbeat od lidera."""
    global last_heartbeat
    last_sent = 0.0
    while not stop_event.is_set():
        await asyncio.sleep(STEP_SEC)
        async with leader_lock:
            leader = current_leader
        if leader is not None and alive.get(leader, False):
            if sim_time() - last_sent >= HEARTBEAT_INTERVAL:
                await broadcast(("HEARTBEAT", leader))
                last_sent = sim_time()
                async with leader_lock:
                    last_heartbeat = sim_time()
                log(f"Lider {leader}: wysyła HEARTBEAT")


async def faults_and_recoveries_task(stop_event: asyncio.Event):
    """Generator awarii/napraw w krokach symulacji."""
    steps = 0
    while not stop_event.is_set() and steps < SIM_STEPS:
        for pid in PROCESS_IDS:
            if alive.get(pid, False) and random.random() < PROB_CRASH:
                alive[pid] = False
                log(f"!!! Proces {pid} ULEGL AWARII !!!")
                async with leader_lock:
                    if current_leader == pid:
                        log(f"!!! Lider {pid} padl — reszta wykryje po timeoutcie !!!")
        for pid in PROCESS_IDS:
            if not alive.get(pid, True) and random.random() < PROB_RECOVER:
                alive[pid] = True
                log(f">>> Proces {pid} odzyskal sprawnosc")
                if STRICT_BULLY_ON_RECOVERY:
                    await check_and_maybe_start_election(pid)
        steps += 1
        await asyncio.sleep(STEP_SEC)

    stop_event.set()


async def main():
    """Glowna funkcja symulacji."""
    global mailboxes, alive, current_leader, last_heartbeat, start_time_monotonic, leader_lock

    random.seed(RANDOM_SEED)
    mailboxes = {pid: asyncio.Queue() for pid in PROCESS_IDS}
    alive = {pid: True for pid in PROCESS_IDS}
    current_leader = None
    last_heartbeat = None
    leader_lock = asyncio.Lock()
    start_time_monotonic = asyncio.get_running_loop().time()

    stop_event = asyncio.Event()

    tasks = []
    for pid in PROCESS_IDS:
        tasks.append(asyncio.create_task(process_task(pid, stop_event), name=f"proc-{pid}"))
    tasks.append(asyncio.create_task(leader_heartbeat_task(stop_event), name="heartbeat"))
    tasks.append(asyncio.create_task(faults_and_recoveries_task(stop_event), name="faults"))

    await stop_event.wait()

    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def start(
    *,
    sim_steps: Optional[int] = None,
    crash: Optional[float] = None,
    recover: Optional[float] = None,
    heartbeat_interval: Optional[float] = None,
    heartbeat_timeout: Optional[float] = None,
    step_sec: Optional[float] = None,
    strict_bully_on_recovery: Optional[bool] = None,
    process_ids: Optional[List[int]] = None,
    seed: Optional[int] = None,
):
    """Uruchamia symulacje z podanymi parametrami."""
    global SIM_STEPS, PROB_CRASH, PROB_RECOVER, HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT
    global STEP_SEC, STRICT_BULLY_ON_RECOVERY, PROCESS_IDS, RANDOM_SEED

    if sim_steps is not None:
        SIM_STEPS = int(sim_steps)
    if crash is not None:
        PROB_CRASH = float(crash)
    if recover is not None:
        PROB_RECOVER = float(recover)
    if heartbeat_interval is not None:
        HEARTBEAT_INTERVAL = float(heartbeat_interval)
    if heartbeat_timeout is not None:
        HEARTBEAT_TIMEOUT = float(heartbeat_timeout)
    if step_sec is not None:
        STEP_SEC = float(step_sec)
    if strict_bully_on_recovery is not None:
        STRICT_BULLY_ON_RECOVERY = bool(strict_bully_on_recovery)
    if process_ids is not None:
        PROCESS_IDS = list(process_ids)
    if seed is not None:
        RANDOM_SEED = int(seed)

    await main()

asyncio.run(start(
    crash=0.08,          
    recover=0.02,        
    heartbeat_interval=0.3,
    heartbeat_timeout=0.8,
    strict_bully_on_recovery=True
))