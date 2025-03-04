import os
import re
import shutil
import sys

def extract_wav(file_path):
    # WAVのヘッダーパターン
    wav_signature = b"RIFF....WAVE"
    
    # ファイル全体を読み込む
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    # 出力フォルダの作成
    output_dir = "output/wav"
    os.makedirs(output_dir, exist_ok=True)
    
    # WAVデータの検索と抽出
    matches = list(re.finditer(wav_signature, file_data))
    
    positions = []
    file_map = {}
    
    for i, match in enumerate(matches):
        start = match.start()
        
        # WAVヘッダーからファイルサイズを取得
        size = int.from_bytes(file_data[start+4:start+8], byteorder="little") + 8
        
        audio_data = file_data[start:start+size]
        output_path = os.path.join(output_dir, f"audio_{i}.wav")
        
        with open(output_path, "wb") as f:
            f.write(audio_data)
        print(f"抽出完了: {output_path}")
        
        positions.append((start, size))
        file_map[f"audio_{i}.wav"] = (start, size)
    
    return file_map, file_data

def make_wav(file_path, file_map):
    input_dir = "input"
    mod_file_path = file_path.replace(".BIN", "_MOD.BIN")
    
    # 元のファイルをコピーして編集用ファイルを作成
    shutil.copy(file_path, mod_file_path)
    
    # 編集用ファイルをバイナリとして読み込み
    with open(mod_file_path, "rb") as f:
        file_data = bytearray(f.read())
    
    offset_shift = 0
    new_file_data = bytearray()
    current_pos = 0
    
    for filename, (start, size) in sorted(file_map.items(), key=lambda x: x[1][0]):
        input_path = os.path.join(input_dir, filename)
        
        if not os.path.exists(input_path):
            new_file_data.extend(file_data[current_pos:start])
            new_file_data.extend(file_data[start:start+size])
            current_pos = start + size
            continue  # ファイルがない場合はスキップ
        
        with open(input_path, "rb") as f:
            wav_data = f.read()
        
        new_file_data.extend(file_data[current_pos:start])
        new_file_data.extend(wav_data)
        offset_shift += len(wav_data) - size
        current_pos = start + size
        print(f"書き込み完了: {filename}")
    
    new_file_data.extend(file_data[current_pos:])
    
    # 書き戻し
    with open(mod_file_path, "wb") as f:
        f.write(new_file_data)
    print(f"編集後のファイルを保存しました: {mod_file_path}")

def main():
    # ドラッグ＆ドロップ対応
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("処理するファイル名を入力してください (例: D1PGM311.BIN): ").strip()
    
    if not os.path.exists(file_path):
        print("エラー: 指定されたファイルが見つかりません。")
        return
    
    if not file_path.lower().endswith(".bin"):
        print("エラー: .BIN ファイルのみ対応しています。")
        return
    
    mode = input("モードを選択してください: 抽出モード (E) / 作成モード (M): ").strip().lower()
    
    if mode == "e":
        file_map, _ = extract_wav(file_path)
    elif mode == "m":
        file_map, _ = extract_wav(file_path)  # 位置情報を取得
        make_wav(file_path, file_map)
    else:
        print("エラー: 無効なモードが選択されました。")

if __name__ == "__main__":
    main()
