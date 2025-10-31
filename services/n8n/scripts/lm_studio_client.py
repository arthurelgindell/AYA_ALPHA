#!/usr/bin/env python3
"""
LM Studio client for n8n workflows
Provides simple interface to query local LLMs via LM Studio API
"""

import requests
import json
from typing import Dict, Optional, List


class LMStudioClient:
    """Client for LM Studio API on ALPHA"""
    
    def __init__(self, base_url='http://localhost:1234/v1'):
        """
        Initialize LM Studio client
        
        Args:
            base_url: LM Studio API base URL
        """
        self.base_url = base_url
        self.timeout = 60
    
    def list_models(self) -> List[Dict]:
        """
        List available models
        
        Returns:
            list: Available models
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            return []
    
    def completion(self, 
                  prompt: str, 
                  model: str = 'foundation-sec-8b-instruct-int8',
                  max_tokens: int = 500,
                  temperature: float = 0.7,
                  stop: Optional[List[str]] = None) -> Dict:
        """
        Generate completion
        
        Args:
            prompt: Input prompt
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            stop: Stop sequences
            
        Returns:
            dict: Completion response
        """
        payload = {
            'model': model,
            'prompt': prompt,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': False
        }
        
        if stop:
            payload['stop'] = stop
        
        try:
            response = requests.post(
                f"{self.base_url}/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def chat_completion(self,
                       messages: List[Dict],
                       model: str = 'qwen3-next-80b-a3b-instruct-mlx',
                       max_tokens: int = 500,
                       temperature: float = 0.7) -> Dict:
        """
        Generate chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            dict: Chat completion response
        """
        payload = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def embedding(self, 
                 text: str,
                 model: str = 'text-embedding-nomic-embed-text-v1.5') -> Dict:
        """
        Generate embedding
        
        Args:
            text: Input text
            model: Embedding model
            
        Returns:
            dict: Embedding response
        """
        payload = {
            'model': model,
            'input': text
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def health_check(self) -> bool:
        """
        Check if LM Studio is responding
        
        Returns:
            bool: True if healthy
        """
        try:
            models = self.list_models()
            return len(models) > 0
        except:
            return False


def test_client():
    """Test the LM Studio client"""
    print("="*60)
    print("LM STUDIO CLIENT TEST")
    print("="*60)
    
    client = LMStudioClient()
    
    # Test 1: Health check
    print("\n1. Testing LM Studio connection...")
    if client.health_check():
        print("   ✅ LM Studio is responding")
    else:
        print("   ❌ LM Studio not available")
        return
    
    # Test 2: List models
    print("\n2. Listing available models...")
    models = client.list_models()
    if models:
        print(f"   ✅ Found {len(models)} models:")
        for model in models[:3]:
            print(f"      - {model.get('id', 'unknown')}")
    else:
        print("   ⚠️  No models found")
    
    # Test 3: Simple completion
    print("\n3. Testing completion...")
    result = client.completion(
        prompt="What is cybersecurity?",
        max_tokens=50
    )
    if 'error' not in result:
        text = result.get('choices', [{}])[0].get('text', '')
        print(f"   ✅ Completion generated: {len(text)} chars")
        print(f"      Preview: {text[:100]}...")
    else:
        print(f"   ❌ Completion failed: {result['error']}")
    
    # Test 4: Chat completion
    print("\n4. Testing chat completion...")
    result = client.chat_completion(
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Say hello in one sentence.'}
        ],
        max_tokens=30
    )
    if 'error' not in result:
        text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f"   ✅ Chat response: {text}")
    else:
        print(f"   ❌ Chat failed: {result['error']}")
    
    print("\n" + "="*60)
    print("CLIENT TEST COMPLETE")
    print("="*60)


if __name__ == '__main__':
    test_client()

