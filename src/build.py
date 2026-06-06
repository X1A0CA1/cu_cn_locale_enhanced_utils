"""
build.py - 合并翻译文件并输出到 outputs 目录
"""

import copy
import json
from pathlib import Path

# ── 路径配置 ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
SUBMODULE_JSON = (
    ROOT
    / "sub_module"
    / "krok_MP_chinese_locale"
    / "translations"
    / "translations.zh-CN.json"
)
OFFICIAL_JSON = ROOT / "sub_module" / "official" / "zh-CN.json"
PATCH_JSON = ROOT / "translate" / "enhanced_patch.json"
OUTPUT_DIR = ROOT / "outputs"

PARATRANZ_EXCLUDE = {"character", "notes", "pdaNotes", "pauseQuotes"}


def load_json(path: Path) -> dict:
    """读取 JSON 文件，保留插入顺序（Python 3.7+ dict 默认有序）。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def merge_into_other(base: dict, extra: dict) -> dict:
    """
    将 extra（flat dict）的所有 key 追加到 base["other"] 末尾。
    如有重复键，输出警告，以 official[other] 中的值为准。
    """
    other = base.get("other")
    if other is None:
        print("[INFO] 官方文件中未找到 'other' 节，将自动创建。")
        base["other"] = {}
        other = base["other"]

    duplicates = [k for k in extra if k in other]
    if duplicates:
        print("[WARN] 发现重复键，将以 official[other] 中的值为准：")
        for k in duplicates:
            print(f"  - {k}")

    for k, v in extra.items():
        if k not in other:
            other[k] = v

    return base


def apply_patch(base: dict, patch: dict) -> dict:
    """
    将 patch 中的 key/value 附加到 base 对应值的末尾（直接字符串拼接）。
    patch 的结构与 zh-CN.json 相同（带层级）。
    """
    for section_key, section_val in patch.items():
        if isinstance(section_val, dict):
            if section_key not in base:
                base[section_key] = {}
            for k, v in section_val.items():
                if k in base[section_key] and isinstance(base[section_key][k], str):
                    base[section_key][k] = base[section_key][k] + v
                else:
                    base[section_key][k] = v
        else:
            # 顶层标量直接覆盖（name、description 等）
            base[section_key] = section_val
    return base


def build_paratranz(merged_before_patch: dict, patch: dict) -> list:
    """
    生成 paratranz 格式列表。
    - original:    patch 应用前 merged 中的 value（即合并后、覆盖前的原文）
    - translation: patch 中对应的 value，若无则为 ""
    跳过非 dict 节及 PARATRANZ_EXCLUDE 中的节。
    """
    records = []

    for section_key, section_val in merged_before_patch.items():
        if not isinstance(section_val, dict):
            continue
        if section_key in PARATRANZ_EXCLUDE:
            continue

        patch_section = (
            patch.get(section_key, {})
            if isinstance(patch.get(section_key), dict)
            else {}
        )

        for k, v in section_val.items():
            full_key = f"{section_key}.{k}"
            translation = patch_section.get(k, "")
            records.append(
                {
                    "key": full_key,
                    "original": v,
                    "translation": translation,
                }
            )

    return records


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. 读取文件 ─────────────────────────────────────────────────────────
    print(f"[1/5] 读取子模块翻译: {SUBMODULE_JSON}")
    submodule_data: dict = load_json(SUBMODULE_JSON)

    print(f"[2/5] 读取官方翻译:   {OFFICIAL_JSON}")
    official_data: dict = load_json(OFFICIAL_JSON)

    print(f"[3/5] 读取补丁文件:   {PATCH_JSON}")
    patch_data: dict = load_json(PATCH_JSON)

    # ── 2. 合并子模块到 other ────────────────────────────────────────────────
    print("[4/5] 合并子模块翻译至 official[other] ...")
    merged = merge_into_other(official_data, submodule_data)

    # ── 3. 保存 patch 前快照（paratranz 的 original 从此处取值）─────────────
    merged_before_patch = copy.deepcopy(merged)

    # ── 4. 应用 patch ────────────────────────────────────────────────────────
    print("[5/5] 应用 enhanced_patch ...")
    merged = apply_patch(merged, patch_data)

    # ── 5. 输出 zh-CN_Enhanced.json ─────────────────────────────────────────
    enhanced_path = OUTPUT_DIR / "zh-CN_Enhanced.json"
    with open(enhanced_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)
    print(f"\n[OK] 已写出: {enhanced_path}")

    # ── 6. 输出 zh-CN_Enhanced_paratranz.json ───────────────────────────────
    paratranz_path = OUTPUT_DIR / "zh-CN_Enhanced_paratranz.json"
    records = build_paratranz(merged_before_patch, patch_data)
    with open(paratranz_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
    print(f"[OK] 已写出: {paratranz_path}  ({len(records)} 条记录)")


if __name__ == "__main__":
    main()
