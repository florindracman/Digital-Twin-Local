import json
import importlib
import logging
from typing import Any, Dict, List

def load_plugins(config_path: str, context: Dict[str, Any]):
    with open(config_path) as f:
        cfg = json.load(f)

    plugins_cfg: List[Dict[str, Any]] = cfg.get("plugins", [])
    instances = []
    for p in plugins_cfg:
        if not p.get("enabled", False):
            continue
        module_name = p["module"]
        class_name = p["class"]
        name = p.get("name", class_name)
        try:
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            inst = cls(name=name, config=p.get("config", {}), context=context)
            inst.validate()
            inst.start()
            logging.info("Plugin started: %s (%s.%s)", name, module_name, class_name)
            instances.append(inst)
        except Exception:
            logging.exception("Failed to start plugin %s (%s.%s)", name, module_name, class_name)
    return instances