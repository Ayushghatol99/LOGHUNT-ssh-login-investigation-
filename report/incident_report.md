# Incident Report: Suspected Account Compromise via SSH Brute Force

> **Synthetic data.** All hosts, users and IP addresses are only for the pratice.

| Field | Detail |
|---|---|
| Host | web-srv-01 |
| Date of events | 12 Oct 2026 |
| Data source | `logs/auth.log` (138 lines) |
| Account involved | `jsmith` |
| Suspicious source IP | `192.0.2.88` |

## 1. Summary

On 12 Oct 2026, the IP 192.0.2.88 made 38 failed SSH logins against the account jsmith in about 3 minutes, then logged in successfully at 14:06:27. The session then tried to gain root access with sudo (`/bin/bash`), which failed 3 times. The account is probably compromised because an outside IP guessed the password after 38 automated attempts, and jsmith normally logs in from 10.10.5.60. Recommended action: disable the account, reset the password, block the IP and confirm with jsmith.

## 2. Timeline

| Time | Event | Source |
|---|---|---|
| 10:27:22 | jsmith logs in normally | 10.10.5.60 (internal) |
| 13:52:05 | jsmith logs in normally | 10.10.5.60 (internal) |
| 14:03:41 | First failed login for jsmith | 192.0.2.88 (external) |
| 14:03:41 to 14:06:17 | 38 failed logins, one every 3 to 6 seconds | 192.0.2.88 |
| **14:06:27** | **Successful login for jsmith** | **192.0.2.88** |
| 14:06:36 | Session opened | jsmith |
| 14:07:19 | sudo authentication failure | jsmith |
| 14:07:28 | sudo: 3 incorrect password attempts, command `/bin/bash` as root | jsmith |
| 14:12:27 | Session closed | jsmith |

## 3. Evidence

All output is saved in `evidence/notes.txt` (Phases 1 to 3).

**Failed logins per source IP**

```bash
grep 'Failed password' logs/auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -nr
```

| Count | Source IP | Pattern |
|---|---|---|
| 60 | `198.51.100.23` | Brute force on `root`, starting 02:14:03. No successful login. |
| 38 | `192.0.2.88` | Brute force on `jsmith`, then a successful login. |
| 9 | `203.0.113.45` | Password spray: one attempt on each of 9 accounts, about 30 seconds apart (09:40 to 09:44). No successful login. |
| 2, 1, 1 | `10.10.x.x` | Internal typos by employees. Normal. |

**Successful logins from outside the company network**

```bash
grep 'Accepted password' logs/auth.log | grep -v 'from 10\.'
```

Only one line: `jsmith` from `192.0.2.88` at 14:06:27. All 22 other successful logins came from internal `10.x` addresses.

**jsmith's normal logins**

```bash
grep 'Accepted password for jsmith' logs/auth.log
```

Two logins from `10.10.5.60` (10:27:22 and 13:52:05), then the one from `192.0.2.88` (14:06:27).

**Activity after the login**

```bash
grep -E 'session|sudo' logs/auth.log
```

Session opened 14:06:36, sudo failures at 14:07:19 and 14:07:28 (`COMMAND=/bin/bash`, `USER=root`), session closed 14:12:27.

## 4. Assessment

### Evidence supporting compromise
1. **Brute-force pattern.** 38 failed logins on `jsmith` in under 3 minutes, one every 3 to 6 seconds, then a successful login 10 seconds after the last failure (14:06:17 to 14:06:27).
2. **Unusual source.** `192.0.2.88` is the only outside IP among the 23 successful logins. jsmith's other logins (10:27 and 13:52) came from `10.10.5.60`.
3. **Root escalation attempt.** About a minute after logging in, `sudo /bin/bash` as root failed 3 times (14:07:19 to 14:07:28).

### Other explanations considered
- **jsmith working remotely and forgetting the password.** Unlikely: the attempts were machine-paced, and jsmith had logged in normally from the office 14 minutes earlier (13:52:05).
- **Authorised security testing.** Cannot be ruled out from the log alone. Check with the security team.

### What the logs show, and what they don't
- **Shown:** an outside IP logged in as `jsmith` after 38 failures and tried to reach root.
- **Not shown:** what happened during the roughly 5 minutes after the sudo failures, whether root access was gained any other way, and who was behind `192.0.2.88`.

### Conclusion
**Probable compromise of `jsmith`: high confidence, not confirmed.**

## 5. Severity

**High.**

- A successful login by what looks like an unauthorised outside party.
- The session attempted to escalate to root.
- The password was guessed within a few minutes, so other accounts may be weak too.
- **Mitigating factors:** the root attempt failed, and the session lasted only about 6 minutes (14:06:36 to 14:12:27).

This would rise to **Critical** if follow-up shows root access, persistence or movement to other systems.

## 6. Recommended actions

**Immediate (containment)**
1. Disable the `jsmith` account and end any active sessions.
2. Contact jsmith by phone or in person, not through the possibly compromised account, then reset the password.
3. Block `192.0.2.88`, `198.51.100.23` and `203.0.113.45` at the firewall.

**Short term (investigation)**
4. Ask jsmith whether they logged in from outside the office at 14:06.
5. Review shell history, new accounts, scheduled jobs and recently changed files on `web-srv-01` for 14:06 to 14:13.
6. Check whether any approved security testing was scheduled for that time.

**Long term (hardening)**
7. Turn off SSH password login and use keys, or require MFA.
8. Add rate limiting such as `fail2ban` to stop bursts of failed logins.

