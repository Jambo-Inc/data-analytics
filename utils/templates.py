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

        tables = []
        for t in data.get('tables', []):
            tables.append(TableConfig(
                project_id=t.get('project_id', ''),
                dataset_id=t.get('dataset_id', ''),
                table_id=t.get('table_id', ''),
                description=t.get('description', '')
            ))

        # system_preambleにテーブル説明を自動追加
        system_preamble = data.get('system_preamble', '')
        system_preamble = _build_system_instruction(system_preamble, tables, data.get('relationships', []))

        return TemplateConfig(
            name=data.get('name', filename),
            description=data.get('description', ''),
            system_preamble=system_preamble,
            tables=tables,
            relationships=data.get('relationships', []),
            example_queries=data.get('example_queries', [])
        )
    except Exception as e:
        print(f"Error loading template {filename}: {e}")
        return None


def _build_system_instruction(base_instruction: str, tables: List[TableConfig], relationships: List[str]) -> str:
    """テーブル説明とリレーションをSystem Instructionに組み込む"""
    sections = [base_instruction.rstrip()]

    # テーブル説明セクション
    table_descriptions = []
    for t in tables:
        if t.description:
            table_name = f"{t.dataset_id}.{t.table_id}"
            table_descriptions.append(f"### {table_name}\n{t.description}")

    if table_descriptions:
        sections.append("## テーブル説明\n\n" + "\n\n".join(table_descriptions))

    # リレーションセクション
    if relationships:
        rel_text = "\n".join(f"- {r}" for r in relationships)
        sections.append(f"## テーブル間のリレーション\n\n{rel_text}")

    return "\n\n".join(sections)
