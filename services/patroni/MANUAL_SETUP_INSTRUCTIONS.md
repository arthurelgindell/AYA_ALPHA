# Manual PostgreSQL Patroni HA Cluster Setup Instructions

## Prerequisites
All these commands require `sudo` privileges. Run them in order.

## Step 1: Install etcd LaunchDaemon on ALPHA

```bash
sudo cp /Users/arthurdell/AYA/services/patroni/com.aya.etcd.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.aya.etcd.plist
sudo chmod 644 /Library/LaunchDaemons/com.aya.etcd.plist
sudo launchctl load /Library/LaunchDaemons/com.aya.etcd.plist
```

Verify etcd is running:
```bash
etcdctl --endpoints=http://127.0.0.1:2379 endpoint health
```

## Step 2: Install etcd LaunchDaemon on BETA (via SSH)

```bash
ssh beta
sudo cp /Volumes/DATA/AYA/services/patroni/com.aya.etcd.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.aya.etcd.plist
sudo chmod 644 /Library/LaunchDaemons/com.aya.etcd.plist
sudo launchctl load /Library/LaunchDaemons/com.aya.etcd.plist
```

Verify BETA etcd:
```bash
etcdctl --endpoints=http://beta.tail5f2bae.ts.net:2379 endpoint health
```

## Step 3: Verify etcd Cluster Quorum

From ALPHA:
```bash
etcdctl --endpoints=http://alpha.tail5f2bae.ts.net:2379,http://beta.tail5f2bae.ts.net:2379 endpoint health
```

Expected output:
```
http://alpha.tail5f2bae.ts.net:2379 is healthy: successfully committed proposal: took = 2.123456ms
http://beta.tail5f2bae.ts.net:2379 is healthy: successfully committed proposal: took = 2.234567ms
```

## Step 4: Load Patroni LaunchDaemon on ALPHA

```bash
sudo launchctl load /Library/LaunchDaemons/com.aya.patroni-alpha.plist
```

Wait 10 seconds, then verify:
```bash
curl http://alpha.tail5f2bae.ts.net:8008/patroni
```

## Step 5: Setup Patroni on BETA

First, copy the LaunchDaemon to BETA:
```bash
scp /Users/arthurdell/AYA/services/patroni/com.aya.patroni-beta.plist beta:/tmp/
```

Then on BETA:
```bash
ssh beta
sudo cp /tmp/com.aya.patroni-beta.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.aya.patroni-beta.plist
sudo chmod 644 /Library/LaunchDaemons/com.aya.patroni-beta.plist

# Ensure patroni-beta.yml is in correct location
sudo mkdir -p /Volumes/DATA/AYA/services/patroni
sudo cp /Volumes/DATA/AYA/services/patroni/patroni-beta.yml /Volumes/DATA/AYA/services/patroni/

# Ensure log directory exists
sudo mkdir -p /Volumes/DATA/AYA/logs

# Load the service
sudo launchctl load /Library/LaunchDaemons/com.aya.patroni-beta.plist
```

Wait 10 seconds, then verify:
```bash
curl http://beta.tail5f2bae.ts.net:8008/patroni
```

## Step 6: Verify Cluster Status

From ALPHA:
```bash
export PATH="/Users/arthurdell/Library/Python/3.9/bin:$PATH"
patronictl -c /Users/arthurdell/AYA/services/patroni/patroni-alpha.yml list
```

Expected output should show:
```
+ Cluster: aya-postgres-cluster (7557815223099390891) ---------+----+-----------+
| Member | Host                    | Role    | State   | TL | Lag in MB |
+--------+-------------------------+---------+---------+----+-----------+
| alpha  | alpha.tail5f2bae.ts.net | Leader  | running |  2 |           |
| beta   | beta.tail5f2bae.ts.net | Replica | running |  2 |         0 |
+--------+-------------------------+---------+---------+----+-----------+
```

## Step 7: Verify Replication

```bash
PGPASSWORD='Power$$336633$$' psql -h alpha.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag -c "SELECT application_name, client_addr, state, sync_state, pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes FROM pg_stat_replication;"
```

Expected output:
```
 application_name |   client_addr   |  state   | sync_state | lag_bytes 
-----------------+-----------------+----------+------------+-----------
 beta            | 100.84.202.68   | streaming | sync       |         0
```

## Step 8: Test Connections

Test ALPHA (Primary - Read/Write):
```bash
PGPASSWORD='Power$$336633$$' psql -h alpha.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag -c "SELECT 'ALPHA OK' as status, COUNT(*) as chunks FROM chunks"
```

Test BETA (Standby - Read Only):
```bash
PGPASSWORD='Power$$336633$$' psql -h beta.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag -c "SELECT 'BETA OK' as status, COUNT(*) as chunks FROM chunks"
```

## Step 9: Verify Auto-Startup on Boot

Check that services are loaded:
```bash
sudo launchctl list | grep com.aya
```

You should see:
- `com.aya.etcd`
- `com.aya.patroni-alpha`

On BETA:
- `com.aya.etcd`
- `com.aya.patroni-beta`

## Troubleshooting

### etcd not starting
Check logs:
```bash
tail -50 /Users/arthurdell/Library/Logs/etcd.log
```

### Patroni not starting
Check logs:
```bash
tail -50 /Users/arthurdell/Library/Logs/patroni-alpha.log
```

### Replication not working
1. Verify network connectivity between ALPHA and BETA
2. Check that PostgreSQL on BETA is in recovery mode (standby)
3. Verify replicator user credentials

### Service won't load
```bash
# Unload first
sudo launchctl unload /Library/LaunchDaemons/com.aya.patroni-alpha.plist

# Fix permissions
sudo chown root:wheel /Library/LaunchDaemons/com.aya.patroni-alpha.plist
sudo chmod 644 /Library/LaunchDaemons/com.aya.patroni-alpha.plist

# Load again
sudo launchctl load /Library/LaunchDaemons/com.aya.patroni-alpha.plist
```

## Connection Strings for Applications

### Primary (Read/Write) - ALPHA
```
postgresql://postgres:Power$$336633$$@alpha.tail5f2bae.ts.net:5432/aya_rag
```

### Standby (Read Only) - BETA  
```
postgresql://postgres:Power$$336633$$@beta.tail5f2bae.ts.net:5432/aya_rag
```

**Note:** BETA accepts read queries only. Writes will fail with error about standby mode.

## Active-Active Configuration Notes

PostgreSQL with Patroni provides:
- ✅ **Active-Passive writes**: Only ALPHA accepts writes
- ✅ **Active-Active reads**: Both ALPHA and BETA accept reads
- ✅ **Automatic failover**: <30 seconds, BETA becomes primary
- ✅ **Zero data loss**: Synchronous replication (lag = 0)

This is equivalent to "active-active" from a resilience perspective.
