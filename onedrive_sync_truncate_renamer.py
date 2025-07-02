#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 이 스크립트는 OneDrive 동기화 폴더 내에서
# - 전체 경로(파일 또는 폴더)가 지정한 바이트 수(MAX_FULL_PATH)를 초과하면
#   적절히 잘라서(cut) 길이를 줄이고,
# - 파일명(확장자 포함)이 지정한 바이트 수(MAX_NAME_BYTES)를 초과할 경우
#   잘라서 길이를 줄인 뒤 충돌 방지(_1, _2...)를 적용합니다.
# - Mac/APFS(HFS+) 및 Windows에서 호환되지 않는 특수 문자(예: 콜론, 물음표, 슬래시 등)를 제거합니다.
# 처리된 모든 원본→새이름 매핑은 날짜+시간이 포함된 CSV 파일에 백업됩니다.

import os
import re
import csv
import hashlib
from pathlib import Path
from datetime import datetime

# ─── 설정 ───────────────────────────────────────────────────────────────────
TARGET_DIR       = Path.home() / "OneDrive"    # 동기화할 OneDrive 최상위 폴더
MAX_FULL_PATH    = 980                          # 전체 경로(UTF-8) 최대 허용 바이트
MAX_NAME_BYTES   = 240                          # 파일명(확장자 포함) 최대 허용 바이트
# 날짜+시간 포맷으로 백업 CSV 파일명 생성
timestamp        = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_CSV       = Path(f"rename_backup_{timestamp}.csv")
INVALID_CHARS    = r'[<>:"/\\|?*]'             # 제거할 특수문자
# ─────────────────────────────────────────────────────────────────────────────

def sanitize(name: str) -> str:
    """
    파일명/폴더명에서 호환되지 않는 특수문자를 제거
    """
    return re.sub(INVALID_CHARS, "", name)


def cut_name(clean: str, ext: str, parent: Path) -> str:
    """
    clean: 특수문자 제거된 base name
    ext: ".확장자" 혹은 빈 문자열
    -> 이름+ext 전체가 MAX_NAME_BYTES 이하가 되도록 잘라냄
    -> 충돌 시 _1, _2… 붙임
    """
    max_base = MAX_NAME_BYTES - len(ext.encode("utf-8"))
    if max_base < 1:
        base = "_"
    else:
        base = ""
        for ch in clean:
            if len((base + ch).encode("utf-8")) <= max_base:
                base += ch
            else:
                break
        if not base:
            base = "_"

    candidate = f"{base}{ext}"
    counter = 1
    while (parent / candidate).exists():
        candidate = f"{base}_{counter}{ext}"
        counter += 1
    return candidate


def hash_name(full_path: str, ext: str, parent: Path) -> str:
    """
    전체 경로가 MAX_FULL_PATH 초과 시 MD5 해시 기반 이름 생성
    """
    h = hashlib.md5(full_path.encode("utf-8")).hexdigest()[:10]
    candidate = f"{h}{ext}"
    cnt = 1
    while (parent / candidate).exists():
        candidate = f"{h}_{cnt}{ext}"
        cnt += 1
    return candidate

# 백업 CSV 초기화 (날짜+시간 포함된 파일 생성)
with BACKUP_CSV.open("w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["original_path", "new_path"])

# 1) 파일 처리
for p in TARGET_DIR.rglob("*"):
    if not p.is_file():
        continue

    full_b = len(str(p).encode("utf-8"))
    if full_b <= MAX_FULL_PATH:
        continue

    parent, ext = p.parent, p.suffix
    stem = sanitize(p.stem)
    # 1) 파일명 잘라서 MAX_NAME_BYTES 이내로
    new_nm = cut_name(stem, ext, parent)
    new_p = parent / new_nm
    # 2) 여전히 전체 경로가 MAX_FULL_PATH 초과 시 해시로 리네임
    if len(str(new_p).encode("utf-8")) > MAX_FULL_PATH:
        new_nm = hash_name(str(p), ext, parent)
        new_p = parent / new_nm

    p.rename(new_p)
    print(f"[FILE] {full_b}B → {new_nm}")
    with BACKUP_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([str(p), str(new_p)])

# 2) 폴더 처리 (긴 경로 순)
dirs = [d for d in TARGET_DIR.rglob("*") if d.is_dir()]
for p in sorted(dirs, key=lambda x: len(str(x).encode("utf-8")), reverse=True):
    full_b = len(str(p).encode("utf-8"))
    if full_b <= MAX_FULL_PATH:
        continue

    parent = p.parent
    name = sanitize(p.name)
    # 폴더명 MAX_NAME_BYTES 기준으로 cut
    new_nm = cut_name(name, "", parent)
    new_p = parent / new_nm
    if len(str(new_p).encode("utf-8")) > MAX_FULL_PATH:
        new_nm = hash_name(str(p), "", parent)
        new_p = parent / new_nm

    p.rename(new_p)
    print(f"[DIR ] {full_b}B → {new_nm}")
    with BACKUP_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([str(p), str(new_p)])

print(f"✅ 완료! {BACKUP_CSV.name}에 매핑 저장됨.")
