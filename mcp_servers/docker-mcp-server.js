#!/usr/bin/env node
/**
 * Docker MCP Server
 * Provides Docker container management capabilities via MCP protocol
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class DockerMCPServer {
  constructor() {
    this.tools = [
      {
        name: 'docker_list_containers',
        description: 'List all Docker containers (running and stopped)',
        inputSchema: {
          type: 'object',
          properties: {
            all: {
              type: 'boolean',
              description: 'Show all containers (default shows just running)',
              default: true
            }
          }
        }
      },
      {
        name: 'docker_exec',
        description: 'Execute a command inside a running container',
        inputSchema: {
          type: 'object',
          properties: {
            container: {
              type: 'string',
              description: 'Container name or ID'
            },
            command: {
              type: 'string',
              description: 'Command to execute'
            }
          },
          required: ['container', 'command']
        }
      },
      {
        name: 'docker_logs',
        description: 'Get logs from a container',
        inputSchema: {
          type: 'object',
          properties: {
            container: {
              type: 'string',
              description: 'Container name or ID'
            },
            tail: {
              type: 'number',
              description: 'Number of lines to show from the end',
              default: 100
            }
          },
          required: ['container']
        }
      },
      {
        name: 'docker_inspect',
        description: 'Get detailed information about a container',
        inputSchema: {
          type: 'object',
          properties: {
            container: {
              type: 'string',
              description: 'Container name or ID'
            }
          },
          required: ['container']
        }
      },
      {
        name: 'docker_stats',
        description: 'Get resource usage statistics for containers',
        inputSchema: {
          type: 'object',
          properties: {
            container: {
              type: 'string',
              description: 'Container name or ID (omit for all)'
            }
          }
        }
      }
    ];
  }

  async listContainers(all = true) {
    try {
      const flag = all ? '-a' : '';
      const { stdout } = await execAsync(`docker ps ${flag} --format '{{json .}}'`);
      const containers = stdout.trim().split('\n')
        .filter(line => line)
        .map(line => JSON.parse(line));
      return { success: true, containers };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async execCommand(container, command) {
    try {
      const { stdout, stderr } = await execAsync(`docker exec ${container} ${command}`);
      return { success: true, stdout, stderr };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getLogs(container, tail = 100) {
    try {
      const { stdout } = await execAsync(`docker logs --tail ${tail} ${container}`);
      return { success: true, logs: stdout };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async inspectContainer(container) {
    try {
      const { stdout } = await execAsync(`docker inspect ${container}`);
      const info = JSON.parse(stdout)[0];
      return { success: true, info };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getStats(container = '') {
    try {
      const { stdout } = await execAsync(`docker stats --no-stream ${container} --format '{{json .}}'`);
      const stats = stdout.trim().split('\n')
        .filter(line => line)
        .map(line => JSON.parse(line));
      return { success: true, stats };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async handleToolCall(name, args) {
    switch (name) {
      case 'docker_list_containers':
        return await this.listContainers(args.all);
      case 'docker_exec':
        return await this.execCommand(args.container, args.command);
      case 'docker_logs':
        return await this.getLogs(args.container, args.tail);
      case 'docker_inspect':
        return await this.inspectContainer(args.container);
      case 'docker_stats':
        return await this.getStats(args.container);
      default:
        return { success: false, error: `Unknown tool: ${name}` };
    }
  }

  async run() {
    // MCP stdio-based server with proper protocol implementation
    process.stdin.setEncoding('utf8');
    
    let buffer = '';
    process.stdin.on('data', async (chunk) => {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;
        
        try {
          const request = JSON.parse(line);
          let response;

          if (request.method === 'initialize') {
            response = {
              jsonrpc: '2.0',
              id: request.id,
              result: {
                protocolVersion: '2024-11-05',
                capabilities: { tools: {} },
                serverInfo: {
                  name: 'docker-mcp-server',
                  version: '1.0.0'
                }
              }
            };
          } else if (request.method === 'notifications/initialized') {
            // No response needed for notifications
            continue;
          } else if (request.method === 'tools/list') {
            response = {
              jsonrpc: '2.0',
              id: request.id,
              result: { tools: this.tools }
            };
          } else if (request.method === 'tools/call') {
            const result = await this.handleToolCall(
              request.params.name,
              request.params.arguments || {}
            );
            response = {
              jsonrpc: '2.0',
              id: request.id,
              result: { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] }
            };
          } else {
            response = {
              jsonrpc: '2.0',
              id: request.id,
              error: { code: -32601, message: 'Method not found' }
            };
          }

          if (response) {
            process.stdout.write(JSON.stringify(response) + '\n');
          }
        } catch (error) {
          const errorResponse = {
            jsonrpc: '2.0',
            id: null,
            error: { code: -32700, message: 'Parse error', data: error.message }
          };
          process.stdout.write(JSON.stringify(errorResponse) + '\n');
        }
      }
    });

    process.stdin.on('end', () => {
      process.exit(0);
    });
  }
}

// Run the server if executed directly
if (require.main === module) {
  const server = new DockerMCPServer();
  server.run().catch(error => {
    console.error('Server error:', error);
    process.exit(1);
  });
}

module.exports = DockerMCPServer;

