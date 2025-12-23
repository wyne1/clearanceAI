import logging
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from app.services.llm_provider import PricingInfo

logger = logging.getLogger(__name__)


@dataclass
class RequestRecord:
    """Record of a single LLM request with pricing."""
    timestamp: datetime
    provider: str
    model: str
    function_name: str
    input_tokens: int
    output_tokens: int
    total_cost: float
    request_id: str = ""


class PricingTracker:
    """Tracks pricing and usage for LLM requests."""
    
    def __init__(self):
        self.requests: List[RequestRecord] = []
        self._cumulative_cost = 0.0
        self._request_count = 0
    
    def record_request(
        self,
        pricing_info: PricingInfo,
        function_name: str,
        request_id: str = ""
    ) -> None:
        """
        Record a request with its pricing information.
        
        Args:
            pricing_info: PricingInfo from the provider
            function_name: Name of the function making the request
            request_id: Optional request identifier
        """
        record = RequestRecord(
            timestamp=datetime.now(),
            provider=pricing_info.provider,
            model=pricing_info.model,
            function_name=function_name,
            input_tokens=pricing_info.input_tokens,
            output_tokens=pricing_info.output_tokens,
            total_cost=pricing_info.total_cost,
            request_id=request_id
        )
        
        self.requests.append(record)
        self._cumulative_cost += pricing_info.total_cost
        self._request_count += 1
        
        logger.info(
            f"💰 Pricing: {pricing_info.provider}/{pricing_info.model} - "
            f"${pricing_info.total_cost:.6f} "
            f"({pricing_info.input_tokens} in, {pricing_info.output_tokens} out) - "
            f"Function: {function_name}"
        )
    
    def get_cumulative_stats(self) -> Dict[str, Any]:
        """
        Get cumulative statistics.
        
        Returns:
            Dictionary with cumulative stats
        """
        provider_breakdown = {}
        for record in self.requests:
            provider_key = f"{record.provider}/{record.model}"
            if provider_key not in provider_breakdown:
                provider_breakdown[provider_key] = {
                    "requests": 0,
                    "total_cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            
            provider_breakdown[provider_key]["requests"] += 1
            provider_breakdown[provider_key]["total_cost"] += record.total_cost
            provider_breakdown[provider_key]["input_tokens"] += record.input_tokens
            provider_breakdown[provider_key]["output_tokens"] += record.output_tokens
        
        return {
            "total_requests": self._request_count,
            "cumulative_cost": self._cumulative_cost,
            "average_cost_per_request": self._cumulative_cost / self._request_count if self._request_count > 0 else 0.0,
            "provider_breakdown": provider_breakdown
        }
    
    def get_function_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics broken down by function.
        
        Returns:
            Dictionary keyed by function name with stats
        """
        function_stats = {}
        for record in self.requests:
            if record.function_name not in function_stats:
                function_stats[record.function_name] = {
                    "requests": 0,
                    "total_cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            
            function_stats[record.function_name]["requests"] += 1
            function_stats[record.function_name]["total_cost"] += record.total_cost
            function_stats[record.function_name]["input_tokens"] += record.input_tokens
            function_stats[record.function_name]["output_tokens"] += record.output_tokens
        
        return function_stats
    
    def log_summary(self) -> None:
        """Log a summary of all pricing information."""
        stats = self.get_cumulative_stats()
        function_stats = self.get_function_stats()
        
        logger.info("=" * 60)
        logger.info("📊 PRICING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Requests: {stats['total_requests']}")
        logger.info(f"Cumulative Cost: ${stats['cumulative_cost']:.6f}")
        logger.info(f"Average Cost per Request: ${stats['average_cost_per_request']:.6f}")
        logger.info("")
        logger.info("Provider Breakdown:")
        for provider, data in stats['provider_breakdown'].items():
            logger.info(f"  {provider}:")
            logger.info(f"    Requests: {data['requests']}")
            logger.info(f"    Total Cost: ${data['total_cost']:.6f}")
            logger.info(f"    Avg Cost: ${data['total_cost']/data['requests']:.6f}")
            logger.info(f"    Tokens: {data['input_tokens']:,} in, {data['output_tokens']:,} out")
        logger.info("")
        logger.info("Function Breakdown:")
        for func_name, data in function_stats.items():
            logger.info(f"  {func_name}:")
            logger.info(f"    Requests: {data['requests']}")
            logger.info(f"    Total Cost: ${data['total_cost']:.6f}")
            logger.info(f"    Avg Cost: ${data['total_cost']/data['requests']:.6f}")
        logger.info("=" * 60)
    
    def reset(self) -> None:
        """Reset all tracking data."""
        self.requests.clear()
        self._cumulative_cost = 0.0
        self._request_count = 0
        logger.info("🔄 Pricing tracker reset")


# Global instance
_pricing_tracker = PricingTracker()


def get_pricing_tracker() -> PricingTracker:
    """Get the global pricing tracker instance."""
    return _pricing_tracker

