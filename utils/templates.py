"""テンプレート管理ユーティリティ"""
import os
import yaml
from typing import List, Dict, Optional
from dataclasses import dataclass

CONTEXTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contexts")


@dataclass
class TableConfig:
    project_id: str
    dataset_id: str
    table_id: str
    description: str = ""


@dataclass
class TemplateConfig:
    name: str
    description: str
    system_preamble: str
    tables: List[TableConfig]
    relationships: List[str]
    example_queries: List[Dict]


def list_templates() -> List[str]:
    """contexts/内のYAMLファイル一覧を取得"""
    if not os.path.exists(CONTEXTS_DIR):
        return []
    return [f for f in os.listdir(CONTEXTS_DIR) if f.endswith('.yaml')]


def load_template(filename: str) -> Optional[TemplateConfig]:
    """YAMLテンプレートを読み込み"""
    filepath = os.path.join(CONTEXTS_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        tables = [
            TableConfig(
                project_id=t.get('project_id', ''),
                dataset_id=t.get('dataset_id', ''),
                table_id=t.get('table_id', ''),
                description=t.get('description', '')
            )
            for t in data.get('tables', [])
        ]
        return TemplateConfig(
            name=data.get('name', filename),
            description=data.get('description', ''),
            system_preamble=data.get('system_preamble', ''),
            tables=tables,
            relationships=data.get('relationships', []),
            example_queries=data.get('example_queries', [])
        )
    except Exception as e:
        print(f"Error loading template {filename}: {e}")
        return None
