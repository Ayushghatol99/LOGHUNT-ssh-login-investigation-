import random
from datetime import datetime, timedelta

random.seed(1337)

HOST = "web-srv-01"
LINES = []

def add(ts, msg):
    LINES.append((ts, msg))

DAY = datetime(2026, 10, 12, 0, 0, 0)
def port():
    return random.randint(40000, 65000)

def failed(ts, user, ip):
    add(ts, f"Failed password for {user} from {ip} port {port()} ssh2")

def accepted(ts, user, ip):
    add(ts, f"Accepted password for {user} from {ip} port {port()} ssh2")

EMPLOYEES = {
    "asharma": "10.10.5.21",
    "mpatel":  "10.10.5.34",
    "rkhan":   "10.10.5.47",
    "tnguyen": "10.10.6.12",
    "lbrown":  "10.10.6.18",
    "dokafor": "10.10.7.9",
    "jsmith":  "10.10.5.60",
}

for user, ip in EMPLOYEES.items():
    for _ in range(random.randint(2, 4)):
        t = DAY + timedelta(hours=random.randint(8, 17),
                            minutes=random.randint(0, 59),
                            seconds=random.randint(0, 59))
        if random.random() < 0.25:
            failed(t - timedelta(seconds=random.randint(5, 20)), user, ip)
        accepted(t, user, ip)

print(len(LINES), "entries so far")

BF_IP = "198.51.100.23"
t = DAY + timedelta(hours=2, minutes=14, seconds=3)
for i in range(60):
    failed(t, "root", BF_IP)
    t += timedelta(seconds=random.randint(2, 5))

print(len(LINES), "entries now")

def failed_invalid(ts, user, ip):
    add(ts, f"Failed password for invalid user {user} from {ip} port {port()} ssh2")

SPRAY_IP = "203.0.113.45"
t = DAY + timedelta(hours=9, minutes=40, seconds=12)
for user in EMPLOYEES:
    failed(t, user, SPRAY_IP)
    t += timedelta(seconds=random.randint(25, 40))
for user in ["svc-backup", "hr-portal"]:
    failed_invalid(t, user, SPRAY_IP)
    t += timedelta(seconds=random.randint(25, 40))

print(len(LINES), "entries after spray")

print()

ATK_IP = "192.0.2.88"
t = DAY + timedelta(hours=14, minutes=3, seconds=41)
for i in range(38):
    failed(t, "jsmith", ATK_IP)
    t += timedelta(seconds=random.randint(3, 6))
t += timedelta(seconds=4)
accepted(t, "jsmith", ATK_IP)

add(t + timedelta(seconds=9),  "pam_unix(sshd:session): session opened for user jsmith by (uid=0)")
add(t + timedelta(seconds=52), "pam_unix(sudo:auth): authentication failure; logname=jsmith uid=1004 euid=0 tty=/dev/pts/0 ruser=jsmith rhost= user=jsmith")
add(t + timedelta(seconds=61), "sudo: jsmith : 3 incorrect password attempts ; TTY=pts/0 ; PWD=/home/jsmith ; USER=root ; COMMAND=/bin/bash")
add(t + timedelta(minutes=6),  "pam_unix(sshd:session): session closed for user jsmith")

print(len(LINES), "entries after incident")
LINES.sort(key=lambda x: x[0])

with open("logs/auth.log", "w") as f:
    for ts, msg in LINES:
        stamp = ts.strftime("%b %d %H:%M:%S")
        if msg.startswith("sudo:") or msg.startswith("pam_unix(sudo"):
            proc = "sudo"
        else:
            proc = "sshd"
        f.write(f"{stamp} {HOST} {proc}[{random.randint(10000, 39999)}]: {msg}\n")

print("wrote", len(LINES), "lines to logs/auth.log")
