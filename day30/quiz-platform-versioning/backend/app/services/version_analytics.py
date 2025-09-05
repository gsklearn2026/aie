from typing import Dict, List, Any
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import asyncio
import json

class VersionAnalyticsService:
    def __init__(self):
        self.usage_data = defaultdict(list)
        self.daily_stats = defaultdict(lambda: defaultdict(int))
    
    async def record_usage(self, version: str, endpoint: str, user_agent: str, client_ip: str):
        """Record API version usage"""
        timestamp = datetime.now()
        
        usage_record = {
            "timestamp": timestamp.isoformat(),
            "version": version,
            "endpoint": endpoint,
            "user_agent": user_agent,
            "client_ip": client_ip
        }
        
        self.usage_data[version].append(usage_record)
        
        # Update daily stats
        date_key = timestamp.date().isoformat()
        self.daily_stats[date_key][version] += 1
    
    def get_version_distribution(self) -> Dict[str, int]:
        """Get current version usage distribution"""
        total_usage = Counter()
        
        for version, records in self.usage_data.items():
            total_usage[version] = len(records)
        
        return dict(total_usage)
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Dict[str, int]]:
        """Get daily version usage stats"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        result = {}
        for i in range(days):
            date = (start_date + timedelta(days=i)).isoformat()
            result[date] = dict(self.daily_stats.get(date, {}))
        
        return result
    
    def get_endpoint_popularity(self, version: str = None) -> Dict[str, int]:
        """Get most popular endpoints by version"""
        endpoint_counts = Counter()
        
        if version:
            records = self.usage_data.get(version, [])
            for record in records:
                endpoint_counts[record["endpoint"]] += 1
        else:
            for version_records in self.usage_data.values():
                for record in version_records:
                    endpoint_counts[record["endpoint"]] += 1
        
        return dict(endpoint_counts.most_common(10))
    
    def get_client_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get client type breakdown by version"""
        client_breakdown = defaultdict(lambda: defaultdict(int))
        
        for version, records in self.usage_data.items():
            for record in records:
                user_agent = record["user_agent"].lower()
                client_type = self.classify_client(user_agent)
                client_breakdown[version][client_type] += 1
        
        return {v: dict(clients) for v, clients in client_breakdown.items()}
    
    def classify_client(self, user_agent: str) -> str:
        """Classify client type from user agent"""
        user_agent = user_agent.lower()
        
        if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
            return "mobile"
        elif "chrome" in user_agent or "firefox" in user_agent or "safari" in user_agent:
            return "web_browser"
        elif "curl" in user_agent or "wget" in user_agent or "python" in user_agent:
            return "api_client"
        else:
            return "unknown"
    
    def get_deprecation_impact(self) -> Dict[str, Any]:
        """Analyze impact of deprecating old versions"""
        distribution = self.get_version_distribution()
        total_requests = sum(distribution.values())
        
        if total_requests == 0:
            return {"impact": "none", "affected_requests": 0}
        
        # Calculate impact of deprecating v1
        v1_usage = distribution.get("v1", 0)
        impact_percentage = (v1_usage / total_requests) * 100
        
        return {
            "deprecated_version": "v1",
            "affected_requests": v1_usage,
            "total_requests": total_requests,
            "impact_percentage": round(impact_percentage, 2),
            "recommendation": self.get_deprecation_recommendation(impact_percentage)
        }
    
    def get_deprecation_recommendation(self, impact_percentage: float) -> str:
        """Get recommendation for version deprecation"""
        if impact_percentage < 5:
            return "Safe to deprecate - minimal impact"
        elif impact_percentage < 15:
            return "Proceed with caution - moderate impact"
        elif impact_percentage < 30:
            return "High impact - extend deprecation timeline"
        else:
            return "Critical impact - reconsider deprecation"

# Global analytics instance
analytics_service = VersionAnalyticsService()
