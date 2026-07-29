"""
Weather Agent - Lấy thông tin thời tiết
"""

from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel


class WeatherAgent(BaseAgent):
    """Agent thời tiết"""
    
    agent_name = "weather"
    agent_description = "Lấy thông tin thời tiết hiện tại và dự báo"
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self._api_key = api_key
        
        self.register_tool(
            ToolSchema(
                name="get_weather",
                description="Lấy thông tin thời tiết hiện tại cho 1 thành phố",
                parameters={"city": {"type": "string", "description": "Tên thành phố (vd: Hà Nội, Hồ Chí Minh)"}},
                risk_level=RiskLevel.SAFE,
                requires_online=True,
                estimated_time=2.0
            ),
            self._get_weather
        )
    
    def set_api_key(self, key: str):
        self._api_key = key
    
    def _get_weather(self, city: str) -> ToolResult:
        """Lấy thời tiết từ OpenWeatherMap"""
        if not self._api_key:
            # Thử dùng wttr.in (không cần API key)
            return self._get_weather_wttr(city)
        
        try:
            import requests
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": self._api_key,
                "units": "metric",
                "lang": "vi"
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            if resp.status_code != 200:
                return ToolResult(success=False, error=data.get("message", "Unknown error"))
            
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            desc = data["weather"][0]["description"]
            wind = data["wind"]["speed"]
            
            text = (
                f"Thời tiết {city}: {desc}, nhiệt độ {temp:.0f}°C "
                f"(cảm giác {feels_like:.0f}°C), độ ẩm {humidity}%, "
                f"gió {wind:.1f} m/s"
            )
            
            return ToolResult(success=True, data={
                "text": text,
                "city": city,
                "temp": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "description": desc,
                "wind": wind
            })
        except ImportError:
            return self._get_weather_wttr(city)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _get_weather_wttr(self, city: str) -> ToolResult:
        """Fallback: dùng wttr.in"""
        try:
            import requests
            url = f"https://wttr.in/{city}?format=j1&lang=vi"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            current = data["current_condition"][0]
            temp = current["temp_C"]
            feels_like = current["FeelsLikeC"]
            humidity = current["humidity"]
            desc = current["weatherDesc"][0]["value"]
            wind = current["windspeedKmph"]
            
            text = (
                f"Thời tiết {city}: {desc}, nhiệt độ {temp}°C "
                f"(cảm giác {feels_like}°C), độ ẩm {humidity}%, "
                f"gió {wind} km/h"
            )
            
            return ToolResult(success=True, data={
                "text": text,
                "city": city,
                "temp": int(temp),
                "feels_like": int(feels_like),
                "humidity": int(humidity),
                "description": desc,
                "wind": int(wind)
            })
        except ImportError:
            return ToolResult(success=False, error="Cần cài requests: pip install requests")
        except Exception as e:
            return ToolResult(success=False, error=str(e))