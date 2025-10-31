# PostgreSQL 18 Database Highlights
**Database**: `aya_rag`  
**Date**: October 29, 2025

---

## 📊 Database Overview

- **Total Tables**: 139
- **Extensions Installed**:
  - `plpgsql` (1.0) - Procedural language
  - `uuid-ossp` (1.1) - UUID generation
  - `vector` (0.8.1) - Vector similarity search (pgvector)

---

## 🔑 Key Data Components

### 1. **RAG (Retrieval-Augmented Generation) System**
- **`chunks`** table: 27,924 records
  - Primary vector embeddings storage
  - Used for semantic search and AI context retrieval
  - Largest data component

### 2. **Agent Turbo System**
- **`agent_sessions`**: Active agent session management
- **`agent_knowledge`**: Knowledge base for agents
- **`agent_tasks`**: Task tracking and execution
- **`agent_actions`**: Action history and logging
- **`agent_performance_metrics`**: Performance monitoring
- **`agent_context_cache`**: Context caching for efficiency

### 3. **Code Audit System**
- **`code_audit_findings`**: Security/vulnerability findings
- **`code_audit_health`**: System health records
- **`code_audit_metrics`**: Performance metrics
- **`code_audit_config`**: Audit configuration
- **`code_audit_job_queue`**: Background job processing
- **`code_audit_remediations`**: Remediation tracking
- **`code_audit_runs`**: Audit execution history

### 4. **GLADIATOR Project**
Multiple tables prefixed with `gladiator_*`:
- `gladiator_agent_coordination`
- `gladiator_attack_generation_stats`
- `gladiator_attack_patterns`
- `gladiator_blue_to_red_intelligence`
- `gladiator_change_log`
- `gladiator_clean_state_validations`
- `gladiator_documentation`
- `gladiator_endpoint_quarantine`
- `gladiator_execution_plan`
- And more...

### 5. **Document Management**
- **`documents`**: Document metadata
- **`folder`**: File system structure
- **`folder_tag`**: Folder categorization
- **`documentation_files`**: Documentation tracking
- **`firecrawl_docs`**: Web scraping documentation
- **`crush_documentation`**: CRUSH docs
- **`docker_documentation`**: Docker docs

### 6. **Execution & Workflow**
- **`execution_entity`**: Execution records
- **`execution_data`**: Execution data storage
- **`execution_metadata`**: Metadata tracking
- **`execution_annotations`**: Execution annotations
- **`execution_annotation_tags`**: Tag management

### 7. **Authentication & Authorization**
- **`auth_identity`**: User identities
- **`auth_provider_sync_history`**: OAuth sync history
- **`credentials_entity`**: Credential management

### 8. **Data & Schema Management**
- **`data_table`**: Table definitions
- **`data_table_column`**: Column definitions
- **`database_schemas`**: Schema metadata

### 9. **System Tables**
- **`change_log`**: System-wide change tracking
- **`system_prompts`**: AI system prompts
- **`event_destinations`**: Event routing

---

## 📈 Data Distribution

**Top Data-Intensive Tables:**
1. **chunks**: 27,924 rows, 277 MB (RAG vector embeddings - largest table)
2. **Documentation tables**: 132 MB total
   - `zapier_documentation`: 51 MB
   - `docker_documentation`: 38 MB
   - `crush_documentation`: 24 MB
   - `postgresql_documentation`: 33 MB
   - `firecrawl_docs`: 18 MB
   - `lmstudio_documentation`: 1584 KB
3. **agent_* tables**: 
   - Agent Sessions: 191
   - Agent Tasks: 573
   - Agent Knowledge: 121
4. **code_audit_findings**: 83 records
5. **gladiator_* tables**: 25 tables (currently empty, ready for data)

---

## 🔧 Technical Features

### Vector Search (pgvector)
- **Extension**: `vector` v0.8.1
- Enables semantic similarity search on embeddings
- Critical for RAG system functionality

### UUID Generation
- **Extension**: `uuid-ossp` v1.1
- Used for distributed ID generation across services

---

## 🎯 Use Cases

1. **AI Agent System**: Full agent session, task, and knowledge management
2. **RAG System**: 27K+ vector embeddings for semantic search
3. **Code Security**: Comprehensive audit and vulnerability tracking
4. **Project Management**: GLADIATOR project coordination
5. **Documentation**: Multi-source documentation management
6. **Workflow Execution**: Execution tracking and annotation

---

## 💾 Database Characteristics

- **Total Size**: 586 MB (current database size)
- **Vector Data**: Significant portion (27K+ embeddings)
- **High Concurrency**: Optimized for 300 connections
- **Production Ready**: Synchronous replication configured

---

This database is the core of your AYA system, supporting AI agents, RAG functionality, code auditing, and project management workflows.
