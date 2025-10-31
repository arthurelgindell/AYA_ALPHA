#!/bin/bash
# Monitor Intelligence Scout Crawl Progress

QUEUE_ID=${1:-1}

echo "=== Intelligence Scout Crawl Monitor ==="
echo "Queue ID: $QUEUE_ID"
echo ""

while true; do
    STATUS=$(PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -t -c "SELECT status FROM intelligence_scout_queue WHERE id = $QUEUE_ID" | tr -d ' ')
    PAGES=$(PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -t -c "SELECT pages_crawled FROM intelligence_scout_queue WHERE id = $QUEUE_ID" | tr -d ' ')
    
    echo -ne "\rStatus: $STATUS | Pages Crawled: $PAGES"
    
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
        echo ""
        echo ""
        echo "=== Final Status ==="
        PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT * FROM intelligence_scout_queue WHERE id = $QUEUE_ID;"
        break
    fi
    
    sleep 10
done

