# onedrive_sync_truncate_renamer
원드라이브 상에서 "파일 다운로드 중" 무한 현상을 해결하기 위한 파이썬 코드


해당 코드들은 모두 ChatGPT로 제작했으며 이 코드를 실행해서 발생하는 문제에 대하여 책임지지 않습니다.

<img width="342" alt="image" src="https://github.com/user-attachments/assets/238eb5eb-af1d-4168-853f-1cb2abc9c10e" />

onedrive_sync_truncate.renamer.py 를 실행시키는 곳은 조건이 있습니다.

onedrive 에서 최상위 폴더에 두고 실행 시켜야 합니다.

예를 들면 /Users/[사용자명]/Onedrive/onedrive_sync_truncate_renamer.py 

저기에 위치한 상태로,

cmd 터미널에서도 cd /User/[사용자명]/Onedrive 경로에서 하셔야 함.

python onedrive_sync_truncate_renamer.py 

입력 인자는 없고 그냥 실행시키면 됩니다.

근데 갑자기 내가 원래 했던 것들을 원상복구 하고 싶다?

<img width="278" alt="image" src="https://github.com/user-attachments/assets/72b7038a-f9de-46a4-9353-0221833b22f6" />

그럼 그 rename_backup_[코드 실행한 시간].csv 이런 파일이 생길겁니다.

이걸 인자로 

python onedrive_sync_truncate_renamer_restore.py rename_backup_[코드 실행한 시간].csv

이렇게 해주면 다시 원상복구 되니 참고 하시길 바랍니다.

