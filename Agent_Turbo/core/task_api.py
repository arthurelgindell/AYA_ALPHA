#!/usr/bin/env python3
"""
Task API - HTTP Interface for Task Management
FastAPI server for creating and monitoring parallel agent tasks

Prime Directives Compliance:
- Directive #1: FUNCTIONAL REALITY - Real database operations
- Directive #2: DATABASE FIRST - PostgreSQL is source of truth
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import sys
import os
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from postgres_connector import PostgreSQLConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent Turbo Task API",
    description="Parallel agent execution task management",
    version="1.0.0"
)

# Database connector (initialized on startup)
db: Optional[PostgreSQLConnector] = None


class TaskCreate(BaseModel):
    """Task creation request"""
    task_type: str = Field(..., description="Type of task")
    description: str = Field(..., description="Task description/prompt")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")
    timeout_seconds: int = Field(default=300, ge=10, le=3600, description="Timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=5, description="Maximum retry attempts")


class TaskResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: str
    task_type: str
    description: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_worker_id: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None


class DashboardResponse(BaseModel):
    """System dashboard metrics"""
    queued: int
    running: int
    completed_last_hour: int
    failed_last_hour: int
    total_completed: int
    avg_execution_time_sec: Optional[float] = None


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    global db
    db = PostgreSQLConnector()
    logger.info("Task API started - Database connected")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    if db:
        db.close()
    logger.info("Task API shutdown")


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate):
    """
    Create a new task for parallel execution.
    
    The task will be queued and picked up by available workers.
    """
    try:
        task_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO agent_tasks (
                task_id,
                task_type,
                task_description,
                task_priority,
                status,
                timeout_seconds,
                max_retries,
                retry_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING task_id, task_type, task_description, task_priority, 
                      created_at, status
        """
        
        result = db.execute_query(
            query,
            (task_id, task.task_type, task.description, task.priority,
             'pending', task.timeout_seconds, task.max_retries, 0),
            fetch=True
        )
        
        if result:
            task_data = result[0]
            logger.info(f"Task created: {task_id} - {task.description[:50]}...")
            
            return TaskResponse(
                task_id=task_data['task_id'],
                status=task_data['status'],
                task_type=task_data['task_type'],
                description=task_data['task_description'],
                priority=task_data['task_priority'],
                created_at=task_data['created_at']
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create task")
    
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Get task status and details.
    """
    try:
        query = """
            SELECT 
                task_id,
                task_type,
                task_description,
                task_priority,
                status,
                created_at,
                started_at,
                completed_at,
                assigned_worker_id,
                error_message,
                output_data
            FROM agent_tasks
            WHERE task_id = %s
        """
        
        result = db.execute_query(query, (task_id,), fetch=True)
        
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = result[0]
        
        # Extract execution time from output_data if available
        exec_time_ms = None
        if task_data['output_data'] and 'execution_time_ms' in task_data['output_data']:
            exec_time_ms = task_data['output_data']['execution_time_ms']
        
        return TaskResponse(
            task_id=task_data['task_id'],
            status=task_data['status'],
            task_type=task_data['task_type'],
            description=task_data['task_description'],
            priority=task_data['task_priority'],
            created_at=task_data['created_at'],
            started_at=task_data['started_at'],
            completed_at=task_data['completed_at'],
            assigned_worker_id=task_data['assigned_worker_id'],
            error_message=task_data['error_message'],
            execution_time_ms=exec_time_ms
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 20
):
    """
    List recent tasks, optionally filtered by status.
    """
    try:
        if status:
            query = """
                SELECT 
                    task_id, task_type, task_description, task_priority,
                    status, created_at, started_at, completed_at,
                    assigned_worker_id, error_message, output_data
                FROM agent_tasks
                WHERE status = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            result = db.execute_query(query, (status, limit), fetch=True)
        else:
            query = """
                SELECT 
                    task_id, task_type, task_description, task_priority,
                    status, created_at, started_at, completed_at,
                    assigned_worker_id, error_message, output_data
                FROM agent_tasks
                ORDER BY created_at DESC
                LIMIT %s
            """
            result = db.execute_query(query, (limit,), fetch=True)
        
        tasks = []
        for task_data in result:
            exec_time_ms = None
            if task_data['output_data'] and 'execution_time_ms' in task_data['output_data']:
                exec_time_ms = task_data['output_data']['execution_time_ms']
            
            tasks.append(TaskResponse(
                task_id=task_data['task_id'],
                status=task_data['status'],
                task_type=task_data['task_type'],
                description=task_data['task_description'],
                priority=task_data['task_priority'],
                created_at=task_data['created_at'],
                started_at=task_data['started_at'],
                completed_at=task_data['completed_at'],
                assigned_worker_id=task_data['assigned_worker_id'],
                error_message=task_data['error_message'],
                execution_time_ms=exec_time_ms
            ))
        
        return tasks
    
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """
    Get system dashboard with key metrics.
    """
    try:
        query = """
            SELECT 
                COUNT(*) FILTER (WHERE status = 'pending') as queued,
                COUNT(*) FILTER (WHERE status = 'running') as running,
                COUNT(*) FILTER (WHERE status = 'completed' AND completed_at > NOW() - INTERVAL '1 hour') as completed_last_hour,
                COUNT(*) FILTER (WHERE status = 'failed' AND completed_at > NOW() - INTERVAL '1 hour') as failed_last_hour,
                COUNT(*) FILTER (WHERE status = 'completed') as total_completed,
                AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) FILTER (WHERE status = 'completed' AND completed_at > NOW() - INTERVAL '1 hour') as avg_exec_time
            FROM agent_tasks
        """
        
        result = db.execute_query(query, fetch=True)
        
        if result:
            data = result[0]
            return DashboardResponse(
                queued=data['queued'] or 0,
                running=data['running'] or 0,
                completed_last_hour=data['completed_last_hour'] or 0,
                failed_last_hour=data['failed_last_hour'] or 0,
                total_completed=data['total_completed'] or 0,
                avg_execution_time_sec=float(data['avg_exec_time']) if data['avg_exec_time'] else None
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")
    
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a pending task.
    """
    try:
        query = """
            UPDATE agent_tasks
            SET status = 'cancelled'
            WHERE task_id = %s AND status = 'pending'
        """
        
        db.execute_query(query, (task_id,), fetch=False)
        
        return {"status": "cancelled", "task_id": task_id}
    
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Simple database connectivity check
        result = db.execute_query("SELECT 1", fetch=True)
        if result:
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "database": "error"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/")
async def root():
    """API root - documentation redirect"""
    return {
        "message": "Agent Turbo Task API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', '8765'))
    
    print("=" * 60)
    print("  Agent Turbo Task API")
    print("=" * 60)
    print(f"  Port: {port}")
    print(f"  Docs: http://localhost:{port}/docs")
    print(f"  Health: http://localhost:{port}/health")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

