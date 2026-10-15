from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from backend.app.agents.chat_assistant import ContractChatAgent
from backend.app.agents.clause_segmentation import ClauseSegmentationAgent
from backend.app.agents.document_ingestion import DocumentIngestionAgent
from backend.app.config import Settings
from backend.app.services.llm_client import LLMClient
from backend.app.services.pipeline import ContractAnalysisPipeline


SAMPLE = b"""SERVICE AGREEMENT

1. LIABILITY
The Client accepts unlimited liability for every direct and indirect loss under this Agreement.

2. TERMINATION
The Provider may terminate immediately without notice in its sole discretion.

3. CONFIDENTIALITY
Each party must protect confidential information and use it only for the services.
"""


class AgentTests(unittest.IsolatedAsyncioTestCase):
    def test_ingestion_and_segmentation(self):
        text = DocumentIngestionAgent().extract("agreement.txt", SAMPLE)
        clauses = ClauseSegmentationAgent().segment(text)
        self.assertGreaterEqual(len(clauses), 3)
        self.assertTrue(any("LIABILITY" in clause.title for clause in clauses))

    async def test_demo_pipeline_scores_risk(self):
        with TemporaryDirectory() as directory:
            target = Path(directory)
            settings = Settings(provider="demo", data_dir=target)
            result = await ContractAnalysisPipeline(settings).run("agreement.txt", SAMPLE)
            self.assertGreaterEqual(result.overall_risk_score, 70)
            self.assertGreaterEqual(result.risk_distribution.high, 1)
            self.assertTrue(result.risky_clauses[0].recommendation)
            self.assertGreater(len(result.risky_clauses[0].explanation), 180)
            self.assertGreater(len(result.risky_clauses[0].recommendation), 220)
            self.assertTrue((target / f"{result.contract_id}.json").exists())

    async def test_chat_refuses_off_topic(self):
        with TemporaryDirectory() as directory:
            settings = Settings(provider="demo", data_dir=Path(directory))
            analysis = await ContractAnalysisPipeline(settings).run("agreement.txt", SAMPLE)
            agent = ContractChatAgent(LLMClient(settings))
            response = await agent.answer(analysis, "Tell me a cricket joke")
            self.assertTrue(response.refused)
            self.assertIn("only help", response.answer)

    async def test_chat_accepts_plain_language_risk_question(self):
        with TemporaryDirectory() as directory:
            settings = Settings(provider="demo", data_dir=Path(directory))
            analysis = await ContractAnalysisPipeline(settings).run("agreement.txt", SAMPLE)
            agent = ContractChatAgent(LLMClient(settings))
            response = await agent.answer(analysis, "Tell me about the risks")
            self.assertFalse(response.refused)
            self.assertIn("risk", response.answer.lower())

    async def test_chat_gives_contract_wide_suggestions(self):
        with TemporaryDirectory() as directory:
            settings = Settings(provider="demo", data_dir=Path(directory))
            analysis = await ContractAnalysisPipeline(settings).run("agreement.txt", SAMPLE)
            agent = ContractChatAgent(LLMClient(settings))
            response = await agent.answer(analysis, "Give me suggestions for this contract")
            self.assertFalse(response.refused)
            self.assertIn("top changes", response.answer.lower())
            self.assertIn("1.", response.answer)
            self.assertNotIn("CONFIDENTIALITY", response.sources)

    async def test_chat_answers_distinct_contract_intents(self):
        with TemporaryDirectory() as directory:
            settings = Settings(provider="demo", data_dir=Path(directory))
            analysis = await ContractAnalysisPipeline(settings).run("agreement.txt", SAMPLE)
            agent = ContractChatAgent(LLMClient(settings))
            negotiation = await agent.answer(analysis, "Which clause should I negotiate first?")
            changes = await agent.answer(analysis, "What changes should be made to this contract?")
            signing = await agent.answer(analysis, "Should I sign this contract unchanged?")
            self.assertIn("negotiation priorities", negotiation.answer.lower())
            self.assertIn("change needed", changes.answer.lower())
            self.assertIn("not treat this contract as ready", signing.answer.lower())
            self.assertEqual(len({negotiation.answer, changes.answer, signing.answer}), 3)


if __name__ == "__main__":
    unittest.main()
