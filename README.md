# obd2_monitor

Raspberry Pi 上で CAN バス（OBD2）の受信、ロータリーエンコーダー入力、LCD 表示を行うモニタリングプログラムです。

**本プログラムは Raspberry Pi 5 および Raspberry Pi Zero 2 W 向けに作成されています。**  
GPIO ピン配置・I2C バス番号・ライブラリ（`rpi-lgpio`）はこの2機種を前提としています。他の Raspberry Pi モデルでは動作しない、または設定変更が必要な場合があります。

## 概要

`main.py` は次の機能を並列スレッドで動作させます。

| 機能 | 説明 | 関連モジュール |
|------|------|----------------|
| CAN 受信 | Seeed I2C-CAN モジュール（0x25）経由で CAN フレームを受信。参考：https://jp.seeedstudio.com/I2C-CAN-Bus-Module-p-5054.html | `lib/i2c_can.py` |
| LCD 表示 | 受信した CAN ID・データ、ロータリーエンコーダー状態を 16x2 LCD に表示。参考：https://jp.seeedstudio.com/Grove-16x2-LCD-White-on-Blue.html | `lib/lcd1602.py` |
| ロータリーエンコーダー | 2 系統のロータリーエンコーダー＋プッシュスイッチ＋RGB LED を監視。 参考：https://akizukidenshi.com/catalog/g/g105773/ | `switch.py` |
| USB ログ | オプションで USB ストレージへ CAN ログを追記 | `config.py` |

### 動作の流れ

1. 起動時に I2C-CAN モジュールを初期化（ボーレート・フィルタ設定）
2. バックグラウンドスレッドを起動
   - **I2C-CAN スレッド**: CAN フレームをポーリング受信し、コールバックでコンソール出力
   - **ロータリーエンコーダースレッド**: 2 系統のエンコーダー回転・スイッチ押下を検出
   - **LCD スレッド**: 最新の CAN データとスイッチ状態を LCD に表示
3. メインスレッドは待機し、`Ctrl-C` で終了

## 対応ハードウェア

### Raspberry Pi

| 機種 | 対応 |
|------|------|
| Raspberry Pi 5 | 対応（開発・動作確認済み） |
| Raspberry Pi Zero 2 W | 対応（開発・動作確認済み） |
| その他（Zero W 初代など） | 非対応。I2C タイミングや GPIO ライブラリの違いにより動作保証外 |

### 周辺機器

