#!/usr/bin/env python3
"""
LM Studio Client for AGENT_TURBO Integration
GAMMA Project - Prime Directives Compliance
"""
import requests
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

class LMStudioClient:
    """Client for LM Studio API integration with AGENT_TURBO"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.model_id = "qwen/qwen3-next-80b"
        self.cache = {}
        self.stats = {
            'requests_made': 0,
            'requests_cached': 0,
            'total_tokens': 0,
            'total_response_time': 0.0,
            'errors': 0
        }
        
        # Test connectivity
        self._test_connectivity()
    
    def _test_connectivity(self):
        """Test connectivity to LM Studio server"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                if 'data' in models and len(models['data']) > 0:
                    self.model_id = models['data'][0]['id']
                    print(f"✅ LM Studio connected: {self.model_id}")
                else:
                    print("⚠️  LM Studio connected but no models available")
            else:
                print(f"❌ LM Studio connection failed: {response.status_code}")
        except Exception as e:
            print(f"❌ LM Studio connection error: {e}")
    
    def _generate_cache_key(self, prompt: str, max_tokens: int = 100, temperature: float = 0.3) -> str:
        """Generate cache key for request"""
        cache_data = f"{prompt}:{max_tokens}:{temperature}"
        return hashlib.sha256(cache_data.encode()).hexdigest()[:16]
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache"""
        if cache_key in self.cache:
            self.stats['requests_cached'] += 1
            return self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, response_data: Dict[str, Any]):
        """Save response to cache"""
        self.cache[cache_key] = response_data
    
    def generate_text(self, prompt: str, max_tokens: int = 100, temperature: float = 0.3, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate text using LM Studio
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            use_cache: Whether to use caching
            
        Returns:
            Dictionary with response data and metadata
        """
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(prompt, max_tokens, temperature)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={'Content-Type': 'application/json'},
                json={
                    'model': self.model_id,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': max_tokens,
                    'temperature': temperature
                },
                timeout=self.timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response content
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    usage = data.get('usage', {})
                    
                    result = {
                        'success': True,
                        'content': content,
                        'response_time': response_time,
                        'tokens': usage.get('total_tokens', 0),
                        'prompt_tokens': usage.get('prompt_tokens', 0),
                        'completion_tokens': usage.get('completion_tokens', 0),
                        'tokens_per_second': usage.get('completion_tokens', 0) / response_time if response_time > 0 else 0,
                        'model': data.get('model', self.model_id),
                        'cached': False
                    }
                    
                    # Update stats
                    self.stats['requests_made'] += 1
                    self.stats['total_tokens'] += result['tokens']
                    self.stats['total_response_time'] += response_time
                    
                    # Save to cache
                    if use_cache:
                        self._save_to_cache(cache_key, result)
                        result['cached'] = False  # This response wasn't cached, but future ones will be
                    
                    return result
                else:
                    return {
                        'success': False,
                        'error': 'No response content',
                        'response_time': response_time,
                        'cached': False
                    }
            else:
                self.stats['errors'] += 1
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'response_time': response_time,
                    'cached': False
                }
                
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'success': False,
                'error': str(e),
                'response_time': 0,
                'cached': False
            }
    
    def enhance_knowledge(self, knowledge_text: str, enhancement_type: str = "explanation") -> Dict[str, Any]:
        """
        Enhance knowledge using LM Studio
        
        Args:
            knowledge_text: Original knowledge text
            enhancement_type: Type of enhancement (explanation, summary, expansion)
            
        Returns:
            Enhanced knowledge with metadata
        """
        prompts = {
            'explanation': f"Provide a detailed explanation of this knowledge: {knowledge_text}",
            'summary': f"Create a concise summary of this knowledge: {knowledge_text}",
            'expansion': f"Expand and elaborate on this knowledge with additional context: {knowledge_text}",
            'context': f"Provide relevant context and background for this knowledge: {knowledge_text}"
        }
        
        prompt = prompts.get(enhancement_type, prompts['explanation'])
        
        return self.generate_text(prompt, max_tokens=200, temperature=0.3)
    
    def generate_response(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """
        Generate intelligent response using LM Studio
        
        Args:
            query: User query
            context: List of relevant context strings
            
        Returns:
            Generated response with metadata
        """
        if context:
            context_text = "\n".join([f"- {ctx}" for ctx in context])
            prompt = f"Based on the following context:\n{context_text}\n\nAnswer this question: {query}"
        else:
            prompt = f"Answer this question: {query}"
        
        return self.generate_text(prompt, max_tokens=300, temperature=0.2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        avg_response_time = (self.stats['total_response_time'] / self.stats['requests_made'] 
                           if self.stats['requests_made'] > 0 else 0)
        
        return {
            'requests_made': self.stats['requests_made'],
            'requests_cached': self.stats['requests_cached'],
            'total_tokens': self.stats['total_tokens'],
            'average_response_time': avg_response_time,
            'errors': self.stats['errors'],
            'cache_size': len(self.cache),
            'model_id': self.model_id,
            'base_url': self.base_url
        }
    
    def clear_cache(self):
        """Clear response cache"""
        self.cache.clear()
        print("✅ LM Studio cache cleared")
    
    def test_performance(self) -> Dict[str, Any]:
        """Test LM Studio performance"""
        test_prompts = [
            "Explain the benefits of GPU acceleration for AI workloads.",
            "What are the key components of a knowledge management system?",
            "Describe the advantages of using MLX for Apple Silicon."
        ]
        
        results = []
        for prompt in test_prompts:
            result = self.generate_text(prompt, max_tokens=100, temperature=0.3, use_cache=False)
            if result['success']:
                results.append(result)
        
        if results:
            avg_response_time = sum(r['response_time'] for r in results) / len(results)
            avg_tokens_per_second = sum(r['tokens_per_second'] for r in results) / len(results)
            total_tokens = sum(r['tokens'] for r in results)
            
            return {
                'success': True,
                'test_count': len(results),
                'average_response_time': avg_response_time,
                'average_tokens_per_second': avg_tokens_per_second,
                'total_tokens': total_tokens,
                'results': results
            }
        else:
            return {
                'success': False,
                'error': 'No successful test results'
            }

