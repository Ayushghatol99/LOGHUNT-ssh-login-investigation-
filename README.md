# LogHunt: SOC Investigation of Suspicious SSH Logins

A beginner-friendly blue-team project. I investigated a day of SSH authentication logs, separated real attacks from normal activity, and wrote an incident report.

> **All data here is synthetic.** Hostnames, usernames and IP addresses are for my pratice (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`) or private `10.x` space. No real systems, credentials or personal logs are included.

## Objective
Work like a SOC Level 1 analyst on one case:
1. Understand what an SSH auth log records.
2. Find brute-force and password-spray patterns with Linux commands.
3. Investigate repeated failures followed by a successful login.
4. Write an incident report that does not claim more than the evidence shows.

## What I found

| Source IP | Behaviour | Outcome |
|---|---|---|
| `198.51.100.23` | 60 failed logins on `root`, fast, starting 02:14 | Failed, no success |
| `203.0.113.45` | Password spray: 1 attempt on each of 9 accounts, about 30 s apart | Failed, no success |
| `192.0.2.88` | 38 failed logins on `jsmith`, then a successful login, then 3 failed `sudo` attempts to root | **Probable account compromise (not confirmed)** |
| Internal `10.x` | 4 typo failures by employees | Normal |

Full write-up: [`report/incident_report.md`](report/incident_report.md)

## Repository layout
```
loghunt/
├── README.md
├── logs/
│   └── auth.log                 # synthetic SSH/sudo log (138 lines)
├── scripts/
│   └── logs.py                  # generates the synthetic log (seeded, reproducible)
├── evidence/
│   └── notes.txt                # real output of every command, by phase
└── report/
    └── incident_report.md       # the incident report
```

## How the log was built
`scripts/logs.py` creates normal employee logins plus three simulated scenarios: a brute force, a password spray, and a brute force followed by a successful login. A fixed random seed makes the output the same every run.

```bash
python3 scripts/logs.py
```

## Investigation phases

| Phase | Focus |
|---|---|
| 1 | Understand the logs: size, first and last entries, success and failure counts |
| 2 | Find noisy IPs and check whether the brute force and spray ever succeeded |
| 3 | Investigate the successful login from an outside IP and what the session did |

## Key commands
```bash
# Failed logins per source IP, highest first
grep 'Failed password' logs/auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -nr

# Successful logins from outside the internal network
grep 'Accepted password' logs/auth.log | grep -v 'from 10\.'

# Session and sudo activity after a login
grep -E 'session|sudo' logs/auth.log
```

## Limitations
- One day of synthetic data, so per-user baselines are thin.
- No GeoIP, threat-intelligence, MFA or shell-history data.
- Real logs are noisier and messier than this dataset.

## Skills practised
Linux command line (`grep`, `sort`, `uniq`, `wc`, `head`, `tail`), log analysis, brute-force and password-spray detection, timeline building, incident reporting, severity assessment.