- **I2C-CAN モジュール**: [Seeed I2C-CAN Bus Module](https://www.seeedstudio.com/I2C-CAN-Bus-Module-p-5054.html)（I2C アドレス `0x25`）
- **LCD**: I2C 接続の 16x2 キャラクタ LCD（PCF8574 ベース）
- **ロータリーエンコーダー**: 2 系統（各 A/B 相 + プッシュスイッチ + RGB LED）

### Pi Zero 2 W + Seeed I2C-CAN (0x25) 配線

| Pi ピン | 信号 | モジュール |
|--------|------|-----------|
| 1 | 3.3V | VCC |
| 3 | SDA (GPIO2) | SDA |
| 5 | SCL (GPIO3) | SCL |
| 6 | GND | GND |

## セットアップ

### 1. I2C 有効化

```/boot/firmware/config.txt
# I2C CH1を有効にする
dtparam=i2c_arm=on
# enable IC2C0
dtoverlay=i2c0,pins_0_1
```
CH0, 1が有効になっていることを確認
```/boot/firmware/config.txt
i2cdetect -y 0
i2cdetect -y 1
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

主な依存関係:

- `rpi-lgpio` — Raspberry Pi 5 / Zero 2 W 向け GPIO
- `gpiozero` — RGB LED 制御
- `smbus2` — I2C 通信

### 3. 設定（`config.py`）

| 設定項目 | 説明 | 既定値 |
|----------|------|--------|
| `I2C_CAN_CH` | I2C-CAN のバス番号（`/dev/i2c-N`） | `1` |
| `I2C_CAN_ADDR` | I2C-CAN のアドレス | `0x25` |
| `I2C_CAN_BAUD` | CAN ボーレート | `500 kbps` |
| `I2C_CAN_FILTER_MODE` | 受信フィルタ（下記参照） | `"none"` |
| `LCD_I2C_CH` | LCD の I2C バス番号 | `0` |
| `pin_id_rot_*` | ロータリーエンコーダー・LED の GPIO 番号（BCM） | 各ピン定義を参照 |

**`I2C_CAN_FILTER_MODE` の値:**

| 値 | 動作 |
|----|------|
| `"none"` | モジュールのデフォルト設定（USB-CAN テスト向け） |
| `"obd"` | 車両 OBD 向け。ID `0x7E8` のみハードウェアフィルタ |
| `"all"` | 全 CAN ID を受信 |

LCD と I2C-CAN を同じ配線に接続する場合は、**同じ I2C バス番号**に揃えてください。

### 4. 機能の有効/無効（`main.py` 先頭）

```python
is_use_rotary_encoder = True   # ロータリーエンコーダー
is_use_i2c_can = True          # I2C-CAN 受信
is_use_lcd = True              # LCD 表示
is_use_usb_storage = True      # USB へのログ書き込み
```

## 実行

```bash
python main.py
```

終了は `Ctrl-C` です。終了処理が完了するまで数秒待ってください。

VS Code / Cursor からは `.vscode/launch.json` の **Python: main.py** でデバッグ起動できます。

## テスト・診断用スクリプト

### I2C バススキャン

```bash
python lib/i2c_scan.py
# または
sudo i2cdetect -y 0
sudo i2cdetect -y 1
```

`0x25`（I2C-CAN）が表示されることを確認してください。

### CAN 受信テスト（Pi のみ）

```bash
python lib/i2c_can_test.py
```

USB-CAN アダプタから 500 kbps でフレームを送信して受信を確認します。  
`filter=obd` のとき `0x7E8` 以外はハードウェアで破棄されます。

### LCD テスト

```bash
python lcd_test.py
```

## トラブルシューティング

### I2C-CAN が `i2cdetect` に出ない

- 配線（SDA / SCL / GND / 3.3V）と SDA・SCL の逆接続を確認
- Pi とモジュールの**電源再投入**
- `config.py` の `I2C_CAN_CH` が実際のバス番号と一致しているか確認

### `OSError: [Errno 5] Input/output error`

I2C レジスタ読み出しの失敗です。Zero 2 W では I2C タイミングの影響を受けやすい場合があります。

- `i2cdetect -y 1` で `0x25` が見えるか確認（見えれば配線は概ね正常）
- I2C 速度を 100 kHz に下げる（`/boot/firmware/config.txt` に `dtparam=i2c_arm_baudrate=100000`）
- 環境変数 `I2C_CAN_READ_SETTLE_SEC=0.05` でレジスタ読み出し前の待ち時間を延長
- デバッグ: `I2C_CAN_DEBUG=1 python lib/i2c_can_test.py`

### 初期化失敗時のメッセージ

`main.py` は I2C-CAN 初期化に失敗した場合、エラー内容と確認手順を表示し、CAN 機能を無効化したまま他の機能（LCD・エンコーダー）を継続します。

## プロジェクト構成

```
obd2_monitor/
├── main.py              # メインプログラム
├── config.py            # ピン定義・I2C/CAN 設定
├── switch.py            # ロータリーエンコーダー・スイッチ・LED
├── lib/
│   ├── i2c_can.py       # I2C-CAN ドライバ
│   ├── lcd1602.py       # LCD ドライバ
│   ├── i2c_scan.py      # I2C 診断
│   └── i2c_can_test.py  # CAN 受信テスト
├── lcd_test.py          # LCD 単体テスト
├── requirements.txt
└── Pico/                # Raspberry Pi Pico 向け（別ターゲット）
```

## ライセンス

`LICENSE` を参照してください。
