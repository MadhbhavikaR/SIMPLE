from .base import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class CloudflaredService(ServiceStrategy):
    name = "cloudflared"
    category = "gateway"
    
    @property
    def networks(self) -> List[str]:
        return ["net_edge"]
    
    def get_required_secrets(self) -> List[str]:
        return ["CF_DOCKER_TOKEN"]
    
    def generate_service_yaml(self, context: Dict[str, Any]) -> str:
        return f"""  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    hostname: cloudflared
    user: "{context['PUID']}:{context['PGID']}"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    networks:
      - net_edge
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m
    command: >
      tunnel --no-autoupdate run --token ${{CF_DOCKER_TOKEN}}
    restart: unless-stopped"""
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return [context['VOLUMES_DIR'] / 'cloudflared']

class SwagService(ServiceStrategy):
    name = "swag"
    category = "gateway"
    
    @property
    def networks(self) -> List[str]:
        return ["net_edge", "net_app"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def generate_service_yaml(self, context: Dict[str, Any]) -> str:
        volumes_dir = context['VOLUMES_DIR']
        return f"""  swag:
    image: lscr.io/linuxserver/swag:latest
    container_name: swag
    hostname: swag
    cap_add:
      - NET_ADMIN
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m
      - /run:rw,exec,nosuid,nodev,size=32m
    networks:
      - net_edge
      - net_app
    environment:
      - PUID={context['PUID']}
      - PGID={context['PGID']}
      - UMASK={context['UMASK']}
      - TZ={context['TZ']}
      - URL={context['DOMAIN']}
      - SUBDOMAINS=drive,books,memories,photos,auth
      - ONLY_SUBDOMAINS=true
      - STAGING={context['SWAG_STAGING']}
      - VALIDATION=dns
      - DNSPLUGIN=cloudflare
      - EMAIL={context['EMAIL']}
      - PROPAGATION=60
      - CROWDSEC_LAPI_URL=http://crowdsec:8080
    volumes:
      - {volumes_dir}/swag:/config:rw
    depends_on:
      - cloudflared
    restart: unless-stopped"""
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return [context['VOLUMES_DIR'] / 'swag']
