#!/bin/bash
# Update PostgreSQL 18 with Jumbo Frames MTU configuration

echo "Updating PostgreSQL 18 with Jumbo Frames configuration..."

ssh beta.local "PGPASSWORD='Power\$\$336633\$\$' psql -h localhost -p 5432 -U postgres -d aya_rag -c \"
UPDATE network_interfaces
SET metadata = jsonb_set(
    COALESCE(metadata, '{}'::jsonb),
    '{mtu}',
    '9000'::jsonb
),
updated_at = NOW()
WHERE interface_name = 'en0'
AND node_id IN (SELECT id FROM system_nodes WHERE node_name IN ('ALPHA', 'BETA'));
\""

echo ""
echo "Verifying database update..."

ssh beta.local "PGPASSWORD='Power\$\$336633\$\$' psql -h localhost -p 5432 -U postgres -d aya_rag -c \"
SELECT
    sn.node_name,
    ni.connection_type,
    ni.metadata->>'mtu' as mtu,
    ni.updated_at
FROM network_interfaces ni
JOIN system_nodes sn ON ni.node_id = sn.id
WHERE ni.interface_name = 'en0'
ORDER BY sn.node_name;
\""

echo ""
echo "✓ Database updated with Jumbo Frames configuration"
