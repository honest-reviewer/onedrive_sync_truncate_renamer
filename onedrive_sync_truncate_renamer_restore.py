#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 이 스크립트는 rename_backup.csv에 기록된 원본 ↔ 새이름 매핑을 바탕으로
# 잘못 변경된 파일 및 폴더 이름을 원래대로 복구합니다.

import csv
from pathlib import Path

# 복구할 백업 CSV 경로 (필요시 절대경로로 수정)
BACKUP_CSV = Path("rename_backup.csv")


def restore_names(csv_path: Path):
    """
    CSV의 각 행(new_path, original_path)을 읽어
    new_path가 존재할 경우 original_path로 rename 수행
    """
    if not csv_path.exists():
        print(f"[ERROR] 백업 CSV를 찾을 수 없습니다: {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # 헤더 스킵
        for row in reader:r
            if len(row) < 2:
                continue
            original_str, new_str = row[0], row[1]
            new_path = Path(new_str)
            orig_path = Path(original_str)

            if not new_path.exists():
                print(f"[SKIP] 복구 대상 없음: {new_path}")
                continue

            # 원본 디렉토리 없으면 생성
            orig_path.parent.mkdir(parents=True, exist_ok=True)

            if orig_path.exists():
                print(f"[EXISTS] 이미 원본 경로 존재, 건너뜀: {orig_path}")
                continue

            try:
                new_path.rename(orig_path)
                print(f"[RESTORED] {new_path} → {orig_path}")
            except Exception as e:
                print(f"[ERROR] 복구 실패: {new_path} → {orig_path} ({e})")

    print("✅ 복구 완료!")


if __name__ == "__main__":
    restore_names(BACKUP_CSV)
