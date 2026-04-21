from __future__ import annotations

import pytest
from agent.react_agent import ReActAgent


class TestReActAgent:
    @pytest.fixture
    def agent(self):
        return ReActAgent(user_id="test_user")
    
    def test_agent_initialization(self, agent):
        assert agent.user_id == "test_user"
        assert agent.tools is not None
        assert len(agent.tools) > 0
    
    def test_agent_info(self, agent):
        info = agent.get_agent_info()
        assert "model" in info
        assert "tools_count" in info
        assert info["tools_count"] > 0
    
    def test_memory_manager(self, agent):
        summary = agent.get_conversation_summary()
        assert "user_id" in summary
        assert "message_count" in summary


if __name__ == "__main__":
    pytest.main([__file__])