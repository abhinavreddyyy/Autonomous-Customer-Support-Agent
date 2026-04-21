from __future__ import annotations

#!/usr/bin/env python3
import logging
from evaluation.evaluate_agent import AgentEvaluator
from agent.react_agent import get_react_agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("\n" + "="*60)
    print("AGENT EVALUATION SCRIPT")
    print("="*60 + "\n")
    
    logger.info("Initializing evaluator...")
    agent = get_react_agent("eval_user")
    evaluator = AgentEvaluator(agent)
    
    logger.info("Running evaluation...")
    summary = evaluator.run_full_evaluation()
    
    evaluator.print_summary()
    evaluator.save_results()
    
    print("\nEvaluation complete! Results saved to data/evaluation_results.json")


if __name__ == "__main__":
    main()