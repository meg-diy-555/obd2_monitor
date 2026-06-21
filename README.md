# obd2_monitor

Raspberry Pi 上で OBD2 / CAN 関連の入出力を扱うプロジェクトです。

## 実行

```bash
python main.py
```

## I2C 診断（CAN が i2cdetect に出ない場合）

```bash
python i2c_scan.py
# または
sudo i2cdetect -y 0
sudo i2cdetect -y 1
```

### Pi Zero 2 W + Seeed I2C-CAN (0x25) 配線

| Pi ピン | 信号 | モジュール |
|--------|------|-----------|
| 1 | 3.3V | VCC |
| 3 | SDA (GPIO2) | SDA |
| 5 | SCL (GPIO3) | SCL |
| 6 | GND | GND |

- I2C アドレス: **0x25**（[Seeed I2C-CAN Module](https://www.seeedstudio.com/I2C-CAN-Bus-Module-p-5054.html)）
- `config.py`: `I2C_CAN_CH = 1`（`/dev/i2c-1`）。LCD と同じ配線なら **同じ bus 番号**に揃える
- `I2C_CAN_FILTER_MODE`: `"none"`（USB-CAN テスト）/ `"obd"`（車両 OBD、ID 0x7E8 のみ）/ `"all"`（全 ID）

### CAN 受信テスト（Pi のみ）

```bash
python i2c_can_test.py
```

USB-CAN から 500kbps で送信。`filter=obd` のとき 0x7E8 以外は **ハードウェアで破棄**される。
- 全アドレス `--` の場合: 配線・電源・SDA/SCL 逆接続を確認。Pi とモジュール両方の **電源再投入**

### I2C 有効化

```bash
sudo raspi-config   # Interface Options -> I2C -> Enable
ls /dev/i2c-*
```
