from __future__ import annotations

import logging
import json
from typing import List, Dict, Any
from datetime import datetime
from agent.react_agent import get_react_agent

logger = logging.getLogger(__name__)


class AgentEvaluator:
    def __init__(self, agent: Any = None):
        self.agent = agent or get_react_agent("eval_user")
        self.results = []
        self.test_queries = self._create_test_queries()
    
    def _create_test_queries(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "TEST001",
                "query": "What is the price of the Premium Wireless Headphones?",
                "category": "product_info",
                "expected_keywords": ["199.99", "headphones", "price"]
            },
            {
                "id": "TEST002",
                "query": "What is your return policy?",
                "category": "policy",
                "expected_keywords": ["30 days", "return", "original condition"]
            },
            {
                "id": "TEST003",
                "query": "I have a Smart Watch Pro and want to know about water resistance",
                "category": "product_features",
                "expected_keywords": ["water resistant", "50 meters", "ATM"]
            },
            {
                "id": "TEST004",
                "query": "How long does standard shipping take?",
                "category": "shipping",
                "expected_keywords": ["5-7", "business days", "standard"]
            },
            {
                "id": "TEST005",
                "query": "Can I use the USB-C charger with my iPhone?",
                "category": "compatibility",
                "expected_keywords": ["USB-C", "compatible", "cable"]
            },
            {
                "id": "TEST006",
                "query": "Look up my order ORD001",
                "category": "order_lookup",
                "expected_keywords": ["ORD001", "status", "delivered"]
            },
            {
                "id": "TEST007",
                "query": "What are the current promotions?",
                "category": "pricing",
                "expected_keywords": ["promotion", "discount", "off"]
            },
            {
                "id": "TEST008",
                "query": "I'm having issues with my headphones, please help",
                "category": "troubleshooting",
                "expected_keywords": ["support", "issue", "help"]
            }
        ]
    
    def evaluate_query(self, test_query: Dict[str, str]) -> Dict[str, Any]:
        query_id = test_query["id"]
        query_text = test_query["query"]
        expected_keywords = test_query.get("expected_keywords", [])
        
        logger.info(f"Evaluating query {query_id}: {query_text}")
        
        response, metadata = self.agent.process_input(query_text)
        
        accuracy_score = self._calculate_accuracy(response, expected_keywords)
        hallucination_score = self._detect_hallucination(response, test_query)
        relevance_score = self._calculate_relevance(response, query_text)
        
        result = {
            "query_id": query_id,
            "query": query_text,
            "category": test_query.get("category"),
            "response": response,
            "response_length": len(response),
            "metrics": {
                "accuracy_score": accuracy_score,
                "hallucination_score": hallucination_score,
                "relevance_score": relevance_score,
                "overall_score": (accuracy_score + (1 - hallucination_score) + relevance_score) / 3
            },
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def _calculate_accuracy(self, response: str, expected_keywords: List[str]) -> float:
        if not expected_keywords:
            return 0.5
        
        found = sum(1 for keyword in expected_keywords if keyword.lower() in response.lower())
        return found / len(expected_keywords)
    
    def _detect_hallucination(self, response: str, test_query: Dict) -> float:
        hallucination_indicators = [
            "I cannot verify",
            "based on my training",
            "I'm not sure but",
            "I assume",
            "probably",
            "I guess"
        ]
        
        suspicious_count = sum(
            1 for indicator in hallucination_indicators 
            if indicator.lower() in response.lower()
        )
        
        return min(suspicious_count / 3, 1.0)
    
    def _calculate_relevance(self, response: str, query: str) -> float:
        if len(response) < 20:
            return 0.3
        
        error_indicators = [
            "error",
            "unable to process",
            "failed",
            "could not find"
        ]
        
        if any(indicator in response.lower() for indicator in error_indicators):
            return 0.6
        
        return 0.9
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        logger.info(f"Running full evaluation with {len(self.test_queries)} test queries")
        
        for test_query in self.test_queries:
            self.evaluate_query(test_query)
        
        summary = self._calculate_summary()
        return summary
    
    def _calculate_summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}
        
        accuracy_scores = [r["metrics"]["accuracy_score"] for r in self.results]
        hallucination_scores = [r["metrics"]["hallucination_score"] for r in self.results]
        relevance_scores = [r["metrics"]["relevance_score"] for r in self.results]
        overall_scores = [r["metrics"]["overall_score"] for r in self.results]
        
        return {
            "total_queries": len(self.results),
            "average_accuracy": sum(accuracy_scores) / len(accuracy_scores),
            "average_hallucination": sum(hallucination_scores) / len(hallucination_scores),
            "average_relevance": sum(relevance_scores) / len(relevance_scores),
            "average_overall_score": sum(overall_scores) / len(overall_scores),
            "timestamp": datetime.now().isoformat(),
            "results": self.results
        }
    
    def save_results(self, filepath: str = "data/evaluation_results.json") -> None:
        summary = self._calculate_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Evaluation results saved to {filepath}")
    
    def print_summary(self) -> None:
        summary = self._calculate_summary()
        
        print("\n" + "="*60)
        print("AGENT EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Queries: {summary.get('total_queries', 0)}")
        print(f"Average Accuracy: {summary.get('average_accuracy', 0):.2%}")
        print(f"Average Hallucination: {summary.get('average_hallucination', 0):.2%}")
        print(f"Average Relevance: {summary.get('average_relevance', 0):.2%}")
        print(f"Overall Score: {summary.get('average_overall_score', 0):.2%}")
        print("="*60 + "\n")
        
        print("Detailed Results:")
        for result in summary.get('results', []):
            print(f"\n{result['query_id']}: {result['category']}")
            print(f"  Query: {result['query'][:50]}...")
            print(f"  Score: {result['metrics']['overall_score']:.2%}")