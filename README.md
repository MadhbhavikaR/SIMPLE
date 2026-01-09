# S.I.M.P.L.E (Self-hosted Infrastructure Made Painless with Linux & Engineering)

## Quick Start
```sh
# 1. Clone & setup
git clone <this-repo> SIMPLE
cd home-infra-setup
chmod +x setup.sh
./setup.sh

# 2. Activate & run wizard
source activate
sudo python main.py

# 3. Deploy
cd docker
docker compose up -d

# 4. Validate
python -m pytest tests/ -v
```


### TODO:
1. Add support for custom files overrides/<path>/file.<ext>.jinja and rename <service>.yaml.jinja -> service.yaml.jinja 
2.use the detected os to have customization to move out of diet pi
3.add custome notifications like telegram, as service