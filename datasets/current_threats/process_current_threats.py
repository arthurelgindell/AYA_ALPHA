import json

# Process CISA KEV
with open('cisa_kev_oct2025.json') as f:
    cisa = json.load(f)

vulns = cisa.get('vulnerabilities', [])
print(f"CISA KEV: {len(vulns)} actively exploited vulnerabilities")

# Sample first few
for i, vuln in enumerate(vulns[:5]):
    cve = vuln.get('cveID', 'unknown')
    name = vuln.get('vulnerabilityName', 'unknown')
    print(f"  {i+1}. {cve}: {name[:60]}...")

# Process NVD CVEs
with open('nvd_recent.json') as f:
    nvd = json.load(f)

cves = nvd.get('vulnerabilities', [])
print(f"\nNVD Recent: {len(cves)} CVEs from Sept-Oct 2025")

# Sample
for i, item in enumerate(cves[:3]):
    cve_data = item.get('cve', {})
    cve_id = cve_data.get('id', 'unknown')
    desc = cve_data.get('descriptions', [{}])[0].get('value', 'No description')
    print(f"  {i+1}. {cve_id}: {desc[:80]}...")

print(f"\n✅ Total CURRENT threat intelligence: {len(vulns) + len(cves)} items")
print("✅ Ready to convert to training format")
