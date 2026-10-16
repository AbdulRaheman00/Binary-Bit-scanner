# MCP Server Scan Report

- **Target:** `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py`
- **Generated:** 2026-10-16 11:01 UTC
- **Modules:** static
- **Result:** PASS (fail-on: never)

## Summary

| Severity | Count |
| --- | ---: |
| HIGH | 3 |
| MEDIUM | 1 |
| LOW | 1 |
| INFO | 0 |

## Findings

| ID | Severity | Location | Title |
| --- | --- | --- | --- |
| CMD-002 | HIGH | `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:16` | os.system / os.popen call |
| DES-001 | HIGH | `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:20` | Unsafe deserialization (pickle) |
| SEC-004 | HIGH | `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:7` | API key (sk-...) |
| SEC-005 | MEDIUM | `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:7` | Hardcoded secret-looking value |
| NET-001 | LOW | `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:24` | Outbound network access |

## Details

### CMD-002: os.system / os.popen call

- **ID:** CMD-002
- **Severity:** HIGH
- **Category:** static
- **Location:** `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:16`
- **Evidence:** `return os.popen("echo " + cmd).read()`
- **Fix:** Use subprocess.run([...]) with an argument list.

### DES-001: Unsafe deserialization (pickle)

- **ID:** DES-001
- **Severity:** HIGH
- **Category:** static
- **Location:** `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:20`
- **Evidence:** `return pickle.loads(blob)`
- **Fix:** Use JSON or another data-only format.

### SEC-004: API key (sk-...)

- **ID:** SEC-004
- **Severity:** HIGH
- **Category:** static
- **Location:** `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:7`
- **Evidence:** `API_KEY = "sk-live-9f8e7d6c5b4a39281706f5e4d3c2b1a0"`
- **Fix:** Move it to an env var and rotate the key.

### SEC-005: Hardcoded secret-looking value

- **ID:** SEC-005
- **Severity:** MEDIUM
- **Category:** static
- **Location:** `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:7`
- **Evidence:** `API_KEY = "sk-live-9f8e7d6c5b4a39281706f5e4d3c2b1a0"`
- **Fix:** Load it from the environment at runtime.

### NET-001: Outbound network access

- **ID:** NET-001
- **Severity:** LOW
- **Category:** static
- **Location:** `C:\Users\temp6\Desktop\mcp-security-auditor\demo\vuln_server.py:24`
- **Evidence:** `return urllib.request.urlopen(url).read().decode()`
- **Fix:** Restrict to an allowlist of hosts and document it.
