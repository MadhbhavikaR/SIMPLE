import subprocess
from typing import Dict, List, Optional, Any


from simple.config.config_reader import ConfigReader
from simple.config.models.servers import ServerDetectionResult
from simple.detectors.detector import Detector


class ServerDetector(Detector):
    """Detects running servers/services from YAML config using sockets + processes."""
    
    def __init__(self, config_reader: ConfigReader):
        super().__init__(config_reader)
        self.server_config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load servers config from YAML."""
        config_result = self.config_reader.read_yaml_config("servers")
        if not config_result.success:
            print(f"⚠️  Warning: servers.yaml not found: {config_result.error}")
            return {}
        return config_result.data.get("services", {})
    
    def detect(self) -> Dict[str, ServerDetectionResult]:
        """Bulk detection - fetches socket/process data ONCE PER INVOCATION."""
        print("🔍 Starting bulk server detection...")
        
        # Fresh data for each invocation - no instance caching
        socket_lines = self._get_fresh_socket_data()
        process_lines = self._get_fresh_process_data()
        
        self.detected: Dict[str, ServerDetectionResult] = {}
        
        if not socket_lines and not process_lines:
            print("⚠️  No socket/process data available")
            return self.detected
        
        # Single pass detection for all services using fresh data
        for keyword, config in self.server_config.items():
            result = self._detect_single_server(keyword, config, socket_lines, process_lines)
            self.detected[keyword] = result
        
        return self.detected
    
    def _get_fresh_socket_data(self) -> List[str]:
        """Get fresh socket data every invocation."""
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.splitlines()
        except:
            pass
        
        try:
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.splitlines()
        except:
            pass
        
        return []
    
    def _get_fresh_process_data(self) -> List[str]:
        """Get fresh process data every invocation."""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.splitlines()
        except:
            pass
        
        try:
            result = subprocess.run(['ps', '-ef'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.splitlines()
        except:
            pass
        
        return []
    
    def _detect_single_server(self, keyword: str, config: Dict, 
                            socket_lines: List[str], process_lines: List[str]) -> ServerDetectionResult:
        """Detect single server using fresh socket + process data."""
        keywords = config.get("keywords", [keyword])
        default_ports = config.get("default_port", [])
        if isinstance(default_ports, int):
            default_ports = [default_ports]
        
        detected_port = None
        process_name = None
        
        # 1. Check PROCESSES first
        for line in process_lines:
            low_line = line.lower()
            for kword in keywords:
                if kword.lower() in low_line:
                    process_name = kword
                    break
            if process_name:
                break
        
        # 2. Check SOCKETS for port
        for line in socket_lines:
            low_line = line.lower()
            
            # Socket keyword match
            for kword in keywords:
                if kword.lower() in low_line:
                    port = self._extract_port_from_line(line)
                    if port:
                        detected_port = port
                        process_name = process_name or kword
                        break
            
            # Default port match
            for port in default_ports:
                if f":{port} " in line or line.strip().endswith(f":{port}"):
                    port_num = self._extract_port_from_line(line)
                    if port_num:
                        detected_port = port_num
                        break
            
            if detected_port:
                break
        
        return ServerDetectionResult(
            keyword=keyword,
            detected_port=detected_port,
            process_name=process_name
        )
    
    def _extract_port_from_line(self, line: str) -> Optional[int]:
        """Extract port from ss/netstat line."""
        parts = line.split()
        if len(parts) < 4:
            return None
        
        addr = parts[3]
        if addr.startswith('[') and ']' in addr:
            addr = addr.rsplit(']', 1)[-1]
        
        if ':' in addr:
            try:
                return int(addr.split(':')[-1])
            except ValueError:
                pass
        return None
    
    def print_summary(self) -> bool:
        """Print server detection summary."""
        print(f"\n🖥️  SERVER DETECTION SUMMARY")
        print("-" * 65)
        
        detected_count = sum(1 for result in self.detected.values() if result.detected_port or result.process_name)
        total = len(self.detected)
        
        for keyword, result in self.detected.items():
            if result.detected_port:
                status = "✅ RUNNING"
                port_info = f"port {result.detected_port}"
            elif result.process_name:
                status = "⚠️  PROCESS"
                port_info = "no socket"
            else:
                status = "❌ NOT FOUND"
                port_info = "N/A"
            
            proc_info = f"({result.process_name})" if result.process_name else ""
            print(f"{status:<12} | {keyword:<12} | {port_info:<10} {proc_info}")
        
        print(f"\n🎯 {detected_count}/{total} servers detected")
        return detected_count > 0
